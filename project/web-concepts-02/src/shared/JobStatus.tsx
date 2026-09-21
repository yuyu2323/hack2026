import { Status, type Data } from "./core";
export function JobStatus({ job }: { job: Data }) {
  const pending = ["queued", "running"].includes(job.status);
  return (
    <section
      className={"job-status " + (job.status === "failed" ? "danger" : "")}
      aria-label="분석 진행 상태"
    >
      <div className="card-top">
        <Status value={job.status} />
        {job.elapsed_ms != null && (
          <small>{Math.round(job.elapsed_ms / 1000)}초 경과</small>
        )}
      </div>
      {pending && (
        <>
          <h2>
            {job.status === "queued"
              ? "분석 순서를 기다리고 있어요"
              : "사진을 분석하고 있어요"}
          </h2>
          <p>제출 사진과 적용 기준, Reference를 함께 확인하고 있어요.</p>
          {job.delayed && (
            <p className="notice" role="status">
              분석에 시간이 더 필요해요. 이 화면을 나가도 이력에서 확인할 수
              있어요.
            </p>
          )}
          <div className="progress-track" aria-hidden="true">
            <span />
          </div>
        </>
      )}
      {job.status === "failed" && (
        <>
          <h2>분석을 완료하지 못했어요</h2>
          <p>{job.error_message}</p>
          <p>
            플랫폼 운영자에게 복구를 요청해 주세요. 기존 사진으로 실패 작업을
            재처리할 수 있어요.
          </p>
          <small>오류 분류: {job.error_code}</small>
        </>
      )}
      {job.status === "succeeded" && (
        <p>점검을 마쳤어요. 아래 근거와 개선 행동을 확인해 주세요.</p>
      )}
    </section>
  );
}
