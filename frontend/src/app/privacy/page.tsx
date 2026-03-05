import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "개인정보처리방침",
};

export default function PrivacyPage() {
  return (
    <article className="max-w-3xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
        개인정보처리방침
      </h1>

      <div className="prose dark:prose-invert max-w-none space-y-8 text-gray-800 dark:text-gray-200">
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제1조 (수집하는 개인정보)
          </h2>
          <p>서비스는 다음과 같은 개인정보를 수집합니다:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>필수 정보:</strong> 이메일 주소, 이름(필명), 비밀번호
            </li>
            <li>
              <strong>선택 정보:</strong> 시각 장애 유형 (서비스 최적화 목적)
            </li>
            <li>
              <strong>자동 수집:</strong> 서비스 이용 기록, 접속 로그
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제2조 (음성 데이터 처리)
          </h2>
          <p>
            음성 인식(STT) 기능 이용 시 음성 데이터는 다음과 같이 처리됩니다:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              음성 데이터는 텍스트 변환 목적으로만 사용되며, 변환 완료 후 즉시
              삭제됩니다.
            </li>
            <li>음성 데이터는 서버에 영구 저장되지 않습니다.</li>
            <li>
              STT 서비스 제공업체(CLOVA Speech)의 개인정보처리방침이 추가로
              적용될 수 있습니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제3조 (장애 정보의 처리)
          </h2>
          <p>
            시각 장애 유형 정보는 「개인정보보호법」상 민감정보에 해당하며,
            다음과 같이 처리됩니다:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>이용자의 별도 동의를 받아 수집합니다.</li>
            <li>서비스 접근성 최적화 목적으로만 사용됩니다.</li>
            <li>암호화하여 저장하며, 동의 철회 시 즉시 삭제합니다.</li>
            <li>제3자에게 제공하지 않습니다.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제4조 (개인정보의 보유 및 이용 기간)
          </h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              회원 탈퇴 시 개인정보는 지체 없이 파기합니다.
            </li>
            <li>
              관련 법령에 의해 보존이 필요한 경우, 해당 법령에서 정한 기간 동안
              보관합니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제5조 (이용자의 권리)
          </h2>
          <p>이용자는 언제든지 다음 권리를 행사할 수 있습니다:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>개인정보 열람, 수정, 삭제 요청</li>
            <li>개인정보 수집 및 이용 동의 철회</li>
            <li>장애 정보 수집 동의 철회</li>
          </ul>
          <p>
            설정 페이지에서 직접 변경하거나, 서비스 제공자에게 요청할 수
            있습니다.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제6조 (개인정보의 안전성 확보 조치)
          </h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>비밀번호의 암호화 저장</li>
            <li>SSL/TLS를 통한 데이터 전송 암호화</li>
            <li>접근 권한 관리 및 접근 통제</li>
            <li>Row Level Security(RLS) 기반 데이터 접근 제어</li>
          </ul>
        </section>

        <p className="text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
          시행일: 2026년 3월 1일
        </p>
      </div>
    </article>
  );
}
