"use client";

import type React from "react";

import { useState } from "react";
import {
  ChevronRight,
  ChevronDown,
  Folder,
  Star,
  Clock,
  Trash2,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
}

interface SidebarProps {
  selectedFolder: string;
  onFolderSelect: (folderId: string) => void;
}

export default function Sidebar({ selectedFolder, onFolderSelect }: SidebarProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set(["projects", "my-project"])
  );

  const folders: FolderNode[] = [
    {
      id: "projects",
      name: "Projects",
      children: [
        {
          id: "my-project",
          name: "My Project",
          children: [
            { id: "designs", name: "Designs" },
            { id: "marketing", name: "Marketing" },
            { id: "assets", name: "Assets" },
          ],
        },
        {
          id: "client-work",
          name: "Client Work",
          children: [
            { id: "branding", name: "Branding" },
            { id: "web-design", name: "Web Design" },
          ],
        },
      ],
    },
  ];

  const quickAccess = [
    { id: "all", name: "All Files", icon: <Folder className="h-4 w-4" /> },
    { id: "starred", name: "Starred", icon: <Star className="h-4 w-4" /> },
    { id: "recent", name: "Recent", icon: <Clock className="h-4 w-4" /> },
    { id: "trash", name: "Trash", icon: <Trash2 className="h-4 w-4" /> },
  ];

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFolder = (folder: FolderNode, level = 0) => {
    const isExpanded = expandedFolders.has(folder.id);
    const hasChildren = folder.children && folder.children.length > 0;
    const isSelected = selectedFolder === folder.id;

    return (
      <div key={folder.id}>
        <button
          onClick={() => {
            if (hasChildren) {
              toggleFolder(folder.id);
            }
            onFolderSelect(folder.id);
          }}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-1.5 text-sm rounded-md transition-colors",
            "hover:bg-sidebar-accent text-sidebar-foreground",
            isSelected && "bg-sidebar-accent text-sidebar-accent-foreground",
            level > 0 && "ml-4"
          )}
          style={{ paddingLeft: `${level * 12 + 12}px` }}
        >
          {hasChildren &&
            (isExpanded ? (
              <ChevronDown className="h-4 w-4 shrink-0" />
            ) : (
              <ChevronRight className="h-4 w-4 shrink-0" />
            ))}
          {!hasChildren && <div className="w-4" />}
          <Folder className="h-4 w-4 shrink-0" />
          <span className="truncate">{folder.name}</span>
        </button>
        {hasChildren && isExpanded && (
          <div className="mt-0.5">
            {folder.children!.map((child) => renderFolder(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <aside className="w-64 bg-sidebar border-r border-sidebar-border flex flex-col shrink-0">
      <div className="h-14 border-b border-sidebar-border flex items-center justify-between px-4">
        <h1 className="font-semibold text-sidebar-foreground text-lg">
          File Manager
        </h1>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        <div>
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3 mb-2">
            Quick Access
          </h2>
          <div className="space-y-0.5">
            {quickAccess.map((item) => (
              <button
                key={item.id}
                onClick={() => onFolderSelect(item.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-1.5 text-sm rounded-md transition-colors",
                  "hover:bg-sidebar-accent text-sidebar-foreground",
                  selectedFolder === item.id &&
                    "bg-sidebar-accent text-sidebar-accent-foreground"
                )}
              >
                {item.icon}
                <span>{item.name}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3 mb-2">
            Folders
          </h2>
          <div className="space-y-0.5">
            {folders.map((folder) => renderFolder(folder))}
          </div>
        </div>
      </div>

      <div className="p-3 border-t border-sidebar-border">
        <div className="bg-sidebar-accent rounded-lg p-3">
          <p className="text-xs text-sidebar-foreground font-medium mb-1">
            Storage
          </p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-sidebar rounded-full overflow-hidden">
              <div className="h-full bg-primary w-2/3" />
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            6.2 GB of 10 GB used
          </p>
        </div>
      </div>
    </aside>
  );
}
