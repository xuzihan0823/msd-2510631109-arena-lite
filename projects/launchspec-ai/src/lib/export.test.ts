import { describe, expect, it } from "vitest";

import { exportProjectMarkdown } from "./export";
import type { Project } from "./types";

const project: Project = {
  id: "project-1",
  name: "LaunchSpec AI",
  idea: "帮助小型团队把想法整理为可评审的项目方案。",
  createdAt: "2026-07-20T00:00:00.000Z",
  updatedAt: "2026-07-20T00:00:00.000Z",
  blueprint: {
    projectTitle: "LaunchSpec AI",
    oneSentencePitch: "把产品想法变成可审查的 MVP 方案。",
    targetUsers: ["创业团队负责人"],
    problem: "团队很难把模糊想法转换为一致的执行文档。",
    coreScenario: "输入想法后生成、审查、编辑并导出项目方案。",
    mvpScope: ["新建项目"],
    nonGoals: ["不自动生成完整业务代码"],
    acceptanceCriteria: [
      { operation: "输入有效想法并生成", expected: "返回方案" },
      { operation: "编辑后保存", expected: "刷新后仍存在" },
    ],
    risks: [{ risk: "模型输出不稳定", mitigation: "人工确认" }],
    architecture: ["Next.js"],
    aiBoundary: ["AI 输出仅为草案，用户必须人工确认。"],
  },
};

describe("exportProjectMarkdown", () => {
  it("exports the proposal and its AI boundary as Markdown", () => {
    const markdown = exportProjectMarkdown(project);

    expect(markdown).toContain("# LaunchSpec AI");
    expect(markdown).toContain("## 验收标准");
    expect(markdown).toContain("人工确认");
  });
});
