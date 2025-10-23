import { useState, useEffect, useCallback } from "react";
import { Outlet } from "react-router-dom";
import {
  RotateCcw,
  LayoutDashboard,
  LayoutList,
  LayoutGrid,
} from "lucide-react";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
import Sidebar from "@/components/Layout/Dashboard/Sidebar/Sidebar";
import SearchService from "@/components/api/search.service";
import AssetsService from "@/components/api/assets.service";
import folderService from "@/components/api/folder.service";

import SortDropdown from "@/components/ui/SortDropdown";
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
  const [view, setView] = useState<"mosaic" | "list" | "card">("mosaic");

  const fetchFolderContent = useCallback(async () => {
    try {
      let response;
      if (folderPath === "home") {
        response = await AssetsService.GetAll({ is_deleted: false });
        setAssets(response);
        console.log(response)
      } else if (folderPath === "trash") {
        response = await AssetsService.GetAll({ is_deleted: true });
        setAssets(response);
      } else if (folderPath === "favorite") {
        response = await AssetsService.GetAll({
          is_deleted: false,
          is_favorite: true,
        });
        setAssets(response);
      } else {
        response = await folderService.GetContent({ path: folderPath });
        setFolders(response.folders);
        setAssets(response.assets);
      }
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  }, [folderPath]);

  useEffect(() => {
    fetchFolderContent();
  }, [fetchFolderContent]); // ✅ thêm fetchFolderContent vào deps

  const handleSearch = async (e, queryText: string) => {
    try {
      const formData = new FormData();

      // Nếu gọi từ input file thì có e.target.files
      const file = e?.target?.files?.[0];
      if (file) {
        formData.append("file", file);
      }

      // Nếu có text search thì thêm query_text
      if (queryText) {
        formData.append("query_text", queryText);
      }

      // Gọi API
      const res = await SearchService.Search(formData);
      console.log("Search result:", res);
      setAssets(res); // ✅ Tùy backend trả về dạng nào
    } catch (err) {
      console.error("Search failed", err);
    }
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
          <SearchBar onSearch={handleSearch} onUpload={handleUpload} />
          <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 text-white">
            <button
              // onClick={fetchAssets}
              className="flex items-center text-gray-400 hover:text-white px-2"
            >
              <RotateCcw size={20} /> &nbsp;
              <span className="text-sm">Refresh</span>
            </button>

            <div className="flex items-center gap-4">
              <SortDropdown />
              <div className="flex gap-3 p-1 shadow-md">
                <button
                  onClick={() => setView("mosaic")}
                  className={`p-2 rounded-full ${
                    view === "mosaic"
                      ? "text-highlight"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <LayoutDashboard size={20} />
                </button>
                <button
                  onClick={() => setView("list")}
                  className={`p-2 rounded-full ${
                    view === "list"
                      ? "text-highlight"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <LayoutList size={20} />
                </button>
                <button
                  onClick={() => setView("card")}
                  className={`p-2 rounded-full ${
                    view === "card"
                      ? "text-highlight"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <LayoutGrid size={20} />
                </button>
              </div>
            </div>
          </div>
          <div className="grow">
            <Outlet
              context={{
                assetsOutlet: assets,
                foldersOutlet: folders,
                view: view,
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
