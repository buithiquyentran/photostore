import { createApiClient } from "./api";

class AuthService {
  private api: any;

  constructor(baseUrl = "api/v1/auth") {
    this.api = createApiClient(baseUrl);
  }
  async Login(data: any) {
    return (await this.api.post("/login", data)).data;
  }
  async Logout() {
    return (await this.api.post("/logout")).data;
  }
}

export function resetLocalStorage() {
  localStorage.removeItem("access_token");
  localStorage.clear();
  return;
}

export function logOut() {
  resetLocalStorage();
}

export const authService = new AuthService();
