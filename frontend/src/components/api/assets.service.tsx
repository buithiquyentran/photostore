import createApiClient from "./api.service";
class AssetService {
  private api: any;

  constructor(baseUrl = "/api/v1") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
  }
  async GetAsset(file_path: string | undefined) {
    return this.api.get(`/uploads/${file_path}`, {
      responseType: "blob",
    });
  }
  async GetAll() {
    return (await this.api.get("/assets/all")).data.data;
  }
  async GetMetadata(file_path: string | undefined) {
    return (await this.api.get(`/${file_path}/metadata`)).data.data;
  }
  async GetNextPre(name: string | undefined) {
    return (await this.api.get(`/${name}/nextprev/metadata`)).data;
  }
  async Count() {
    return (await this.api.get("assets/count")).data.data;
  }
  async Update(
    id: number | undefined,
    payload: Partial<{
      is_deleted: boolean;
      is_private: boolean;
      is_favorite: boolean;
    }>
  ) {
    return (await this.api.patch(`assets/${id}`, payload)).data;
  }
  async Upload(formData: FormData) {
    return (
      await this.api.post("assets/upload-images", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
    ).data;
  }
  async UploadImageForSearch(formData: FormData) {
    return (
      await this.api.post("assets/search", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
    ).data.data;
  }
}

export default new AssetService();
