import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "이용약관",
};

export default function TermsPage() {
  return (
    <article className="max-w-3xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-8">
        이용약관
      </h1>

      <div className="prose dark:prose-invert max-w-none space-y-8 text-gray-800 dark:text-gray-200">
        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제1조 (목적)
          </h2>
          <p>
            이 약관은 &quot;모두가 작가&quot; 서비스(이하 &quot;서비스&quot;)를
            이용함에 있어 서비스 제공자와 이용자 간의 권리, 의무 및 책임 사항을
            규정함을 목적으로 합니다.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제2조 (서비스 내용)
          </h2>
          <p>서비스는 다음과 같은 기능을 제공합니다:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>음성 인식(STT)을 통한 텍스트 입력</li>
            <li>AI 기반 글쓰기 지원 및 편집</li>
            <li>책 디자인(표지 및 내지 조판)</li>
            <li>전자책(EPUB) 및 인쇄용(PDF) 출판 지원</li>
            <li>음성 안내(TTS) 및 접근성 기능</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제3조 (AI 생성물의 저작권)
          </h2>
          <p>
            AI가 생성한 글의 저작권은 다음과 같이 처리됩니다:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              이용자가 음성 또는 텍스트로 제공한 원본 아이디어와 내용에 대한
              저작권은 이용자에게 있습니다.
            </li>
            <li>
              AI가 보조적으로 생성한 문장, 표현, 구조 제안 등은 이용자가 수정
              및 편집한 최종 결과물에 포함되어 이용자의 창작물로 간주됩니다.
            </li>
            <li>
              다만, AI 생성 비율이 높은 경우 일부 출판 플랫폼의 정책에 따라
              제한이 있을 수 있습니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제4조 (이용자의 의무)
          </h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>이용자는 타인의 저작물을 무단으로 입력하여서는 안 됩니다.</li>
            <li>
              서비스를 이용하여 불법적인 콘텐츠를 제작하여서는 안 됩니다.
            </li>
            <li>
              이용자는 자신의 계정 정보를 안전하게 관리할 책임이 있습니다.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제5조 (서비스 제한 및 중단)
          </h2>
          <p>
            서비스 제공자는 시스템 점검, 기술적 장애, 또는 불가피한 사유로
            서비스를 일시적으로 중단할 수 있으며, 이 경우 사전에 공지합니다.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
            제6조 (면책 조항)
          </h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              AI가 생성한 글의 정확성, 적절성에 대해 서비스 제공자는 보증하지
              않습니다.
            </li>
            <li>
              이용자가 출판한 콘텐츠로 인해 발생하는 법적 분쟁에 대해 서비스
              제공자는 책임을 지지 않습니다.
            </li>
          </ul>
        </section>

        <p className="text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
          시행일: 2026년 3월 1일
        </p>
      </div>
    </article>
  );
}
