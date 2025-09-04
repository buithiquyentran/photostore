import createApiClient from "./api.service";

class LoginService {
  private api: any;

  constructor(baseUrl = "api/v1/auth") {
    this.api = createApiClient(baseUrl);
  }
  async Login(data: any) {
    return (await this.api.post("/login", data)).data;
  }
  async resetLocalStorage() {
    localStorage.removeItem("access_token");
    localStorage.clear();
    return;
  }
  async LogOut() {
    this.resetLocalStorage();
  }
}
export default new LoginService();
