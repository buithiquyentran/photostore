import createApiClient from "./api.service";
class UserService {
  private api: any;

  constructor(baseUrl = "/api/v1/users/") {
    this.api = createApiClient(baseUrl);
  }
  async GetMe() {
    const res = await this.api.get("/me");
    return res.data;
  }
  async SocialLogin() {
    const res = await this.api.post("/social-login");
    return res.data;
  }
  async GetAll() {
    return (await this.api.get("assets/all")).data.data;
  }
  async GetMetadata(name: string | undefined) {
    return (await this.api.get(`assets/${name}/metadata`)).data.data;
  }
  async GetNextPre(name: string | undefined) {
    return (await this.api.get(`assets/${name}/nextprev/metadata`)).data;
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

export default new UserService();
