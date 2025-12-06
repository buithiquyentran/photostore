import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { UploadCloud, Upload, ChevronDown } from "lucide-react";
import PreviewUploadDialog from "@/components/ui/Modals/PreviewUploadDialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import FolderService from "@/components/api/folder.service";
import { useLocation } from "react-router-dom";
import { toast } from "@/hooks/use-toast";

import { cn } from "@/lib/utils";
import FolderGrid from "@/components/ui/Folders/FolderGrid";
import BreadcrumbPath from "@/components/ui/Folders/BreadcrumbPath";
import { useOutletContext, useNavigate } from "react-router-dom";
import MosaicView from "@/components/ui/View/MosaicView";
import ListView from "@/components/ui/View/ListView";
import CardView from "@/components/ui/View/CardView";
import AssetsService from "@/components/api/assets.service";

import { Asset, Folder, Filter } from "@/interfaces/interfaces";

type DashboardContextType = {
  assetsOutlet: Asset[];
  view: string;
  foldersOutlet: Folder[];
  onUpload: (
    e: React.ChangeEvent<HTMLInputElement> | File[],
    isPrivate?: boolean,
    project_slug?: string | null,
    folder_slug?: string | null
  ) => void;
  fetchContent: (filters: Filter) => void;

  setFolderPath: React.Dispatch<React.SetStateAction<string>>;
  selectedMenu: string;
  setSelectedMenu: React.Dispatch<React.SetStateAction<string>>;
};

export default function Dashboard() {
  const {
    assetsOutlet,
    view,
    foldersOutlet,
    onUpload,
    fetchContent,
    setFolderPath,
    selectedMenu,
    setSelectedMenu,
  } = useOutletContext<DashboardContextType>();
  const [assets, setAssets] = useState<Asset[]>(assetsOutlet);
  const navigate = useNavigate();
  const location = useLocation();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewFiles, setPreviewFiles] = useState<File[]>([]);
  const [showPreviewDialog, setShowPreviewDialog] = useState(false);
  const [uploadingFolder, setUploadingFolder] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      setPreviewFiles(files);
      setShowPreviewDialog(true);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);

      // Check if this is folder upload by checking webkitRelativePath
      const isFolder = files.some((f) => f.webkitRelativePath);

      if (isFolder && files.length > 0) {
        // Get folder name from first file's path
        const folderName = files[0].webkitRelativePath.split("/")[0];
        setUploadingFolder(folderName);
        console.log("Uploading folder:", folderName);
      } else {
        setUploadingFolder(null);
      }

      setPreviewFiles(files);
      setShowPreviewDialog(true);
    }
  };

  const handleConfirmUpload = async (files: File[], isPrivate: boolean) => {
    try {
      // If uploading a folder, create folders first
      if (uploadingFolder) {
        const pathParts = location.pathname
          .replace(/^\/dashboard\/?/, "")
          .split("/")
          .filter(Boolean);

        const project_slug = pathParts[0];
        const folder_slug =
          pathParts.length > 1 ? pathParts[pathParts.length - 1] : null;

        const folder = await FolderService.Create({
          project_slug,
          folder_slug,
          name: uploadingFolder,
        });
        await onUpload(files, isPrivate, folder.project_slug, folder.slug);

        toast({
          title: "Folder created!",
          description: `Created folder "${uploadingFolder}" and uploading ${files.length} files...`,
        });
      }

      // Call parent's onUpload with files
      onUpload(files, isPrivate);
      setShowPreviewDialog(false);
      setPreviewFiles([]);
      setUploadingFolder(null);

      // Reset file inputs
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
      if (folderInputRef.current) {
        folderInputRef.current.value = "";
      }
    } catch (err) {
      console.error("Upload failed:", err);
      toast({
        title: "Upload failed",
        description: "Could not create folder or upload files.",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async (asset_id: number) => {
    try {
      await AssetsService.Update(asset_id, { is_deleted: true });
      setAssets((prev) => prev.filter((p) => p.id !== asset_id));
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };

  useEffect(() => {
    setAssets(assetsOutlet);
  }, [assetsOutlet, view, setFolderPath]);

  const renderView = () => {
    switch (view) {
      case "list":
        return (
          <ListView
            assets={assets}
            // onSelect={(a) => navigate(`/photos/${a.path}`)}
          />
        );
      case "card":
        return (
          <CardView
            assets={assets}
            onSelect={(a) => navigate(`/photos/${a.path}`)}
            onDelete={handleDelete}
          />
        );
      default:
        return (
          <MosaicView
            assets={assets}
            onSelect={(a) => navigate(`/photos/${a.path}`)}
          />
        );
    }
  };

  return (
    <main
      className="flex-1 overflow-y-auto p-4 bg-[rgb(31,36,46)] "
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <div className="mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-foreground mb-1">
              <BreadcrumbPath
                fetchContent={fetchContent}
                setFolderPath={setFolderPath}
                setSelectedMenu={setSelectedMenu}
              />
            </h2>
            <p className="text-sm text-muted-foreground">
              {assetsOutlet?.length} items
            </p>
          </div>

          {/* Upload Dropdown Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="bg-primary text-[#000] hover:bg-primary/90">
                <UploadCloud className="h-4 w-4 mr-2" />
                Upload
                <ChevronDown className="h-4 w-4 ml-2" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => fileInputRef.current?.click()}>
                <UploadCloud className="h-4 w-4 mr-2" />
                Upload Files
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => folderInputRef.current?.click()}>
                <Upload className="h-4 w-4 mr-2" />
                Upload Folder
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Hidden input for files */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Hidden input for folder */}
          <input
            ref={folderInputRef}
            type="file"
            multiple
            accept="image/*"
            // @ts-expect-error - webkitdirectory is not in TypeScript types but supported by browsers
            webkitdirectory="true"
            directory="true"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
        {/* folders */}
        <FolderGrid
          folders={foldersOutlet}
          setFolderPath={setFolderPath}
          selectedMenu={selectedMenu}
          setSelectedMenu={setSelectedMenu}
        />
        {assets?.length === 0 ? (
          <Card
            className={cn(
              "border-2 border-dashed p-12 text-center transition-colors",
              dragActive
                ? "border-primary bg-primary/5"
                : "border-border bg-card"
            )}
          >
            <UploadCloud className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Upload your first files
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Drag and drop files or folders here, or use the upload button
            </p>
            <div className="flex gap-2 justify-center">
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                className="border-border text-foreground hover:bg-accent"
              >
                <UploadCloud className="h-4 w-4 mr-2" />
                Choose Files
              </Button>
              <Button
                onClick={() => folderInputRef.current?.click()}
                variant="outline"
                className="border-border text-foreground hover:bg-accent"
              >
                <Upload className="h-4 w-4 mr-2" />
                Choose Folder
              </Button>
            </div>
          </Card>
        ) : (
          <div className="p-4">{renderView()}</div>
        )}
        {dragActive && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 pointer-events-none">
            <div className="bg-card border-2 border-dashed border-primary rounded-lg p-12 text-center">
              <Upload className="h-16 w-16 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold text-foreground">
                Drop files or folders to upload
              </h3>
            </div>
          </div>
        )}

        {/* Preview Upload Dialog */}
        <PreviewUploadDialog
          open={showPreviewDialog}
          files={previewFiles}
          onClose={() => {
            setShowPreviewDialog(false);
            setPreviewFiles([]);
            setUploadingFolder(null);
            if (fileInputRef.current) {
              fileInputRef.current.value = "";
            }
            if (folderInputRef.current) {
              folderInputRef.current.value = "";
            }
          }}
          onConfirm={handleConfirmUpload}
        />
      </div>
    </main>
  );
}
