import type { Blueprint } from "@/lib/types";

interface BlueprintEditorProps {
  blueprint: Blueprint;
  onChange: (blueprint: Blueprint) => void;
}

type ListField = "targetUsers" | "mvpScope" | "nonGoals" | "architecture" | "aiBoundary";

function listText(items: string[]): string {
  return items.join("\n");
}

function pairText(items: Array<{ operation: string; expected: string }>): string {
  return items.map((item) => `${item.operation} -> ${item.expected}`).join("\n");
}

function riskText(items: Array<{ risk: string; mitigation: string }>): string {
  return items.map((item) => `${item.risk} -> ${item.mitigation}`).join("\n");
}

function parseList(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parsePairs(value: string): Array<{ operation: string; expected: string }> {
  return value
    .split("\n")
    .map((line) => {
      const [operation = "", ...expectedParts] = line.split(/\s*(?:->|→)\s*/);
      return { operation: operation.trim(), expected: expectedParts.join(" -> ").trim() };
    })
    .filter((item) => item.operation || item.expected);
}

function parseRisks(value: string): Array<{ risk: string; mitigation: string }> {
  return value
    .split("\n")
    .map((line) => {
      const [risk = "", ...mitigationParts] = line.split(/\s*(?:->|→)\s*/);
      return { risk: risk.trim(), mitigation: mitigationParts.join(" -> ").trim() };
    })
    .filter((item) => item.risk || item.mitigation);
}

export function BlueprintEditor({ blueprint, onChange }: BlueprintEditorProps) {
  const setText = (field: "oneSentencePitch" | "problem" | "coreScenario", value: string) => {
    onChange({ ...blueprint, [field]: value });
  };

  const setList = (field: ListField, value: string) => {
    onChange({ ...blueprint, [field]: parseList(value) });
  };

  return (
    <div className="blueprint-editor">
      <section className="editor-section editor-section-accent">
        <p className="eyebrow">可编辑蓝图</p>
        <label>
          <span>一句话价值主张</span>
          <input
            value={blueprint.oneSentencePitch}
            onChange={(event) => setText("oneSentencePitch", event.target.value)}
          />
        </label>
      </section>

      <section className="editor-section two-columns">
        <label>
          <span>目标用户</span>
          <textarea
            value={listText(blueprint.targetUsers)}
            onChange={(event) => setList("targetUsers", event.target.value)}
            rows={4}
          />
          <small>每行一项</small>
        </label>
        <label>
          <span>核心使用场景</span>
          <textarea
            value={blueprint.coreScenario}
            onChange={(event) => setText("coreScenario", event.target.value)}
            rows={4}
          />
        </label>
      </section>

      <section className="editor-section">
        <label>
          <span>要解决的问题</span>
          <textarea
            value={blueprint.problem}
            onChange={(event) => setText("problem", event.target.value)}
            rows={4}
          />
        </label>
      </section>

      <section className="editor-section two-columns">
        <label>
          <span>MVP 范围</span>
          <textarea
            value={listText(blueprint.mvpScope)}
            onChange={(event) => setList("mvpScope", event.target.value)}
            rows={6}
          />
          <small>每行一项，建议控制在 3–5 项</small>
        </label>
        <label>
          <span>非目标</span>
          <textarea
            value={listText(blueprint.nonGoals)}
            onChange={(event) => setList("nonGoals", event.target.value)}
            rows={6}
          />
          <small>每行一项，写清这一版不做什么</small>
        </label>
      </section>

      <section className="editor-section">
        <label>
          <span>验收标准</span>
          <textarea
            value={pairText(blueprint.acceptanceCriteria)}
            onChange={(event) =>
              onChange({ ...blueprint, acceptanceCriteria: parsePairs(event.target.value) })
            }
            rows={6}
          />
          <small>每行格式：操作 -&gt; 可观察的预期输出</small>
        </label>
      </section>

      <section className="editor-section">
        <label>
          <span>风险与缓解</span>
          <textarea
            value={riskText(blueprint.risks)}
            onChange={(event) => onChange({ ...blueprint, risks: parseRisks(event.target.value) })}
            rows={5}
          />
          <small>每行格式：风险 -&gt; 缓解方式</small>
        </label>
      </section>

      <section className="editor-section two-columns">
        <label>
          <span>架构草案</span>
          <textarea
            value={listText(blueprint.architecture)}
            onChange={(event) => setList("architecture", event.target.value)}
            rows={5}
          />
          <small>每行一个模块或关键依赖</small>
        </label>
        <label>
          <span>AI 使用边界</span>
          <textarea
            value={listText(blueprint.aiBoundary)}
            onChange={(event) => setList("aiBoundary", event.target.value)}
            rows={5}
          />
          <small>明确人工确认、数据与自动执行边界</small>
        </label>
      </section>
    </div>
  );
}
