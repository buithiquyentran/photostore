import {createApiClient} from "./api";

class AsssetService {
  private api: any;

  constructor(baseUrl = "/api/v1/assets") {
    this.api = createApiClient(baseUrl);
  }
  async GetAllAssets() {
    return (await this.api.get("/all_assets")).data;
  }
}

export default new AsssetService();
