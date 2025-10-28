import createApiClient from "./api.service";
class TagService {
  private api: any;

  constructor(baseUrl = "/api/v1/tags") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
  }
  async Get() {
    return (await this.api.get("/user_tags")).data;
  }
  async Add(data: any) {
    return (await this.api.post("/asset/add", data)).data;
  }
  async Delete(asset_id: number, tag_id: number) {
    return (await this.api.delete(`/asset/${asset_id}/tag/${tag_id}`)).data;
  }
}

export default new TagService();
