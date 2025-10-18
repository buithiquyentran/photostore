import createApiClient from "./api.service";
class ProjectsService {
  private api: any;

  constructor(baseUrl = "/api/v1/projects") {
    this.api = createApiClient(baseUrl);
  }
  async GetAll() {
    const res = await this.api.get("/");
    return res.data.data;
  }
  async Create(data: { name: string; description?: string | null }) {
    const res = await this.api.post("/", data);
    return res.data.data;
  }
  async Update(
    project_id: number,
    data: { name: string; description?: string | null }
  ) {
    const res = await this.api.patch(`/${project_id}`, data);
    return res.data.data;
  }
  async Delete(project_id: number) {
    const res = await this.api.delete(`/${project_id}`);
    return res.data.data;
  }
  async RegenerateApiKey(project_id: number) {
    const res = await this.api.patch(
      `/${project_id}/regenerate-api-key`
    );
    return res.data;
  }
}

export default new ProjectsService();
