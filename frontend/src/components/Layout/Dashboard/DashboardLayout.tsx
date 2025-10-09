import { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
import UserService from "@/components/api/user.service";
import AssetsService from "@/components/api/assets.service";
import folderService from "@/components/api/folder.service";
interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug?: string;
}
const Layout = () => {
  // const [searchResults, setSearchResults] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [queryText, setqueryText] = useState<string>("");
  const [selectedMenu, setSelectedMenu] = useState<string>("");
  const [folders, setFolders] = useState<FolderNode[] | null>([]);
  const [folderPath, setFolderPath] = useState<string>("");

  const fetchFolderContent = async () => {
    try {
      if (folderPath) {
        const response = await folderService.GetContent({
          path: folderPath,
        });
        setFolders(response.folders);
        setAssets(response.assets);
      } else {
        const user_assets = await AssetsService.GetAll({
          is_deleted: false,
        });

        const response = [...user_assets];
        setAssets(response);
      }
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  };

  // chạy khi app load
  useEffect(() => {
    fetchFolderContent();
  }, [folderPath]);
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
        <Sidebar
          selectedMenu={selectedMenu}
          setSelectedMenu={setSelectedMenu}
          setFolderPath={setFolderPath}
        />
        <div className="grow flex flex-col bg-background">
          <SearchBar
            onSearchFile={handleSearchByFile}
            onSearchText={handleSearchByText}
            onUpload={handleUpload}
          />
          <div className="grow">
            <Outlet context={{ assets, folders }} />
          </div>
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default Layout;
