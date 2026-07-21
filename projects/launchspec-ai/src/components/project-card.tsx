import type { Project } from "@/lib/types";

interface ProjectCardProps {
  project: Project;
  selected: boolean;
  onSelect: () => void;
}

const stageLabel: Record<Project["stage"], string> = {
  draft: "想法",
  generated: "待审查",
  reviewed: "已审查",
};

export function ProjectCard({ project, selected, onSelect }: ProjectCardProps) {
  return (
    <button
      className={`project-card ${selected ? "project-card-selected" : ""}`}
      onClick={onSelect}
      type="button"
    >
      <span className="project-card-topline">
        <span className={`stage stage-${project.stage}`}>{stageLabel[project.stage]}</span>
        <time dateTime={project.updatedAt}>{new Date(project.updatedAt).toLocaleDateString("zh-CN")}</time>
      </span>
      <strong>{project.name}</strong>
      <span>{project.idea}</span>
    </button>
  );
}
