import React, { useEffect } from "react";
import AsssetService from "../util/photostore.api";
import { authService } from "@/components/util/login.api";

const Brower = () => {
  // useEffect(() => {
  //   const fetchAssets = async () => {
  //     try {
  //       const assets = await AsssetService.GetAllAssets();
  //       console.log("Fetched assets:", assets);
  //     } catch (error) {
  //       console.error("Error fetching assets:", error);
  //     }
  //   };
  //   fetchAssets();
  // }, []);
  // lấy user info từ /me
  const fetchUser = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      return;
    }

    try {
      await authService.GetMe(
       token);
    } catch (error) {
      console.error("Lỗi khi lấy thông tin user:", error);
    }
  };

  // chạy khi app load
  useEffect(() => {
    fetchUser();
  }, []);
  return <div className="bg-bg text-paragraph">Brower</div>;
};

export default Brower;
