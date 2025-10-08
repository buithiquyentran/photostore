import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

import {
  Bookmark,
  Play,
  User,
  Star,
  Tag,
  Settings,
  Camera,
  UserPlus,
  Puzzle,
  HelpCircle,
  Key,
} from "lucide-react";
import UserService from "@/components/api/user.service";
import AssetService from "@/components/api/assets.service";
import LoginService from "@/components/api/login.service";
import path from "@/resources/path";

interface MenuItem {
  label: string;
  icon: React.ReactNode;
  count: number;
  subMenu?: string[];
  path?: string;
}
export default function Sidebar() {
  const [openMenus, setOpenMenus] = useState<string[]>([]);
  const [username, setUsername] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const navigate = useNavigate();

  const [menuItems, setMenuItems] = useState<MenuItem[]>([
    {
      label: "Assets",
      icon: <Bookmark size={18} />,
      count: 0, // mặc định 0
      subMenu: ["Projects", "Folders", "Assets"],
      path: path.BROWER,
    },
    { label: "Videos", icon: <Play size={18} />, count: 0 },
    { label: "People", icon: <User size={18} />, count: 0 },
    {
      label: "Favorites",
      icon: <Star size={18} />,
      count: 0,
      path: path.FAVORITE,
    },
    { label: "Labels", icon: <Tag size={18} />, count: 0 },
  ]);
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const assetCount = await AssetService.Count({
          is_deleted: false,
        });
        const favoriteCount = await AssetService.Count({
          is_favorite: true,
        });
        setMenuItems((prev) =>
          prev.map((item) => {
            switch (item.label) {
              case "Assets":
                return { ...item, count: assetCount };
              case "Favorites":
                return { ...item, count: favoriteCount };
              default:
                return item;
            }
          })
        );
      } catch (err) {
        console.error("Failed to fetch asset count:", err);
      }
    };

    fetchCounts();
  }, []);
  const toggleMenu = (label: string) => {
    setOpenMenus((prev) =>
      prev.includes(label) ? prev.filter((m) => m !== label) : [...prev, label]
    );
  };
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
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

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

    // keycloak.logout();
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
  return (
    <div className="flex flex-col sticky top-0 h-screen justify-between  w-60 bg-primary text-main p-4  border border-gray-700">
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

        {/* Menu items */}
        <nav>
          {menuItems.map((item) => (
            <div key={item.label} className="mb-2 text-white">
              <div
                className="flex p-4 space-y-2 items-center justify-between px-2 py-1 rounded-lg hover:text-highlight cursor-pointer"
                onClick={() => {
                  if (item.subMenu) toggleMenu(item.label);
                  if (item.path) navigate(item.path);
                }}
              >
                <div className="flex items-center gap-2">
                  {item.icon}
                  <span>{item.label}</span>
                </div>
                {item.count !== undefined && (
                  <span className="text-sm text-gray-400">{item.count}</span>
                )}
              </div>

              {/* Submenu */}
              {item.subMenu && openMenus.includes(item.label) && (
                <div className="ml-8 mt-1 space-y-1 text-sm text-gray-400">
                  {item.subMenu.map((sub, idx) => (
                    <div key={idx} className="hover:text-white cursor-pointer">
                      {sub}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>

      {/* Bottom storage bar */}
      <div>
        <div className="text-xs text-gray-400 mb-1">1 GB of 25 GB used</div>
        <div className="w-full bg-secondary h-2 rounded-full overflow-hidden mb-4">
          <div className="bg-purple-500 h-2 " style={{ width: "10%" }}></div>
        </div>
        <div className="flex flex-col space-y-6 text-white">
          <div className="flex items-center gap-4">
            <UserPlus className="w-6 h-6 cursor-pointer hover:text-blue-400" />
            <span>Invite new user</span>
          </div>
          <div className="flex items-center gap-4">
            <Puzzle className="w-6 h-6 cursor-pointer hover:text-blue-400" />
            <span>Add-on Marketplace</span>
          </div>
          <div className="flex items-center gap-4">
            <HelpCircle className="w-6 h-6 cursor-pointer hover:text-blue-400" />
            <span>Help</span>
          </div>
          <div className="flex items-center gap-4">
            <Settings className="w-6 h-6 cursor-pointer hover:text-blue-400" />
            <span>Settings</span>
          </div>
          <div
            // className="border-t border-gray-700 pt-4 flex items-center gap-2"
            onClick={toggleUser}
            className="flex items-center gap-2 cursor-pointer border-t border-gray-700 pt-4"
          >
            <div className="w-8 h-8 flex items-center justify-center rounded-full bg-yellow-500 text-black font-bold">
              {initials}
            </div>
            <span>{username}</span>
          </div>
          {open && (
            <div className="absolute left-14 bottom-0 bg-white shadow-lg rounded-md py-2 z-50">
              <div className="px-4 py-2 text-sm text-gray-700 border-b flex">
                <span className="font-bold"> Name: </span> {username}
              </div>
              <div className="px-4 py-2 text-sm text-gray-700 border-b flex">
                <span className="font-bold"> Email: </span> {email}
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
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
