"""
기본 Pydantic 스키마 모듈
모든 스키마가 상속하는 StrictBaseModel을 정의합니다.
strict=True 설정으로 타입 안전성을 보장합니다.
"""

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    """
    엄격한 타입 검증을 적용하는 기본 모델.
    모든 프로젝트 스키마는 이 클래스를 상속해야 합니다.
    """

    model_config = ConfigDict(strict=True, from_attributes=True)
