import createApiClient from "./api.service";
class SearchService {
  private api: any;

  constructor(baseUrl = "/api/v1/search") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
  }

  async Search(formData: FormData) {
    return (
      await this.api.post("/image", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
    ).data.data;
  }
}

export default new SearchService();
