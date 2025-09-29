import { format } from "date-fns";

// Chuyển đổi kích thước tệp từ bytes sang định dạng dễ đọc hơn
function formatFileSize(size: number): string {
  if (size === 0) return "0 B";

  const units = ["B", "KB", "MB", "GB", "TB"];
  const k = 1024;
  const i = Math.floor(Math.log(size) / Math.log(k));

  const formatted = (size / Math.pow(k, i)).toFixed(2); // giữ 2 số thập phân
  return `${formatted} ${units[i]}`;
}

const formatted = (dt: string) => {
  return format(new Date(dt), "MMM dd, yyyy h:mm a");
  // 👉 "Sep 29, 2025 1:29 AM"
};
export { formatFileSize, formatted };
