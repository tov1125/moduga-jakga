"""
사용자/프로필 모델 참조
Supabase 'profiles' 테이블 구조를 코드에서 참조하기 위한 정의입니다.

테이블 구조:
    - id: UUID (auth.users.id와 연결, PK)
    - email: TEXT NOT NULL UNIQUE
    - display_name: TEXT NOT NULL
    - disability_type: TEXT NOT NULL DEFAULT 'none'
    - is_active: BOOLEAN DEFAULT TRUE
    - preferences: JSONB DEFAULT '{}'
    - created_at: TIMESTAMPTZ DEFAULT NOW()
    - updated_at: TIMESTAMPTZ DEFAULT NOW()

RLS 정책:
    - 사용자는 자신의 프로필만 읽기/수정 가능
    - 서비스 키로만 프로필 생성 가능

SQL:
    CREATE TABLE profiles (
        id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        display_name TEXT NOT NULL,
        disability_type TEXT NOT NULL DEFAULT 'none',
        is_active BOOLEAN DEFAULT TRUE,
        preferences JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

    CREATE POLICY "사용자 본인 프로필 조회" ON profiles
        FOR SELECT USING (auth.uid() = id);

    CREATE POLICY "사용자 본인 프로필 수정" ON profiles
        FOR UPDATE USING (auth.uid() = id);
"""

from dataclasses import dataclass


@dataclass
class ProfileColumns:
    """profiles 테이블 컬럼 이름 상수"""
    ID: str = "id"
    EMAIL: str = "email"
    DISPLAY_NAME: str = "display_name"
    DISABILITY_TYPE: str = "disability_type"
    IS_ACTIVE: str = "is_active"
    PREFERENCES: str = "preferences"
    CREATED_AT: str = "created_at"
    UPDATED_AT: str = "updated_at"


PROFILE_COLUMNS = ProfileColumns()
