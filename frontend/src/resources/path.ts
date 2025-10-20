const path = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",

  DASHBOARD: "/dashboard",
  FAVORITE: "/dashboard/favorite",
  VIEWER: "/viewer",
  TEST: "/test",
  TRASH: "/dashboard/trash",
  MY_PROJECT: "/dashboard/my-projects",
  FOLDER_DASHBOARD: "/dashboard/*",
} as const;

export default path;

