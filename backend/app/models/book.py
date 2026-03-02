"""
도서 모델 참조
Supabase 'books' 테이블 구조를 코드에서 참조하기 위한 정의입니다.

테이블 구조:
    - id: UUID DEFAULT gen_random_uuid() PK
    - user_id: UUID REFERENCES profiles(id) ON DELETE CASCADE
    - title: TEXT NOT NULL
    - genre: TEXT NOT NULL DEFAULT 'essay'
    - description: TEXT DEFAULT ''
    - target_audience: TEXT DEFAULT ''
    - status: TEXT NOT NULL DEFAULT 'draft'
    - chapter_count: INTEGER DEFAULT 0
    - word_count: INTEGER DEFAULT 0
    - cover_image_url: TEXT
    - metadata: JSONB DEFAULT '{}'
    - created_at: TIMESTAMPTZ DEFAULT NOW()
    - updated_at: TIMESTAMPTZ DEFAULT NOW()

RLS 정책:
    - 사용자는 자신의 도서만 CRUD 가능

SQL:
    CREATE TABLE books (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
        title TEXT NOT NULL,
        genre TEXT NOT NULL DEFAULT 'essay',
        description TEXT DEFAULT '',
        target_audience TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'draft',
        chapter_count INTEGER DEFAULT 0,
        word_count INTEGER DEFAULT 0,
        cover_image_url TEXT,
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    ALTER TABLE books ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "사용자 본인 도서 CRUD" ON books
        FOR ALL USING (auth.uid() = user_id);

    CREATE INDEX idx_books_user_id ON books(user_id);
"""

from dataclasses import dataclass


@dataclass
class BookColumns:
    """books 테이블 컬럼 이름 상수"""
    ID: str = "id"
    USER_ID: str = "user_id"
    TITLE: str = "title"
    GENRE: str = "genre"
    DESCRIPTION: str = "description"
    TARGET_AUDIENCE: str = "target_audience"
    STATUS: str = "status"
    CHAPTER_COUNT: str = "chapter_count"
    WORD_COUNT: str = "word_count"
    COVER_IMAGE_URL: str = "cover_image_url"
    METADATA: str = "metadata"
    CREATED_AT: str = "created_at"
    UPDATED_AT: str = "updated_at"


BOOK_COLUMNS = BookColumns()
