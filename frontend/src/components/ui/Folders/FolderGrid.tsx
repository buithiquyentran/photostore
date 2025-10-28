import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import {
  FolderIcon,
  MoreVertical,
  FolderOpen,
  Share,
  Trash2,
  Edit,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import ShareDialog from "@/components/ui/Modals/ShareDialog";
interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug: string;
  path: string;
}
interface FolderGridProps {
  folders: FolderNode[] | null;
  selectedMenu: string;
  setSelectedMenu: (id: string) => void;
  setFolderPath: (path: string) => void;
}

export default function FolderGrid({
  folders,
  selectedMenu,
  setSelectedMenu,
  setFolderPath,
}: FolderGridProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [shareFolder, setShareFolder] = useState<FolderNode | null>(null);
  const pathParts = location.pathname.replace(/^\/dashboard\/?/, "");

  const handleOpenFolder = (folder: FolderNode) => {
    if (selectedMenu === folder.id) return;
    console.log(selectedMenu, folder.id);
    const fullPath = pathParts ? `${pathParts}/${folder.slug}` : folder.slug;
    console.log(fullPath);
    setFolderPath(fullPath);
    navigate(`/dashboard/${fullPath}`);
    setSelectedMenu(folder.path);
  };
  if (!folders?.length)
    return (
      <p className="text-muted-foreground text-sm p-4 italic">
        No folders in this directory
      </p>
    );

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-6">
      {folders.map((folder) => (
        <Card
          key={folder.id}
          className="group relative border border-gray-700 hover:border-primary/50 transition-colors"
          onClick={() => handleOpenFolder(folder)}
        >
          <CardContent className="p-2 flex items-center justify-between">
            <div className="flex items-center gap-2 truncate">
              <FolderIcon className="h-5 w-5 text-yellow-400" />
              <span className="font-medium truncate text-sm group-hover:text-primary">
                {folder.name}
              </span>
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => e.stopPropagation()}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MoreVertical className="h-4 w-4 text-white" />
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                align="end"
                className="w-40 bg-popover border-border"
              >
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenFolder(folder);
                  }}
                >
                  <FolderOpen className="h-4 w-4 mr-2" /> Open
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation();
                    setShareFolder(folder);
                  }}
                >
                  <Share className="h-4 w-4 mr-2" /> Share
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Edit className="h-4 w-4 mr-2" /> Rename
                </DropdownMenuItem>
                <DropdownMenuSeparator />

                <DropdownMenuItem className="text-destructive">
                  <Trash2 className="h-4 w-4 mr-2" /> Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </CardContent>
        </Card>
      ))}

      {/* Hộp thoại chia sẻ */}
      {shareFolder && (
        <ShareDialog
          folder={shareFolder}
          onClose={() => setShareFolder(null)}
        />
      )}
    </div>
  );
}
