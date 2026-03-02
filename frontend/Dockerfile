FROM node:20-slim

WORKDIR /app

# 의존성 먼저 복사하여 Docker 캐시 활용
COPY package.json package-lock.json* ./
RUN npm install

# 소스 코드 복사
COPY . .

# 포트 노출
EXPOSE 3000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# 앱 실행 (프로덕션 빌드 후 시작)
CMD ["npm", "run", "dev"]
