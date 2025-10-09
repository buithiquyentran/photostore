import createApiClient from "./api.service";
class FolderService {
  private api: any;

  constructor(baseUrl = "/api/v1/folders") {
    this.api = createApiClient(baseUrl);
  }
  async GetAll() {
    const res = await this.api.get("/all");
    return res.data.data;
  }
  async GetContent(params: Record<string, any> = {}) {
    return (await this.api.get("/contents", { params })).data;
  }
}

export default new FolderService();
