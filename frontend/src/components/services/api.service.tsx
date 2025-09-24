import axios from "axios";
import keycloak from "@/keycloak";
const commonConfig = {
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
};
const createApiClient = (baseURL: string) => {
  const api = axios.create({
    baseURL,
    ...commonConfig,
  });
  

  return api;
};

export default createApiClient;
