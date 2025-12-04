import { useState, useEffect, useCallback } from "react";
import { Outlet } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

import SearchBar from "@/components/Layout/Dashboard/Searchbar";
import Sidebar from "@/components/Layout/Dashboard/Sidebar/Sidebar";
import SearchService from "@/components/api/search.service";
import AssetsService from "@/components/api/assets.service";
import { Asset } from "@/interfaces/interfaces";
interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug?: string;
}
const Layout = () => {
  const pathParts = location.pathname.replace(/^\/dashboard\/?/, "");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedMenu, setSelectedMenu] = useState<string>("");
  const [folders, setFolders] = useState<FolderNode[] | null>([]);
  const [folderPath, setFolderPath] = useState<string>(pathParts);
  const [view, setView] = useState<string>("mosaic"); //"mosaic" | "list" | "card";
  const { toast } = useToast();


  const fetchContent = useCallback(
    async (filters = {}) => {
      try {
        let response;
        if (folderPath === "home") {
          response = await AssetsService.GetAll({
            is_deleted: false,
            ...filters,
          });
        } else if (folderPath === "trash") {
          response = await AssetsService.GetAll({
            is_deleted: true,
            ...filters,
          });
        } else if (folderPath === "favorite") {
          response = await AssetsService.GetAll({
            is_deleted: false,
            is_favorite: true,
            ...filters,
          });
        } else {
          response = await AssetsService.GetAll({
            folder_path: folderPath,
            ...filters,
          });
        }
        setFolders(response.folders);
        setAssets(response.assets);
      } catch (error) {
        console.error("Error fetching assets:", error);
      }
    },
    [folderPath]
  );

  useEffect(() => {
    fetchContent();
  }, [fetchContent]); // ✅ thêm fetchContent vào deps

  const handleSearch = (
    e?: React.ChangeEvent<HTMLInputElement> | null,
    queryText?: string
  ): void => {
    (async () => {
      try {
        const formData = new FormData();

        // Nếu gọi từ input file thì có e.target.files
        if (e) {
          const file = e?.target?.files?.[0];
          if (file) {
            formData.append("file", file);
          }
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
    })();
  };

  const handleUpload = async (
    eOrFiles: React.ChangeEvent<HTMLInputElement> | File[],
    isPrivate: boolean = false
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

      // Thêm is_private vào formData
      formData.append("is_private", isPrivate.toString());

      if (
        folderPath &&
        folderPath !== "home" &&
        folderPath !== "trash" &&
        folderPath !== "favorite"
      ) {
        const project_slug = folderPath.split("/")[0];
        const folder_slug = folderPath.split("/").slice(1).join("/");
        formData.append("project_slug", project_slug);
        formData.append("folder_slug", folder_slug);
      }

      try {
        await AssetsService.Upload(formData);
        toast({
          title: "Success",
          description: "Upload successfully",
        });
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
            onSearch={handleSearch}
            onUpload={handleUpload}
            fetchContent={fetchContent}
            view={view}
            setView={setView}
          />

          <div className="grow">
            <Outlet
              context={{
                assetsOutlet: assets,
                foldersOutlet: folders,
                view: view,
                onUpload: handleUpload,
                fetchContent: fetchContent,
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
