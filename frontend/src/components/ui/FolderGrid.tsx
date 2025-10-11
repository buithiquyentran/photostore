import { useLocation, useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { FolderIcon, MoreVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug: string;
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

  const pathParts = location.pathname
    .replace(/^\/dashboard\/?/, "")

  const handleOpenFolder = (folder: FolderNode) => {
    if (selectedMenu === folder.id) return;
    console.log(selectedMenu, folder.id);
    const fullPath = pathParts ? `${pathParts}/${folder.slug}` : folder.slug;
    console.log(fullPath);
    setFolderPath(fullPath);
    navigate(`/dashboard/${fullPath}`);
    setSelectedMenu(folder.id);
  };
  if (!folders?.length)
    return (
      <p className="text-muted-foreground text-sm p-4 italic">
        No folders in this directory
      </p>
    );

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4  gap-4 mb-6 ">
      {folders.map((folder) => (
        <motion.div
          key={folder.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
        >
          <Card
            className="group relative cursor-pointer hover:bg-accent/40 transition-colors border-border border border-gray-700"
            onClick={() => handleOpenFolder(folder)}
          >
            <CardContent className="p-2 flex items-center justify-between">
              <div className="flex items-center gap-2 truncate">
                <FolderIcon className="h-5 w-5 text-yellow-400" />
                <span className="font-medium truncate text-sm group-hover:text-primary">
                  {folder.name}
                </span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => e.stopPropagation()}
              >
                <MoreVertical className="h-4 w-4 text-muted-foreground" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
