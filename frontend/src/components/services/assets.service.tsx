import createApiClient from "./api.service";
import axios from "axios";
class AssetService {
  private api: any;

  constructor(baseUrl = "/api/v1/users/assets") {
    // Khởi tạo api
    this.api = createApiClient(baseUrl);
    // Interceptor để gắn token vào header
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    // Gắn interceptor sau khi api đã khởi tạo
    this.api.interceptors.response.use(
      (res: any) => res,
      async (error: any) => {
        const originalRequest = error.config;

        if (error.response && error.response.status === 401) {
          const refreshToken = localStorage.getItem("refresh_token");
          if (refreshToken) {
            try {
              const res = await axios.post("/api/v1/auth/refresh", {
                refresh_token: refreshToken,
              });

              localStorage.setItem("access_token", res.data.access_token);

              originalRequest.headers[
                "Authorization"
              ] = `Bearer ${res.data.access_token}`;

              return this.api(originalRequest);
            } catch (refreshError) {
              console.error("Refresh token failed", refreshError);
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

  async GetPublicAssets() {
    return (await this.api.get("/public_asssets")).data.data;
  }
  async GetAll() {
    return (await this.api.get("/all")).data.data;
  }
  async GetSignedUrl(asset_id: string) {
    return (await this.api.get(`/${asset_id}/signed-url`)).data.data;
  }
  async Count() {
    return (await this.api.get("/count")).data.data;
  }
  async Upload(formData: FormData) {
    return (
      await this.api.post("/upload-images", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
    ).data;
  }
  async UploadImageForSearch(formData: FormData) {
    return (
      await this.api.post("/search", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
    ).data.data;
  }
}

export default new AssetService();
