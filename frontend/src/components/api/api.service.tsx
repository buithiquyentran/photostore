import axios, { AxiosError, AxiosInstance } from "axios";
import RefreshToken from "./refresh_token.service";
import { showProgressBar, hideProgressBar } from "@/hooks/useProgressBar";

const commonConfig = {
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
};

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];
// Hàm logout tách riêng để tái sử dụng
const forceLogout = () => {
  localStorage.clear(); // Hoặc removeItem các key cụ thể
  console.log("Redirecting to login...");
  window.location.href = "/login";
};
function addSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}
function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

const createApiClient = (baseURL: string): AxiosInstance => {
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL + baseURL,
    ...commonConfig,
  });

  // Request interceptor - show progress bar
  api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Show progress bar for non-refresh requests
    const url = config.url || "";
    if (!url.includes("/auth/refresh")) {
      showProgressBar();
    }

    return config;
  });

  // Response interceptor - hide progress bar
  api.interceptors.response.use(
    (res) => {
      // Hide progress bar on success
      hideProgressBar();
      return res;
    },
    async (error: AxiosError) => {
      const originalRequest = (error.config || {}) as any;
      // Xử lý trường hợp: network / CORS errors (error.response === undefined)
      if (!error.response) {
        console.warn(
          "Network Error detected. Checking for refresh token possibilities..."
        );

        const storedRefreshToken = localStorage.getItem("refresh_token");

        // TRƯỜNG HỢP 1: Không có refresh token trong máy -> Cho về Login.
        if (!storedRefreshToken) {
          forceLogout();
          return Promise.reject(error);
        }

        // TRƯỜNG HỢP 2: Có refresh token
        // -> Khả năng cao đây là lỗi 401 nhưng bị CORS chặn nên Browser báo Network Error.
        // -> tự gán status 401 vào. Để nó trôi xuống logic refresh phía dưới.
        error.response = {
          status: 401,
          data: {},
          headers: {},
          config: error.config,
          statusText: "Unauthorized",
        } as any;
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
      // Nếu không có refresh token trong storage thì không cần cố gắng refresh làm gì -> Logout luôn
      const storedRefreshToken = localStorage.getItem("refresh_token");
      if (!storedRefreshToken) {
        forceLogout();
        return Promise.reject(error);
      }
      // 4) Queue handling: nếu đang refresh, subscribe và đợi token mới
      if (isRefreshing) {
        return new Promise((resolve) => {
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
          console.log("Redirecting to login due to refresh failure");
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
        forceLogout();
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
        hideProgressBar(); // Ensure progress bar is hidden
      }
    }
  );

  return api;
};

export default createApiClient;
