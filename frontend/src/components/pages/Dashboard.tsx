import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import {
  MoreVertical,
  Download,
  Trash2,
  Star,UploadCloud, Upload
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { cn } from "@/lib/utils";
import FolderGrid from "@/components/ui/FolderGrid";
import BreadcrumbPath from "@/components/ui/BreadcrumbPath";
import { useOutletContext } from "react-router-dom";

type DashboardContextType = {
  assets: any[];
  folders: any[];
  onUpload: any;
  refetchFolders: any;
  setFolderPath: React.Dispatch<React.SetStateAction<string>>;
  selectedMenu: string;
  setSelectedMenu: React.Dispatch<React.SetStateAction<string>>;
};

export default function Dashboard() {
  const {
    assets,
    folders,
    onUpload,
    refetchFolders,
    setFolderPath,
    selectedMenu,
    setSelectedMenu,
  } = useOutletContext<DashboardContextType>();
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

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffInDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffInDays === 0) return "Today";
    if (diffInDays === 1) return "Yesterday";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    return date.toLocaleDateString();
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
              />
            </h2>
            <p className="text-sm text-muted-foreground">
              {assets.length} items
            </p>
          </div>
          <Button
            onClick={() => fileInputRef.current?.click()}
            className="bg-primary text-[#000] hover:bg-primary/90"
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
          folders={folders}
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {assets?.map((file) => (
              <Card
                key={file.id}
                className="group overflow-hidden bg-card border border-gray-700 hover:border-primary/50 transition-all cursor-pointer"
              >
                <div className="aspect-video bg-muted relative overflow-hidden">
                  <img
                    src={file.file_url || "/placeholder.svg"}
                    alt={file.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <Button
                      size="icon"
                      variant="secondary"
                      className="h-8 w-8 bg-background/90 hover:bg-background"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      size="icon"
                      variant="secondary"
                      className="h-8 w-8 bg-background/90 hover:bg-background"
                    >
                      <Star className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-foreground truncate mb-1">
                        {file.name}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {file.created_at}
                      </p>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground"
                        >
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent
                        align="end"
                        className="bg-popover border-border"
                      >
                        <DropdownMenuItem className="text-popover-foreground hover:bg-accent">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-popover-foreground hover:bg-accent">
                          <Star className="h-4 w-4 mr-2" />
                          Add to Starred
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive hover:bg-destructive/10">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </Card>
            ))}
          </div>
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
