import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    // proxy: {
    //   "/api/v1": {
    //     target: "http://localhost:8000",
    //     changeOrigin: true,
    //   },
    // },
    // Bắt buộc: Lắng nghe trên tất cả các địa chỉ IP (tương đương --host)
    host: true,
    // --- QUAN TRỌNG NHẤT: Cấu hình Polling ---
    watch: {
      usePolling: true,
    },
    // --- Cấu hình HMR (Hot Module Replacement) ---
    hmr: {
      // Đảm bảo client (trình duyệt) kết nối đúng port mapping của Docker
      clientPort: 5173,
    },
  },
});
