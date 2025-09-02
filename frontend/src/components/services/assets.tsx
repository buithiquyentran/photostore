import createApiClient from "./api";
import axios from "axios";

class AssetService {
  private api: any;

  constructor(baseUrl = "/api/v1/assets") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);

    // Gắn interceptor sau khi api đã khởi tạo
    this.api.interceptors.response.use(
      (res: any) => res,
      async (error: any) => {
        if (error.response && error.response.status === 401) {
          const refreshToken = localStorage.getItem("refresh_token");

          if (refreshToken) {
            try {
              // Gọi API để refresh token
              const res = await axios.post("/api/v1/auth/refresh", {
                refresh_token: refreshToken,
              });

              // Lưu access_token mới
              localStorage.setItem("access_token", res.data.access_token);

              // Gắn token mới vào header và thử lại request
              error.config.headers[
                "Authorization"
              ] = `Bearer ${res.data.access_token}`;
              return this.api(error.config);
            } catch (refreshError) {
              console.error("Refresh token failed", refreshError);
              // Nếu refresh token lỗi => đăng xuất người dùng
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              window.location.href = "/login";
            }
          }
        }
        return Promise.reject(error);
      }
    );
  }

  async GetAllAssets() {
    return (await this.api.get("/all")).data.data;
  }
  async Count (){
    return (await this.api.get("/count")).data.data;
  }
}

export default new AssetService();
