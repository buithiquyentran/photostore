import { Card, CardContent } from "@/components/ui/card";
import { FolderIcon, MoreVertical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

export default function FolderGrid({ folders }: { folders: any[] }) {
  const navigate = useNavigate();

  const handleOpenFolder = (slug: string) => {
    navigate(`/dashboard/${slug}`);
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
            onClick={() => handleOpenFolder(folder.slug)}
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
