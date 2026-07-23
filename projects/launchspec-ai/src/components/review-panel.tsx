import type { ReviewReport } from "@/lib/types";

interface ReviewPanelProps {
  review?: ReviewReport;
}

const sourceLabel: Record<ReviewReport["source"], string> = {
  "demo-rules": "规则检查（非模型审计）",
  model: "模型审查",
};

export function ReviewPanel({ review }: ReviewPanelProps) {
  if (!review) {
    return (
      <section className="review-panel review-empty">
        <p className="eyebrow">审查状态</p>
        <h2>还没有审查结论</h2>
        <p>保存方案后执行审查，系统会检查范围、非目标、验收标准、风险与 AI 人工确认边界。</p>
      </section>
    );
  }

  return (
    <section className="review-panel">
      <div className="review-heading">
        <div>
          <p className="eyebrow">审查状态</p>
          <h2>{review.readiness === "ready" ? "可以进入设计" : "需要修订"}</h2>
        </div>
        <span className={`review-badge review-${review.readiness}`}>
          {review.readiness === "ready" ? "READY" : "REVISION"}
        </span>
      </div>
      <p className="review-summary">{review.summary}</p>
      <p className="review-source">来源：{sourceLabel[review.source]}</p>
      {review.findings.length > 0 ? (
        <ul className="findings-list">
          {review.findings.map((finding) => (
            <li key={finding.id} className={`finding finding-${finding.severity}`}>
              <span>{finding.severity}</span>
              <div>
                <strong>{finding.area}</strong>
                <p>{finding.message}</p>
                <small>建议：{finding.recommendation}</small>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="review-clear">没有发现阻塞问题，但仍需由项目成员人工确认。</p>
      )}
    </section>
  );
}
