import axios from "axios";
const commonConfig = {
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
};
export const createApiClient = (baseURL: string) => {
  return axios.create({
    baseURL,
    ...commonConfig,
  });
};
