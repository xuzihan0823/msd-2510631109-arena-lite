import type { Blueprint, NewProjectInput } from "./types";

function shortIdea(idea: string): string {
  const firstSentence = idea.split(/[。！？!?]/)[0]?.trim();
  return firstSentence && firstSentence.length > 0 ? firstSentence : idea.trim();
}

export function createDemoBlueprint(input: NewProjectInput): Blueprint {
  const conciseIdea = shortIdea(input.idea);

  return {
    projectTitle: input.name,
    oneSentencePitch: `让团队把“${conciseIdea}”转化为可评审、可落地的 MVP 方案。`,
    targetUsers: ["有新产品想法的小型创业团队", "需要快速对齐范围的项目负责人"],
    problem:
      "团队常把产品想法停留在聊天记录或零散笔记中，难以形成明确范围、验收标准和风险共识。",
    coreScenario:
      "负责人输入产品想法，系统生成项目蓝图；团队编辑关键内容，审查范围与风险后导出 Markdown。",
    mvpScope: [
      "创建并保存一个项目想法",
      "生成结构化 PRD/MVP 蓝图草案",
      "在页面中编辑并保存蓝图字段",
      "生成审查清单并导出 Markdown",
    ],
    nonGoals: [
      "不自动生成完整业务代码或替代人类项目决策",
      "不提供多人实时协作、支付或外部项目管理系统同步",
    ],
    acceptanceCriteria: [
      {
        operation: "输入不少于 20 个字符的产品想法并点击生成",
        expected: "页面展示包含范围、非目标、验收标准和风险的结构化蓝图",
      },
      {
        operation: "编辑蓝图后点击保存并刷新页面",
        expected: "页面读取到修改后的内容",
      },
      {
        operation: "在生成蓝图后执行审查并导出",
        expected: "返回审查结论并下载包含 AI 边界的 Markdown 文件",
      },
    ],
    risks: [
      {
        risk: "模型可能生成空泛或超出四周交付范围的建议",
        mitigation: "用规则审查标记范围膨胀，要求用户在导出前人工编辑确认。",
      },
      {
        risk: "外部模型服务不可用或响应格式异常",
        mitigation: "保留明确错误信息；自动化测试使用确定性的 demo provider，不伪造真实模型结果。",
      },
    ],
    architecture: [
      "Next.js App Router：页面与本地 API 路由",
      "Node.js 文件系统：以原子写入方式保存本地 JSON 项目数据",
      "AI provider adapter：demo 模式与 OpenAI-compatible 模式共用结构化蓝图契约",
    ],
    aiBoundary: [
      "AI 输出仅为待审查草案，不代表真实市场、成本或法律结论。",
      "用户必须人工确认范围、风险和验收标准后才可作为项目计划使用。",
      "测试使用 demo provider；真实模型调用只记录脱敏的成功/失败状态，不保存 API Key。",
    ],
  };
}
