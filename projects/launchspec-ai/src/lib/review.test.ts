import { describe, expect, it } from "vitest";

import { reviewBlueprint } from "./review";
import type { Blueprint } from "./types";

const validBlueprint: Blueprint = {
  projectTitle: "LaunchSpec AI",
  oneSentencePitch: "把产品想法变成可审查的 MVP 方案。",
  targetUsers: ["创业团队负责人"],
  problem: "团队很难把模糊想法转换为一致的执行文档。",
  coreScenario: "输入想法后生成、审查、编辑并导出项目方案。",
  mvpScope: ["新建项目", "生成方案", "编辑方案", "导出 Markdown"],
  nonGoals: ["不自动生成完整业务代码"],
  acceptanceCriteria: [
    { operation: "输入有效想法并生成", expected: "返回包含 MVP 范围的方案" },
    { operation: "编辑后保存", expected: "刷新后可读取最新方案" },
  ],
  risks: [{ risk: "模型输出不稳定", mitigation: "人工编辑确认并使用测试 mock" }],
  architecture: ["Next.js 路由", "本地 JSON 数据文件"],
  aiBoundary: ["AI 输出仅为草案，用户必须人工确认后导出。"],
};

describe("reviewBlueprint", () => {
  it("accepts a bounded proposal with testable acceptance criteria", () => {
    const report = reviewBlueprint(validBlueprint);

    expect(report.readiness).toBe("ready");
    expect(report.findings).toHaveLength(0);
  });

  it("flags missing non-goals and insufficient acceptance criteria", () => {
    const report = reviewBlueprint({
      ...validBlueprint,
      nonGoals: [],
      acceptanceCriteria: [validBlueprint.acceptanceCriteria[0]],
    });

    expect(report.readiness).toBe("needs-revision");
    expect(report.findings.map((finding) => finding.area)).toEqual(
      expect.arrayContaining(["非目标", "验收标准"]),
    );
  });
});
