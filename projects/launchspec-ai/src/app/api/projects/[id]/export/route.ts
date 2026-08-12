import { errorResponse } from "@/lib/api";
import { exportProjectMarkdown } from "@/lib/export";
import { projectRepository } from "@/lib/repository";
import type { IdRouteContext } from "@/lib/route-context";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function filenameFor(projectName: string): string {
  const safeName = projectName
    .trim()
    .replace(/[^a-zA-Z0-9\u4E00-\u9FFF_-]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${safeName || "launchspec-project"}.md`;
}

export async function GET(_request: Request, context: IdRouteContext) {
  try {
    const { id } = await context.params;
    const project = await projectRepository.get(id);
    if (!project) {
      return Response.json({ error: "未找到该项目。" }, { status: 404 });
    }

    const markdown = exportProjectMarkdown(project);
    return new Response(markdown, {
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Content-Disposition": `attachment; filename*=UTF-8''${encodeURIComponent(filenameFor(project.name))}`,
      },
    });
  } catch (error) {
    return errorResponse(error);
  }
}
