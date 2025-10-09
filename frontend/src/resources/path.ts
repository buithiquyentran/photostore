const path = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",

  BROWER: "/dashboard",
  FAVORITE: "/dashboard/favorite",
  VIEWER: "/viewer",
  TEST: "/test",
  TRASH: "/dashboard/trash",

  DASHBOARD: "/dashboard/*",
} as const;

export default path;
