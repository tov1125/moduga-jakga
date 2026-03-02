FROM python:3.12-slim

# 시스템 패키지 설치 (Typst, 한글 폰트 등)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Typst 설치 (PDF 생성용)
RUN curl -fsSL https://typst.community/typst-install/install.sh | sh \
    && mv /root/.local/bin/typst /usr/local/bin/typst || true

WORKDIR /app

# 의존성 먼저 복사하여 Docker 캐시 활용
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 앱 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
