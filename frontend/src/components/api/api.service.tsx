import axios, { AxiosError, AxiosInstance } from "axios";
import RefreshToken from "./refresh_token.service";

const commonConfig = {
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
};

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function addSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}
function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

const createApiClient = (baseURL: string): AxiosInstance => {
  const api = axios.create({
    baseURL,
    ...commonConfig,
  });

  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (res) => res,
    async (error: AxiosError) => {
      const originalRequest = (error.config || {}) as any;

      // network / CORS errors: error.response === undefined
      if (!error.response) {
        console.error("Network/CORS error or no response:", error);
        return Promise.reject(error);
      }

      // 1) Chỉ xử lý REFRESH khi backend trả 401
      if (error.response.status !== 401) {
        return Promise.reject(error);
      }

      // 2) Nếu request chính là refresh endpoint -> không retry
      const url = originalRequest.url || "";
      if (typeof url === "string" && url.includes("/auth/refresh")) {
        return Promise.reject(error);
      }

      // 3) Nếu đã retry rồi thì bỏ
      if (originalRequest._retry) {
        return Promise.reject(error);
      }

      // 4) Queue handling: nếu đang refresh, subscribe và đợi token mới
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          addSubscriber((token: string) => {
            originalRequest.headers = {
              ...originalRequest.headers,
              Authorization: `Bearer ${token}`,
            };
            resolve(api(originalRequest));
          });
        });
      }

      // 5) Bắt đầu quá trình refresh
      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const newToken = await RefreshToken();
        if (!newToken) {
          // refresh fail -> logout
          localStorage.clear();
          window.location.href = "/login";
          return Promise.reject(error);
        }

        // broadcast token mới cho các request chờ
        onRefreshed(newToken);

        // retry original
        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${newToken}`,
        };
        return api(originalRequest);
      } catch (err) {
        localStorage.clear();
        window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
  );

  return api;
};

export default createApiClient;
