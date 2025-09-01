import createApiClient from "./api";

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
  async logOut() {
    this.resetLocalStorage();
  }
}
export default new LoginService();