"""
내보내기 모델 참조
Supabase 'exports' 테이블 구조를 코드에서 참조하기 위한 정의입니다.

테이블 구조:
    - id: UUID DEFAULT gen_random_uuid() PK
    - book_id: UUID REFERENCES books(id) ON DELETE CASCADE
    - user_id: UUID REFERENCES profiles(id) ON DELETE CASCADE
    - format: TEXT NOT NULL (docx, pdf, epub)
    - status: TEXT NOT NULL DEFAULT 'pending'
    - progress: FLOAT DEFAULT 0.0
    - file_path: TEXT
    - file_size_bytes: BIGINT
    - download_url: TEXT
    - error_message: TEXT
    - created_at: TIMESTAMPTZ DEFAULT NOW()
    - updated_at: TIMESTAMPTZ DEFAULT NOW()

RLS 정책:
    - 사용자는 자신의 내보내기만 조회/다운로드 가능

SQL:
    CREATE TABLE exports (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        book_id UUID REFERENCES books(id) ON DELETE CASCADE NOT NULL,
        user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
        format TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        progress FLOAT DEFAULT 0.0,
        file_path TEXT,
        file_size_bytes BIGINT,
        download_url TEXT,
        error_message TEXT,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    ALTER TABLE exports ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "사용자 본인 내보내기 조회" ON exports
        FOR SELECT USING (auth.uid() = user_id);

    CREATE INDEX idx_exports_book_id ON exports(book_id);
    CREATE INDEX idx_exports_user_id ON exports(user_id);
"""

from dataclasses import dataclass


@dataclass
class ExportColumns:
    """exports 테이블 컬럼 이름 상수"""
    ID: str = "id"
    BOOK_ID: str = "book_id"
    USER_ID: str = "user_id"
    FORMAT: str = "format"
    STATUS: str = "status"
    PROGRESS: str = "progress"
    FILE_PATH: str = "file_path"
    FILE_SIZE_BYTES: str = "file_size_bytes"
    DOWNLOAD_URL: str = "download_url"
    ERROR_MESSAGE: str = "error_message"
    CREATED_AT: str = "created_at"
    UPDATED_AT: str = "updated_at"


EXPORT_COLUMNS = ExportColumns()
