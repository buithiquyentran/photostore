import { format, toZonedTime } from "date-fns-tz";

// Chuyển đổi kích thước tệp từ bytes sang định dạng dễ đọc hơn
function formatFileSize(size: number): string {
  if (size === 0) return "0 B";

  const units = ["B", "KB", "MB", "GB", "TB"];
  const k = 1024;
  const i = Math.floor(Math.log(size) / Math.log(k));

  const formatted = (size / Math.pow(k, i)).toFixed(2); // giữ 2 số thập phân
  return `${formatted} ${units[i]}`;
}

function formattedDate(dt: string) {
  const timeZone = "Asia/Ho_Chi_Minh"; // múi giờ VN
  const localDate = toZonedTime(new Date(dt), timeZone);
  return format(localDate, "MMM dd, yyyy h:mm a", { timeZone });
}

export { formatFileSize, formattedDate };
