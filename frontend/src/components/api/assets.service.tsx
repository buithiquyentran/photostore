import createApiClient from "./api.service";
import axios from "axios";
class AssetService {
  private api: any;

  constructor(baseUrl = "/api/v1/assets") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
  }
  async GetOne(asset_id: string) {
    return (await this.api.get(`/${asset_id}`)).data.data;
  }
}

export default new AssetService();
