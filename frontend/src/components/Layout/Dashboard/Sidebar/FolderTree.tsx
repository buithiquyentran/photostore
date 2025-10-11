import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronRight, ChevronDown, Folder } from "lucide-react";
import { cn } from "@/lib/utils";

interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug: string;
}

interface FolderTreeProps {
  folders: FolderNode[] | null;
  selectedMenu: string;
  setSelectedMenu: (id: string) => void;
  setFolderPath: (path: string) => void;
}

export default function FolderTree({
  folders,
  selectedMenu,
  setSelectedMenu,
  setFolderPath,
}: FolderTreeProps) {
  const navigate = useNavigate();
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) newExpanded.delete(folderId);
    else newExpanded.add(folderId);
    setExpandedFolders(newExpanded);
  };

  const renderFolder = (folder: FolderNode, level = 0, parentPath = "") => {
    const isExpanded = expandedFolders.has(folder.id);
    const hasChildren = folder.children && folder.children.length > 0;
    const isSelected = selectedMenu === folder.id;
    const fullPath = parentPath ? `${parentPath}/${folder.slug}` : folder.slug;

    const handleOpenFolder = () => {
      if (selectedMenu === folder.id) return;
      setFolderPath(fullPath);
      navigate(`/dashboard/${fullPath}`);
      setSelectedMenu(folder.id);
    };

    return (
      <div key={folder.id}>
        <button
          onClick={() => {
            if (hasChildren) toggleFolder(folder.id);
            if (folder.slug) handleOpenFolder();
          }}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-1.5 text-base rounded-md transition-colors",
            "hover:bg-sidebar-accent text-sidebar-foreground",
            isSelected && "bg-sidebar-accent text-sidebar-accent-foreground",
            level > 0 && "ml-4"
          )}
          style={{ paddingLeft: `${level * 12 + 12}px` }}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 shrink-0" />
            ) : (
              <ChevronRight className="h-4 w-4 shrink-0" />
            )
          ) : (
            <div className="w-4" />
          )}
          <Folder className="h-4 w-4 shrink-0" />
          <span className="truncate">{folder.name}</span>
        </button>

        {hasChildren && isExpanded && (
          <div className="mt-0.5">
            {folder.children!.map((child) =>
              renderFolder(child, level + 1, fullPath)
            )}
          </div>
        )}
      </div>
    );
  };

  return <div className="space-y-0.5">{folders?.map((f) => renderFolder(f))}</div>;
}
