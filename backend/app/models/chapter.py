"""
챕터 모델 참조
Supabase 'chapters' 테이블 구조를 코드에서 참조하기 위한 정의입니다.

테이블 구조:
    - id: UUID DEFAULT gen_random_uuid() PK
    - book_id: UUID REFERENCES books(id) ON DELETE CASCADE
    - title: TEXT NOT NULL
    - content: TEXT DEFAULT ''
    - order: INTEGER NOT NULL DEFAULT 1
    - status: TEXT NOT NULL DEFAULT 'draft'
    - word_count: INTEGER DEFAULT 0
    - metadata: JSONB DEFAULT '{}'
    - created_at: TIMESTAMPTZ DEFAULT NOW()
    - updated_at: TIMESTAMPTZ DEFAULT NOW()

RLS 정책:
    - 도서 소유자만 챕터 CRUD 가능

SQL:
    CREATE TABLE chapters (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        book_id UUID REFERENCES books(id) ON DELETE CASCADE NOT NULL,
        title TEXT NOT NULL,
        content TEXT DEFAULT '',
        "order" INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'draft',
        word_count INTEGER DEFAULT 0,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "도서 소유자 챕터 CRUD" ON chapters
        FOR ALL USING (
            book_id IN (SELECT id FROM books WHERE user_id = auth.uid())
        );

    CREATE INDEX idx_chapters_book_id ON chapters(book_id);
    CREATE INDEX idx_chapters_order ON chapters(book_id, "order");
"""

from dataclasses import dataclass


@dataclass
class ChapterColumns:
    """chapters 테이블 컬럼 이름 상수"""
    ID: str = "id"
    BOOK_ID: str = "book_id"
    TITLE: str = "title"
    CONTENT: str = "content"
    ORDER: str = "order"
    STATUS: str = "status"
    WORD_COUNT: str = "word_count"
    METADATA: str = "metadata"
    CREATED_AT: str = "created_at"
    UPDATED_AT: str = "updated_at"


CHAPTER_COLUMNS = ChapterColumns()
