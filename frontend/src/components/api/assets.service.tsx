import createApiClient from "./api.service";
class AssetService {
  private api: any;

  constructor(baseUrl = "/api/v1/assets") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
  }
    async GetOne(name: string | undefined) {
    return this.api.get(`/${name}`, {
      responseType: "blob",
    });
  }
}

export default new AssetService();
