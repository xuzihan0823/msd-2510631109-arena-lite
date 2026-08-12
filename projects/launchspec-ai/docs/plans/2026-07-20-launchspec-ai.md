# LaunchSpec AI Implementation Plan

> **For Hermes:** Execute directly in small, tested steps. Do not claim a real-model run or a second-model audit until the user authorizes it and provides the required local/provider configuration.

**Goal:** Build a local-first web application where a small team turns one product idea into an editable, reviewable, exportable MVP proposal.

**Architecture:** A Next.js App Router application stores project records in an atomically written local JSON file. Route handlers expose CRUD, generation, review, export, and health endpoints. The domain layer is independent of HTTP and has a deterministic demo provider for tests plus an OpenAI-compatible provider adapter for a later authorized real-model run.

**Tech Stack:** TypeScript, Next.js 16, React 19, Tailwind CSS, Vitest, ESLint; Node file-system persistence for the course MVP.

**Current assumptions and boundaries:**
- Project root: `/Users/mac/code/msd-launchspec-ai`.
- The course-required `MSD_GROUP_ID` is unknown; formal submission filenames and Gate records remain honestly marked as pending until the user supplies it.
- No Ollama model is installed on this Mac. The application will work in clearly labelled demo mode and will include a real OpenAI-compatible provider adapter. A real model evidence run remains a human-authorized follow-up.
- Do not add authentication, billing, multi-user collaboration, or background queues in this MVP.

---

### Task 1: Bootstrap and guardrails

**Objective:** Create the Next.js app, developer tooling, project-local configuration examples, and no-secret defaults.

**Files:**
- Create: `package.json`, Next.js configuration, Tailwind configuration, `.gitignore`, `.env.example`
- Create: `src/app/layout.tsx`, `src/app/page.tsx`, `src/app/globals.css`
- Create: `vitest.config.ts`, `scripts/check.sh`

**Verification:** `npm run lint`, `npm run test`, and `npm run build` run without a credential or live-model dependency.

### Task 2: Define the project proposal domain

**Objective:** Create validated types and pure functions for a project, generated blueprint, reviewer report, and Markdown export.

**Files:**
- Create: `src/lib/types.ts`, `src/lib/validation.ts`, `src/lib/blueprint.ts`, `src/lib/review.ts`, `src/lib/export.ts`
- Test: `src/lib/*.test.ts`

**TDD steps:** Write failing tests for input validation, deterministic demo blueprint shape, rule review findings, and Markdown export; run tests red; implement only the required pure functions; run green.

### Task 3: Add persistence and API routes

**Objective:** Persist projects safely and expose a local API contract that the UI and UAT can exercise.

**Files:**
- Create: `src/lib/repository.ts`, `src/lib/ai-provider.ts`
- Create: `src/app/api/health/route.ts`
- Create: `src/app/api/projects/route.ts`
- Create: `src/app/api/projects/[id]/route.ts`
- Create: `src/app/api/projects/[id]/generate/route.ts`
- Create: `src/app/api/projects/[id]/review/route.ts`
- Create: `src/app/api/projects/[id]/export/route.ts`
- Test: route/domain behavior through domain-level tests and a local smoke script.

**Provider contract:** `AI_PROVIDER=demo` is the documented deterministic default. `AI_PROVIDER=openai-compatible` uses `AI_BASE_URL`, `AI_API_KEY`, and `AI_MODEL`, never records the key, and returns a clear configuration/upstream error rather than pretending generation succeeded.

### Task 4: Implement the user-facing workspace

**Objective:** Deliver a polished responsive UI for creating a proposal, generating/editing a blueprint, reviewing it, and exporting Markdown.

**Files:**
- Create: `src/components/launchspec-workspace.tsx`, `src/components/project-card.tsx`, `src/components/blueprint-editor.tsx`, `src/components/review-panel.tsx`
- Modify: `src/app/page.tsx`, `src/app/globals.css`

**Verification:** Run the local server and use curl to create, generate, review, edit, retrieve, and export one project. Use browser screenshots only after the user explicitly supplies/approves the capture context.

### Task 5: Create course process assets

**Objective:** Make the project independently reviewable and ready to receive the user’s group identity and authorized model evidence.

**Files:**
- Create: `README.md`
- Create: `docs/PRD.md`, `docs/SPEC.md`, `docs/DESIGN.md`, `docs/PROJECT-IDENTITY.md`
- Create: `docs/adr/ADR-001-local-json-persistence.md`, `docs/adr/ADR-002-model-provider-boundary.md`
- Create: `process/task_cards/launchspec-ai-project-cards.md`, `process/sprint/launchspec-ai-initial-log.md`, `PROCESS.md`
- Create: `evidence/README.md`, `process/uat/launchspec-ai-draft-uat.md`

**Verification:** Run the check script, placeholder scan, diff check, and secret scan. “Formal Gate 1”, “real AI capability evidence”, “independent reviewer identity”, and “final UAT signature” must remain pending rather than fabricated.

### Task 6: Final local validation

**Objective:** Verify the build, test suite, linting, and full demo-mode API path with real command output.

**Verification commands:**
- `npm run test`
- `npm run lint`
- `npm run build`
- `bash scripts/check.sh`
- launch `npm run dev`, then exercise `/api/health`, project creation, generation, review, update, and Markdown export.

**Exit criteria:** The application is locally runnable and testable, all completed evidence reflects real commands, and remaining human boundaries are explicitly listed.
