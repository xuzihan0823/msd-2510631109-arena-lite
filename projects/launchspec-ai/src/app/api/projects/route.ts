import { errorResponse, readJsonBody } from "@/lib/api";
import { projectRepository } from "@/lib/repository";
import { validateNewProject } from "@/lib/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  try {
    return Response.json({ projects: await projectRepository.list() });
  } catch (error) {
    return errorResponse(error);
  }
}

export async function POST(request: Request) {
  try {
    const project = await projectRepository.create(validateNewProject(await readJsonBody(request)));
    return Response.json({ project }, { status: 201 });
  } catch (error) {
    return errorResponse(error);
  }
}
