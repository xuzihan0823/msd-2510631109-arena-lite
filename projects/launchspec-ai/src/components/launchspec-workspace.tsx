"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { BlueprintEditor } from "@/components/blueprint-editor";
import { ProjectCard } from "@/components/project-card";
import { ReviewPanel } from "@/components/review-panel";
import type { Blueprint, Project } from "@/lib/types";

type Action = "create" | "generate" | "save" | "review" | null;
type Notice = { tone: "success" | "error" | "info"; message: string } | null;

interface ProjectsResponse {
  projects: Project[];
}

interface ProjectResponse {
  project: Project;
  provider?: string;
  reviewer?: string;
}

interface HealthResponse {
  status: string;
  provider: { mode: string; ready: boolean };
}

const initialForm = { name: "", idea: "" };

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
    cache: "no-store",
  });
  const payload: unknown = await response.json();

  if (!response.ok) {
    const message =
      typeof payload === "object" && payload !== null && "error" in payload
        ? (payload as { error?: unknown }).error
        : undefined;
    throw new Error(typeof message === "string" ? message : "请求失败，请稍后重试。");
  }

  return payload as T;
}

function replaceProject(projects: Project[], updated: Project): Project[] {
  return projects.map((project) => (project.id === updated.id ? updated : project));
}

export function LaunchSpecWorkspace() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [form, setForm] = useState(initialForm);
  const [action, setAction] = useState<Action>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedId) ?? null,
    [projects, selectedId],
  );

  useEffect(() => {
    void Promise.all([
      requestJson<ProjectsResponse>("/api/projects"),
      requestJson<HealthResponse>("/api/health"),
    ])
      .then(([projectData, healthData]) => {
        setProjects(projectData.projects);
        setSelectedId((current) => current ?? projectData.projects[0]?.id ?? null);
        setHealth(healthData);
      })
      .catch((error: unknown) => {
        setNotice({
          tone: "error",
          message: error instanceof Error ? error.message : "无法读取本地项目数据。",
        });
      });
  }, []);

  const runAction = async (nextAction: Exclude<Action, null>, work: () => Promise<void>) => {
    setAction(nextAction);
    setNotice(null);
    try {
      await work();
    } catch (error) {
      setNotice({
        tone: "error",
        message: error instanceof Error ? error.message : "操作未完成，请稍后重试。",
      });
    } finally {
      setAction(null);
    }
  };

  const createProject = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    void runAction("create", async () => {
      const result = await requestJson<ProjectResponse>("/api/projects", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setProjects((current) => [result.project, ...current]);
      setSelectedId(result.project.id);
      setForm(initialForm);
      setNotice({ tone: "success", message: "已保存项目想法，现在可以生成第一版方案。" });
    });
  };

  const generate = () => {
    if (!selectedProject) return;
    void runAction("generate", async () => {
      const result = await requestJson<ProjectResponse>(
        `/api/projects/${selectedProject.id}/generate`,
        { method: "POST" },
      );
      setProjects((current) => replaceProject(current, result.project));
      setNotice({
        tone: "success",
        message:
          result.provider === "demo"
            ? "已生成可编辑的 demo 草案。接入真实模型后请重新生成并保留脱敏运行证据。"
            : "已使用配置的模型生成方案草案，请人工逐项复核。",
      });
    });
  };

  const saveBlueprint = () => {
    if (!selectedProject?.blueprint) return;
    void runAction("save", async () => {
      const result = await requestJson<ProjectResponse>(`/api/projects/${selectedProject.id}`, {
        method: "PUT",
        body: JSON.stringify({ blueprint: selectedProject.blueprint }),
      });
      setProjects((current) => replaceProject(current, result.project));
      setNotice({ tone: "success", message: "方案已保存。保存后需要重新执行审查。" });
    });
  };

  const review = () => {
    if (!selectedProject) return;
    void runAction("review", async () => {
      const result = await requestJson<ProjectResponse>(
        `/api/projects/${selectedProject.id}/review`,
        { method: "POST" },
      );
      setProjects((current) => replaceProject(current, result.project));
      setNotice({
        tone: "success",
        message:
          result.reviewer === "model"
            ? "模型审查已完成，请人工确认每条建议。"
            : "规则检查已完成；这不是独立模型审计。",
      });
    });
  };

  const updateBlueprint = (blueprint: Blueprint) => {
    if (!selectedProject) return;
    setProjects((current) =>
      current.map((project) =>
        project.id === selectedProject.id ? { ...project, blueprint, review: undefined } : project,
      ),
    );
  };

  const download = () => {
    if (!selectedProject?.blueprint) return;
    window.location.assign(`/api/projects/${selectedProject.id}/export`);
  };

  const busy = action !== null;

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#workspace" aria-label="LaunchSpec AI 首页">
          <span className="brand-mark">L</span>
          <span>LaunchSpec <em>AI</em></span>
        </a>
        <div className="topbar-status">
          <span className={`connection ${health?.provider.ready ? "connection-ready" : ""}`} />
          {health ? `${health.provider.mode} · ${health.provider.ready ? "可用" : "待配置"}` : "正在检查本地服务"}
        </div>
      </header>

      <section className="hero" id="workspace">
        <div>
          <p className="eyebrow">PRODUCT CLARITY WORKSPACE</p>
          <h1>把一个模糊想法，<br /><i>变成可执行的共识。</i></h1>
          <p className="hero-copy">
            生成结构化 MVP 蓝图，明确范围、风险和验收标准；再用审查与人工编辑把方案变成真正可用的起点。
          </p>
        </div>
        <aside className="hero-note">
          <span>当前模式</span>
          <strong>
            {health?.provider.ready && health.provider.mode !== "demo"
              ? "真实模型已配置"
              : "确定性 Demo"}
          </strong>
          <p>Demo 用于演示和测试；提交期必须另外保留一次真实 AI 能力运行的脱敏证据。</p>
        </aside>
      </section>

      <section className="workspace-grid">
        <aside className="sidebar">
          <div className="sidebar-heading">
            <div>
              <p className="eyebrow">PROJECTS</p>
              <h2>方案库</h2>
            </div>
            <span>{projects.length}</span>
          </div>

          <div className="project-list">
            {projects.length > 0 ? (
              projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  selected={project.id === selectedId}
                  onSelect={() => setSelectedId(project.id)}
                />
              ))
            ) : (
              <p className="empty-list">还没有方案。从右侧创建第一个项目想法。</p>
            )}
          </div>
        </aside>

        <section className="workspace-main">
          {notice ? <p className={`notice notice-${notice.tone}`} role="status">{notice.message}</p> : null}

          {!selectedProject ? (
            <section className="create-panel">
              <div>
                <p className="eyebrow">START HERE</p>
                <h2>先描述你想解决的问题</h2>
                <p>不要写“做一个 AI 平台”。写清谁在什么情境下遇到了什么问题，以及期待什么可观察结果。</p>
              </div>
              <form onSubmit={createProject}>
                <label>
                  <span>项目名称</span>
                  <input
                    minLength={2}
                    maxLength={120}
                    required
                    placeholder="例如：LaunchSpec AI"
                    value={form.name}
                    onChange={(event) => setForm({ ...form, name: event.target.value })}
                  />
                </label>
                <label>
                  <span>产品想法</span>
                  <textarea
                    minLength={20}
                    maxLength={4000}
                    required
                    rows={8}
                    placeholder="例如：帮助小型创业团队把零散产品想法整理为可评审、可导出的 MVP 项目方案。"
                    value={form.idea}
                    onChange={(event) => setForm({ ...form, idea: event.target.value })}
                  />
                </label>
                <button className="button button-primary" disabled={busy} type="submit">
                  {action === "create" ? "正在保存…" : "创建项目想法"}
                </button>
              </form>
            </section>
          ) : (
            <>
              <section className="project-header">
                <div>
                  <p className="eyebrow">ACTIVE PROJECT</p>
                  <h2>{selectedProject.name}</h2>
                  <p>{selectedProject.idea}</p>
                </div>
                <div className="action-group">
                  <button className="button button-secondary" disabled={busy} onClick={generate} type="button">
                    {action === "generate" ? "生成中…" : selectedProject.blueprint ? "重新生成" : "生成蓝图"}
                  </button>
                  <button
                    className="button button-quiet"
                    disabled={busy || !selectedProject.blueprint}
                    onClick={saveBlueprint}
                    type="button"
                  >
                    {action === "save" ? "保存中…" : "保存编辑"}
                  </button>
                  <button
                    className="button button-quiet"
                    disabled={busy || !selectedProject.blueprint}
                    onClick={review}
                    type="button"
                  >
                    {action === "review" ? "审查中…" : "执行审查"}
                  </button>
                  <button
                    className="button button-quiet"
                    disabled={!selectedProject.blueprint}
                    onClick={download}
                    type="button"
                  >
                    导出 .md
                  </button>
                </div>
              </section>

              {selectedProject.blueprint ? (
                <div className="proposal-layout">
                  <BlueprintEditor blueprint={selectedProject.blueprint} onChange={updateBlueprint} />
                  <ReviewPanel review={selectedProject.review} />
                </div>
              ) : (
                <section className="generate-empty">
                  <span className="spark">✦</span>
                  <p className="eyebrow">FIRST BLUEPRINT</p>
                  <h2>还没有可审查的蓝图</h2>
                  <p>先生成草案，再删掉不必要的功能、补齐验收标准，并由团队成员人工确认。</p>
                  <button className="button button-primary" disabled={busy} onClick={generate} type="button">
                    {action === "generate" ? "正在生成…" : "生成第一版方案"}
                  </button>
                </section>
              )}
            </>
          )}
        </section>
      </section>

      <footer>
        <span>LaunchSpec AI · 本地优先的项目方案工作台</span>
        <span>AI 给草案，人做决策。</span>
      </footer>
    </main>
  );
}
