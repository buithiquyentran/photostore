import createApiClient from "./api.service";
class FolderService {
  private api: any;

  constructor(baseUrl = "/api/v1/folders") {
    this.api = createApiClient(baseUrl);
  }
  async GetFolderTree() {
    const res = await this.api.get("/folder_tree");
    return res.data.data;
  }
  async GetAll() {
    const res = await this.api.get("/all");
    return res.data;
  }
  async Create(data: {
    project_slug: string;
    folder_slug?: string | null;
    name: string;
  }) {
    const res = await this.api.post("/create", data);
    return res.data.data;
  }

  async GetContent(params: Record<string, any> = {}) {
    return (await this.api.get("/contents", { params })).data;
  }
}

export default new FolderService();
