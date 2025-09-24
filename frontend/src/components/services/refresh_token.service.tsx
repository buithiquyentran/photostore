import createApiClient from "./api.service";

class RefreshService {
  private api: any;

  constructor(baseUrl = "api/v1/auth") {
    this.api = createApiClient(baseUrl);
  }
  async  refreshToken() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return null;
    try {
        const res = await this.api.post("/refresh", {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = res.data;
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        return access_token;
    } catch (err) {
        console.error("Refresh token failed", err);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        // window.location.href = "/login";
        return null;
    }
}
}
export default new RefreshService();
