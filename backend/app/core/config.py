"""
애플리케이션 설정 모듈
환경변수 기반 설정을 pydantic-settings로 관리합니다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Supabase 설정
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str

    # OpenAI 설정
    OPENAI_API_KEY: str

    # Google Gemini 설정 (표지 이미지 생성)
    GOOGLE_API_KEY: str = ""

    # CLOVA Speech (STT) 설정
    CLOVA_SPEECH_SECRET: str
    CLOVA_SPEECH_INVOKE_URL: str

    # CLOVA Voice (TTS) 설정
    CLOVA_VOICE_CLIENT_ID: str
    CLOVA_VOICE_CLIENT_SECRET: str

    # JWT 인증 설정
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24시간

    # CORS 설정
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS 허용 출처 목록을 리스트로 반환"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


def get_settings() -> Settings:
    """Settings 싱글톤 반환"""
    return Settings()  # type: ignore[call-arg]
