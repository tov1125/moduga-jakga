"""
기본 Pydantic 스키마 모듈
모든 스키마가 상속하는 StrictBaseModel을 정의합니다.
필드 수준 StrictStr/StrictInt 등으로 타입 안전성을 보장합니다.
"""

from pydantic import BaseModel, ConfigDict


class StrictBaseModel(BaseModel):
    """
    타입 검증을 적용하는 기본 모델.
    필드 수준 Strict* 타입(StrictStr, StrictInt 등)으로 타입 안전성을 보장하고,
    from_attributes=True로 ORM/dict 데이터 변환을 지원합니다.
    """

    model_config = ConfigDict(from_attributes=True)
