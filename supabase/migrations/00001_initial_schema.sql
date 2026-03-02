-- =============================================
-- 모두가 작가 - 초기 데이터베이스 스키마
-- Supabase (PostgreSQL) 마이그레이션
-- =============================================

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. profiles 테이블 (사용자 프로필)
-- auth.users와 1:1 관계
-- =============================================
CREATE TABLE IF NOT EXISTS profiles (
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

-- 회원가입 시 자동 프로필 생성 트리거
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, display_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data ->> 'display_name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- =============================================
-- 2. books 테이블 (도서)
-- =============================================
CREATE TABLE IF NOT EXISTS books (
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

CREATE POLICY "사용자 본인 도서 조회" ON books
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "사용자 본인 도서 생성" ON books
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "사용자 본인 도서 수정" ON books
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "사용자 본인 도서 삭제" ON books
    FOR DELETE USING (auth.uid() = user_id);

CREATE INDEX idx_books_user_id ON books(user_id);

-- =============================================
-- 3. chapters 테이블 (챕터)
-- =============================================
CREATE TABLE IF NOT EXISTS chapters (
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

-- =============================================
-- 4. exports 테이블 (내보내기 이력)
-- =============================================
CREATE TABLE IF NOT EXISTS exports (
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

CREATE POLICY "사용자 본인 내보내기 생성" ON exports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE INDEX idx_exports_book_id ON exports(book_id);
CREATE INDEX idx_exports_user_id ON exports(user_id);

-- =============================================
-- 5. writing_sessions 테이블 (글쓰기 세션)
-- 음성 대화 → 글 변환 세션 추적
-- =============================================
CREATE TABLE IF NOT EXISTS writing_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE NOT NULL,
    chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    transcript TEXT DEFAULT '',
    generated_text TEXT DEFAULT '',
    duration_seconds INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE writing_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "사용자 본인 세션 CRUD" ON writing_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE INDEX idx_writing_sessions_book_id ON writing_sessions(book_id);
CREATE INDEX idx_writing_sessions_user_id ON writing_sessions(user_id);

-- =============================================
-- 6. editing_reports 테이블 (편집/교열 리포트)
-- =============================================
CREATE TABLE IF NOT EXISTS editing_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE NOT NULL,
    chapter_id UUID REFERENCES chapters(id) ON DELETE SET NULL,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
    stage TEXT NOT NULL DEFAULT 'spelling',
    spelling_score FLOAT DEFAULT 0.0,
    style_score FLOAT DEFAULT 0.0,
    structure_score FLOAT DEFAULT 0.0,
    readability_score FLOAT DEFAULT 0.0,
    overall_score FLOAT DEFAULT 0.0,
    issues JSONB DEFAULT '[]',
    suggestions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE editing_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "사용자 본인 리포트 조회" ON editing_reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "사용자 본인 리포트 생성" ON editing_reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE INDEX idx_editing_reports_book_id ON editing_reports(book_id);

-- =============================================
-- updated_at 자동 갱신 트리거
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_books_updated_at
    BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapters_updated_at
    BEFORE UPDATE ON chapters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exports_updated_at
    BEFORE UPDATE ON exports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_writing_sessions_updated_at
    BEFORE UPDATE ON writing_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
