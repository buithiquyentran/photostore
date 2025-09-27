import axios from "axios";
async function RefreshToken() {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return null;
  try {
    // gọi API refresh
    const res = await axios.post(
      "/api/v1/auth/refresh",
      { refresh_token: refreshToken },
      {
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );
    const { access_token, refresh_token } = res.data;
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    return access_token;
  } catch (err) {
    console.error("Refresh token failed", err);
    // localStorage.removeItem("access_token");
    // localStorage.removeItem("refresh_token");
    // window.location.href = "/login";
    return null;
  }
}
export default RefreshToken;
