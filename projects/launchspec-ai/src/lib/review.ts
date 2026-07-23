import type { Blueprint, ReviewFinding, ReviewReport } from "./types";

function finding(
  id: string,
  severity: ReviewFinding["severity"],
  area: string,
  message: string,
  recommendation: string,
): ReviewFinding {
  return { id, severity, area, message, recommendation };
}

export function reviewBlueprint(blueprint: Blueprint): ReviewReport {
  const findings: ReviewFinding[] = [];

  if (blueprint.nonGoals.length === 0) {
    findings.push(
      finding(
        "missing-non-goals",
        "blocking",
        "非目标",
        "方案没有明确说明本期不做什么，范围无法被稳定控制。",
        "至少列出一条本期明确排除的功能或集成。",
      ),
    );
  }

  if (blueprint.acceptanceCriteria.length < 2) {
    findings.push(
      finding(
        "insufficient-criteria",
        "blocking",
        "验收标准",
        "少于两条可验证的验收标准，无法支持后续测试与 UAT。",
        "补充至少两条“操作 → 预期输出”标准。",
      ),
    );
  }

  if (blueprint.mvpScope.length > 5) {
    findings.push(
      finding(
        "scope-too-wide",
        "warning",
        "MVP 范围",
        `当前列出了 ${blueprint.mvpScope.length} 项 MVP 能力，四周内存在范围膨胀风险。`,
        "优先保留一条从输入到可验证输出的纵切面，其余能力转入后续计划。",
      ),
    );
  }

  if (!blueprint.aiBoundary.some((item) => item.includes("人工"))) {
    findings.push(
      finding(
        "missing-human-review",
        "warning",
        "AI 边界",
        "没有写明 AI 输出需要人工确认，容易把生成草案误当作事实或最终决策。",
        "补充人工审查、编辑确认和不自动执行的边界。",
      ),
    );
  }

  if (blueprint.risks.length === 0) {
    findings.push(
      finding(
        "missing-risk",
        "warning",
        "风险",
        "没有记录模型或交付风险。",
        "至少补充一条模型不稳定、隐私、成本或范围风险及缓解方式。",
      ),
    );
  }

  const blockingCount = findings.filter((item) => item.severity === "blocking").length;
  const readiness = blockingCount === 0 ? "ready" : "needs-revision";

  return {
    readiness,
    summary:
      readiness === "ready"
        ? "方案已具备进入设计阶段的最小信息；请结合审查建议人工确认后继续。"
        : `发现 ${blockingCount} 个必须修正的问题；请完成修正后重新审查。`,
    findings,
    reviewedAt: new Date().toISOString(),
    source: "demo-rules",
  };
}
