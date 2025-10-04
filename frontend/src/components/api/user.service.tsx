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

}

export default new UserService();
