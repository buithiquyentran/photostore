import createApiClient from "./api.service";

class LoginService {
  private api: any;

  constructor(baseUrl = "api/v1/auth") {
    this.api = createApiClient(baseUrl);
  }
  async Login(data: any) {
    return (await this.api.post("/login", data)).data;
  }
  async Register(data: any) {
    return (await this.api.post("/register", data)).data;
  }
  async LogOut() {
    return (await this.api.post("/logout")).data;

  }
}
export default new LoginService();
