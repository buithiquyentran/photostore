import { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
import UserService from "@/components/api/user.service";
import AssetsService from "@/components/api/assets.service";
const Layout = () => {
  // const [searchResults, setSearchResults] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [queryText, setqueryText] = useState<string>("");
  const handleSearchText = (text: string) => {
    setqueryText(text);
    console.log("Searching by text:", text);
    // Gọi API backend tìm kiếm text
  };

  const fetchAssets = async () => {
    try {
      const user_assets = await AssetsService.GetAll({
        is_deleted: false,
      });

      const response = [...user_assets];
      setAssets(response);
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  };
  // chạy khi app load
  useEffect(() => {
    fetchAssets();
  }, []);
  const handleSearchByFile = async (e) => {
    const file = e.target.files?.[0];

    if (file) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        const res = await UserService.UploadImageForSearch(formData);
        setAssets(res); // Lưu kết quả tìm kiếm vào state
      } catch (err) {
        console.error("Search failed", err);
      }
    }
  };
  const handleSearchByText = async (text: string) => {
    if (text) {
      try {
        const formData = new FormData();
        formData.append("query_text", text);
        const res = await AssetsService.UploadImageForSearch(formData);
        setAssets(res); // Lưu kết quả tìm kiếm vào state
      } catch (err) {
        console.error("Search failed", err);
      }
    } else {
      const res = await AssetsService.GetAll();
      setAssets(res); // Lưu kết quả tìm kiếm vào state
    }
  };

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]); // phải trùng với tên param trong BE
      }

      try {
        const res = await AssetsService.Upload(formData);

        console.log("Upload results:", res.data);
        alert("Upload thành công");
      } catch (err) {
        console.error(err);
        alert("Upload thất bại");
      }
    }
  };

  return (
    <>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="grow flex flex-col bg-bg">
          <SearchBar
            onSearchFile={handleSearchByFile}
            onSearchText={handleSearchByText}
            onUpload={handleUpload}
          />
          <div className="grow">
            <Outlet context={{ assets }} />
          </div>
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default Layout;
