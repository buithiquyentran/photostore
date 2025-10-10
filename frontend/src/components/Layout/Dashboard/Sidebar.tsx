import { useState, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  Bookmark,
  Play,
  User,
  Tag,
  Settings,
  Camera,
  UserPlus,
  Puzzle,
  HelpCircle,
  Key,
} from "lucide-react";
import UserService from "@/components/api/user.service";
import FolderService from "@/components/api/folder.service";
import LoginService from "@/components/api/login.service";
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
import path from "@/resources/path";

interface FolderNode {
  id: string;
  name: string;
  icon?: React.ReactNode;
  children?: FolderNode[];
  slug: string;
}

interface SidebarProps {
  selectedMenu: string;
  setSelectedMenu: (folderSlug: string) => void;
  setFolderPath: (folderPath: string) => void;
}
const quickAccess = [
  {
    id: "all",
    name: "All Files",
    icon: <Folder className="h-4 w-4" />,
    path: path.BROWER,
  },
  {
    id: "starred",
    name: "Starred",
    icon: <Star className="h-4 w-4" />,
    path: path.FAVORITE,
  },
  { id: "recent", name: "Recent", icon: <Clock className="h-4 w-4" /> },
  {
    id: "trash",
    name: "Trash",
    icon: <Trash2 className="h-4 w-4" />,
    path: path.TRASH,
  },
];
export default function Sidebar({
  selectedMenu,
  setSelectedMenu,
  setFolderPath,
}: SidebarProps) {
  const navigate = useNavigate();
  const [username, setUsername] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [folders, setFolders] = useState<FolderNode[] | null>([]);
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const response = await FolderService.GetAll();
        setFolders(response);
      } catch (err) {
        console.error("Failed to fetch asset count:", err);
      }
    };

    fetchCounts();
  }, []);
  const toggleUser = () => setOpen(!open);
  const fetchUser = async () => {
    try {
      const res = await UserService.GetMe();
      setUsername(res.current_user.username);
      setEmail(res.current_user.email);
    } catch (error) {
      console.error("Lỗi khi lấy thông tin user:", error);
    }
  };

  // chạy khi app load
  useEffect(() => {
    fetchUser();
  }, []);

  const handleLogout = async () => {
    const refreshToken = localStorage.getItem("refresh_token") || 1;
    if (refreshToken) {
      try {
        await LoginService.LogOut({ refresh_token: refreshToken });
      } catch (err) {
        console.error("Logout failed", err);
      }
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/login";
  };

  // Đóng dropdown khi click bên ngoài
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const initials = username
    ? (() => {
        const parts = username.trim().split(" ");
        if (parts.length === 1) return parts[0][0]?.toUpperCase();
        return (
          (parts[0][0]?.toUpperCase() || "") +
          (parts[parts.length - 1][0]?.toUpperCase() || "")
        );
      })()
    : "";

  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set([])
  );

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFolder = (folder: FolderNode, level = 0, parentPath = "") => {
    const isExpanded = expandedFolders.has(folder.id);
    const hasChildren = folder.children && folder.children.length > 0;
    const isSelected = selectedMenu === folder.id;

    const fullPath = parentPath ? `${parentPath}/${folder.slug}` : folder.slug;

    const handleOpenFolder = () => {
      // Nếu đã chọn rồi thì không load lại
      if (selectedMenu === folder.id) return;
      setFolderPath(fullPath);
      console.log(fullPath);
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
            {folder.children!.map((child) =>
              renderFolder(child, level + 1, fullPath)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col sticky top-0 h-screen justify-between w-60 bg-[#111827] p-4  border border-gray-700">
      {/* Top section */}
      <div>
        <div className="flex items-center justify-center gap-2 mb-8 underline underline-offset-4 decoration-4 decoration-highlight">
          <div>
            <Camera className="w-10 h-10 text-tertiary" />
          </div>
          <span className="font-semibold text-2xl text-tertiary">
            photostore
          </span>
        </div>
        <div className="flex-1 space-y-6">
          <div>
            <h2 className="text-base font-medium text-muted-foreground uppercase tracking-wider px-3 mb-2">
              Quick Access
            </h2>
            {quickAccess.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setSelectedMenu(item.id);
                  if (item.path) navigate(item.path);
                }}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-1.5 text-base rounded-md transition-colors",
                  "hover:bg-sidebar-accent text-sidebar-foreground",
                  selectedMenu === item.id &&
                    "bg-sidebar-accent text-sidebar-accent-foreground"
                )}
              >
                {item.icon}
                <span>{item.name}</span>
              </button>
            ))}
          </div>

          <div>
            <h2 className="text-base font-medium text-muted-foreground uppercase tracking-wider px-3 mb-2">
              Projects
            </h2>
            <div className="space-y-0.5">
              {folders?.map((folder) => renderFolder(folder))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom storage bar */}

      <div className="border-t border-gray-700 pt-4">
        <div className="text-base text-gray-400 mb-1">2 GB of 10 GB used</div>
        <div className=" flex w-full bg-secondary h-2 rounded-full overflow-hidden mb-4">
          <div className="bg-purple-500 h-2 " style={{ width: "20%" }}></div>
          <div className="bg-black h-2 " style={{ width: "80%" }}></div>
        </div>
        <div className="flex flex-col space-y-6 text-white">
          <div className="flex items-center gap-4  cursor-pointer hover:text-blue-400">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </div>
          <div
            onClick={toggleUser}
            className="flex items-center gap-2 cursor-pointer"
          >
            <div className="w-8 h-8 flex items-center justify-center rounded-full bg-yellow-500 text-black font-bold">
              {initials}
            </div>
            <span>{username}</span>
          </div>
          {open && (
            <div className="absolute left-14 bottom-0 bg-white shadow-lg rounded-md py-2 z-50">
              <div className="px-4 py-2 text-base text-gray-700 border-b flex">
                <span className="font-bold"> Name: </span> {username}
              </div>
              <div className="px-4 py-2 text-base text-gray-700 border-b flex">
                <span className="font-bold"> Email: </span> {email}
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-base text-red-600 hover:bg-gray-100"
              >
                Đăng xuất
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
