import type { Blueprint, Project, ReviewReport } from "./types";

function bullets(items: string[]): string {
  return items.map((item) => `- ${item}`).join("\n");
}

function criteriaTable(blueprint: Blueprint): string {
  return [
    "| 操作 | 预期输出 |",
    "| --- | --- |",
    ...blueprint.acceptanceCriteria.map(
      (criterion) => `| ${criterion.operation} | ${criterion.expected} |`,
    ),
  ].join("\n");
}

function risksTable(blueprint: Blueprint): string {
  return [
    "| 风险 | 缓解方式 |",
    "| --- | --- |",
    ...blueprint.risks.map((risk) => `| ${risk.risk} | ${risk.mitigation} |`),
  ].join("\n");
}

function reviewSection(review?: ReviewReport): string {
  if (!review) {
    return "尚未执行审查。";
  }

  const findings = review.findings.length
    ? review.findings
        .map(
          (item) => `- [${item.severity}] ${item.area}：${item.message} 建议：${item.recommendation}`,
        )
        .join("\n")
    : "- 未发现阻塞问题。";

  return [`结论：${review.readiness}`, "", review.summary, "", findings].join("\n");
}

export function exportProjectMarkdown(project: Project): string {
  if (!project.blueprint) {
    throw new Error("请先生成并保存方案后再导出");
  }

  const blueprint = project.blueprint;
  return [
    `# ${blueprint.projectTitle}`,
    "",
    `> ${blueprint.oneSentencePitch}`,
    "",
    "## 原始想法",
    project.idea,
    "",
    "## 目标用户",
    bullets(blueprint.targetUsers),
    "",
    "## 要解决的问题",
    blueprint.problem,
    "",
    "## 最小使用场景",
    blueprint.coreScenario,
    "",
    "## MVP 范围",
    bullets(blueprint.mvpScope),
    "",
    "## 非目标",
    bullets(blueprint.nonGoals),
    "",
    "## 验收标准",
    criteriaTable(blueprint),
    "",
    "## 风险与缓解",
    risksTable(blueprint),
    "",
    "## 架构草案",
    bullets(blueprint.architecture),
    "",
    "## AI 使用边界",
    bullets(blueprint.aiBoundary),
    "",
    "## 审查结论",
    reviewSection(project.review),
    "",
    `导出时间：${new Date().toISOString()}`,
  ].join("\n");
}
