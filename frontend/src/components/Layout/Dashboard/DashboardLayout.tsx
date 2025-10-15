import { useState, useEffect, useCallback } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar/Sidebar";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
import SearchService from "@/components/api/search.service";
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
  const pathParts = location.pathname.replace(/^\/dashboard\/?/, "");
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedMenu, setSelectedMenu] = useState<string>("");
  const [folders, setFolders] = useState<FolderNode[] | null>([]);
  const [folderPath, setFolderPath] = useState<string>(pathParts);

  const fetchFolderContent = useCallback(async () => {
    try {
      if (folderPath) {
        const response = await folderService.GetContent({ path: folderPath });
        setFolders(response.folders);
        setAssets(response.assets);
      } else {
        const user_assets = await AssetsService.GetAll({ is_deleted: false });
        setAssets(user_assets);
      }
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  }, [folderPath]); // ✅ khai báo folderPath là dependency ở đây

  useEffect(() => {
    fetchFolderContent();
  }, [fetchFolderContent]); // ✅ thêm fetchFolderContent vào deps

  const handleSearchByFile = async (e) => {
    const file = e.target.files?.[0];

    if (file) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("query_text", "many people");
        const res = await SearchService.Search(formData);
        console.log(res);
        setAssets(res); // Lưu kết quả tìm kiếm vào state
      } catch (err) {
        console.error("Search failed", err);
      }
    }
  };
  const handleSearchByText = async (text: string) => {
    // if (text) {
    //   try {
    //     const formData = new FormData();
    //     formData.append("query_text", text);
    //     const res = await AssetsService.UploadImageForSearch(formData);
    //     setAssets(res); // Lưu kết quả tìm kiếm vào state
    //   } catch (err) {
    //     console.error("Search failed", err);
    //   }
    // } else {
    //   const res = await AssetsService.GetAll();
    //   setAssets(res); // Lưu kết quả tìm kiếm vào state
    // }
  };

  const handleUpload = async (
    eOrFiles: React.ChangeEvent<HTMLInputElement> | File[]
  ) => {
    let files: File[] = [];

    // Nếu là sự kiện từ input
    if (Array.isArray(eOrFiles)) {
      files = eOrFiles;
    } else if (eOrFiles?.target?.files) {
      files = Array.from(eOrFiles.target.files);
    }

    if (files.length === 0) return;
    if (files && files.length > 0) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]); // phải trùng với tên param trong BE
      }
      if (folderPath) {
        const project_slug = folderPath.split("/")[0];
        const folder_slug = folderPath.split("/").slice(1).join("/");
        formData.append("project_slug", project_slug);
        formData.append("folder_slug", folder_slug);
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
            <Outlet
              context={{
                assets,
                folders,
                onUpload: handleUpload,
                refetchFolders: fetchFolderContent,
                setFolderPath: setFolderPath,
                selectedMenu: selectedMenu,
                setSelectedMenu: setSelectedMenu,
              }}
            />
          </div>
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default Layout;
