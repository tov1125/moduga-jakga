"""
Supabase CRUD 서비스 모듈
Supabase 테이블에 대한 범용 CRUD 연산과 도메인별 쿼리를 제공합니다.
"""

from typing import Any

from supabase import Client

from app.models.base import TABLE_BOOKS, TABLE_CHAPTERS, TABLE_EXPORTS


class SupabaseService:
    """Supabase 기반 CRUD 서비스"""

    def __init__(self, supabase: Client) -> None:
        self._client = supabase

    # ──────────────────────────────────────────────
    # 범용 CRUD
    # ──────────────────────────────────────────────

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """테이블에 레코드를 삽입합니다."""
        response = self._client.table(table).insert(data).execute()
        if not response.data:
            raise ValueError(f"'{table}' 테이블 삽입 실패")
        result: dict[str, Any] = response.data[0]
        return result

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
        order_by: str | None = None,
        descending: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """테이블에서 레코드를 조회합니다."""
        query = self._client.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if order_by:
            query = query.order(order_by, desc=descending)

        if limit:
            query = query.limit(limit)

        response = query.execute()
        result: list[dict[str, Any]] = response.data
        return result

    async def select_one(
        self,
        table: str,
        columns: str = "*",
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """테이블에서 단일 레코드를 조회합니다."""
        results = await self.select(table, columns, filters, limit=1)
        return results[0] if results else None

    async def update(
        self,
        table: str,
        data: dict[str, Any],
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """테이블의 레코드를 업데이트합니다."""
        query = self._client.table(table).update(data)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        if not response.data:
            raise ValueError(f"'{table}' 테이블 업데이트 실패")
        result: dict[str, Any] = response.data[0]
        return result

    async def delete(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
    ) -> None:
        """테이블에서 레코드를 삭제합니다."""
        query = self._client.table(table).delete()

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        query.execute()

    async def count(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
    ) -> int:
        """테이블의 레코드 수를 반환합니다."""
        query = self._client.table(table).select("id", count="exact")

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.count or 0

    # ──────────────────────────────────────────────
    # 도서 관련 쿼리
    # ──────────────────────────────────────────────

    async def get_user_books(
        self,
        user_id: str,
        status_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """사용자의 도서 목록을 조회합니다."""
        filters: dict[str, Any] = {"user_id": user_id}
        if status_filter:
            filters["status"] = status_filter

        return await self.select(
            TABLE_BOOKS,
            filters=filters,
            order_by="created_at",
            descending=True,
        )

    async def get_book_with_chapters(
        self,
        book_id: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        """도서와 챕터를 함께 조회합니다."""
        book = await self.select_one(
            TABLE_BOOKS,
            filters={"id": book_id, "user_id": user_id},
        )

        if not book:
            return None

        chapters = await self.select(
            TABLE_CHAPTERS,
            filters={"book_id": book_id},
            order_by="order",
            descending=False,
        )

        book["chapters"] = chapters
        return book

    async def update_book_stats(self, book_id: str) -> None:
        """도서의 챕터 수와 글자 수를 재계산하여 업데이트합니다."""
        chapters = await self.select(
            TABLE_CHAPTERS,
            columns="word_count",
            filters={"book_id": book_id},
        )

        chapter_count = len(chapters)
        word_count = sum(ch.get("word_count", 0) for ch in chapters)

        await self.update(
            TABLE_BOOKS,
            data={"chapter_count": chapter_count, "word_count": word_count},
            filters={"id": book_id},
        )

    # ──────────────────────────────────────────────
    # 챕터 관련 쿼리
    # ──────────────────────────────────────────────

    async def get_book_chapters(
        self,
        book_id: str,
    ) -> list[dict[str, Any]]:
        """도서의 챕터 목록을 순서대로 조회합니다."""
        return await self.select(
            TABLE_CHAPTERS,
            filters={"book_id": book_id},
            order_by="order",
            descending=False,
        )

    async def get_next_chapter_order(self, book_id: str) -> int:
        """도서의 다음 챕터 순서 번호를 반환합니다."""
        chapters = await self.select(
            TABLE_CHAPTERS,
            columns="order",
            filters={"book_id": book_id},
            order_by="order",
            descending=True,
            limit=1,
        )
        if chapters:
            return chapters[0]["order"] + 1
        return 1

    # ──────────────────────────────────────────────
    # 내보내기 관련 쿼리
    # ──────────────────────────────────────────────

    async def get_user_exports(
        self,
        user_id: str,
        book_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """사용자의 내보내기 목록을 조회합니다."""
        filters: dict[str, Any] = {"user_id": user_id}
        if book_id:
            filters["book_id"] = book_id

        return await self.select(
            TABLE_EXPORTS,
            filters=filters,
            order_by="created_at",
            descending=True,
        )

    async def update_export_status(
        self,
        export_id: str,
        status: str,
        progress: float = 0.0,
        file_path: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """내보내기 상태를 업데이트합니다."""
        data: dict[str, Any] = {
            "status": status,
            "progress": progress,
        }
        if file_path:
            data["file_path"] = file_path
        if error_message:
            data["error_message"] = error_message

        await self.update(TABLE_EXPORTS, data=data, filters={"id": export_id})
