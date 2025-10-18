import createApiClient from "./api.service";
class ProjectsService {
  private api: any;

  constructor(baseUrl = "/api/v1/projects") {
    this.api = createApiClient(baseUrl);
  }
  async GetAll() {
    const res = await this.api.get("");
    return res.data.data;
  }
  async Create(data: {
    project_slug: string;
    folder_slug?: string | null;
    name: string;
  }) {
    const res = await this.api.post("/create", data);
    return res.data.data;
  }
}

export default new ProjectsService();
