import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import {
  MoreVertical,
  Download,
  Trash2,
  Star,
  UploadCloud,
  Upload,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { cn } from "@/lib/utils";
import FolderGrid from "@/components/ui/Folders/FolderGrid";
import BreadcrumbPath from "@/components/ui/Folders/BreadcrumbPath";
import { useOutletContext, useNavigate } from "react-router-dom";
import MosaicView from "@/components/ui/View/MosaicView";
import ListView from "@/components/ui/View/ListView";
import CardView from "@/components/ui/View/CardView";
type DashboardContextType = {
  assetsOutlet: any[];
  view: any[];
  foldersOutlet: any[];
  onUpload: any;
  refetchFolders: any;
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
    refetchFolders,
    setFolderPath,
    selectedMenu,
    setSelectedMenu,
  } = useOutletContext<DashboardContextType>();
  const [assets, setAssets] = useState<any[]>(assetsOutlet);
  const navigate = useNavigate();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
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
      onUpload(Array.from(e.dataTransfer.files));
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
            // onDelete={handleDelete}
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
                refetchFolders={refetchFolders}
                setFolderPath={setFolderPath}
                setSelectedMenu={setSelectedMenu}
              />
            </h2>
            <p className="text-sm text-muted-foreground">
              {assetsOutlet?.length} items
            </p>
          </div>
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={selectedMenu?.split("/").length ==1} // disable khi ở root project
            className="bg-primary text-[#000] hover:bg-primary/90 disabled:opacity-50 disabled:pointer-events-none"
          >
            <UploadCloud className="h-4 w-4 mr-2" />
            Upload Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={onUpload}
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
              Drag and drop files here, or click the upload button
            </p>
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
              className="border-border text-foreground hover:bg-accent"
            >
              Choose Files
            </Button>
          </Card>
        ) : (
          <div className="p-4">{renderView()}</div>
        )}
        {dragActive && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 pointer-events-none">
            <div className="bg-card border-2 border-dashed border-primary rounded-lg p-12 text-center">
              <Upload className="h-16 w-16 mx-auto mb-4 text-primary" />
              <h3 className="text-xl font-semibold text-foreground">
                Drop files to upload
              </h3>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
