export type ProjectStage = "draft" | "generated" | "reviewed";

export type FindingSeverity = "blocking" | "warning" | "info";

export interface AcceptanceCriterion {
  operation: string;
  expected: string;
}

export interface Risk {
  risk: string;
  mitigation: string;
}

export interface Blueprint {
  projectTitle: string;
  oneSentencePitch: string;
  targetUsers: string[];
  problem: string;
  coreScenario: string;
  mvpScope: string[];
  nonGoals: string[];
  acceptanceCriteria: AcceptanceCriterion[];
  risks: Risk[];
  architecture: string[];
  aiBoundary: string[];
}

export interface ReviewFinding {
  id: string;
  severity: FindingSeverity;
  area: string;
  message: string;
  recommendation: string;
}

export interface ReviewReport {
  readiness: "ready" | "needs-revision";
  summary: string;
  findings: ReviewFinding[];
  reviewedAt: string;
  source: "demo-rules" | "model";
}

export interface Project {
  id: string;
  name: string;
  idea: string;
  stage: ProjectStage;
  blueprint?: Blueprint;
  review?: ReviewReport;
  createdAt: string;
  updatedAt: string;
}

export interface NewProjectInput {
  name: string;
  idea: string;
}

export interface ProjectStore {
  projects: Project[];
}
