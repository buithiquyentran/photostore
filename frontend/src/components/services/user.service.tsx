import createApiClient from "./api.service";
import RefreshService from "./refresh_token.service";
class UserService {
  private api: any;

  constructor(baseUrl = "/api/v1/users/users") {
    this.api = createApiClient(baseUrl);
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    this.api.interceptors.response.use(
      (res: any) => res,
      async (error: any) => {
        const originalRequest = error.config;

        // Trường hợp 401 → refresh token
        if (
          error.response &&
          error.response.status === 401 &&
          !originalRequest._retry
        ) {
          originalRequest._retry = true;
          try {
            const newToken = await RefreshService.refreshToken();
            if (newToken) {
              localStorage.setItem("access_token", newToken);
              originalRequest.headers["Authorization"] = `Bearer ${newToken}`;
              return this.api(originalRequest); // retry request ban đầu
            }
          } catch {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login";
          }
        }

        // Trường hợp 500 → logout luôn
        if (error.response && error.response.status === 500) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }

        return Promise.reject(error);
      }
    );
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
