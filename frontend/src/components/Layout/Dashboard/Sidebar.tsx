import { useState, useEffect } from "react";
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
} from "lucide-react";
import AuthService from "@/components/services/auth.service";
import AssetService from "@/components/services/assets.service";
interface MenuItem {
  label: string;
  icon: React.ReactNode;
  count: number;
  subMenu?: string[];
}
export default function Sidebar() {
  const [openMenus, setOpenMenus] = useState<string[]>([]);
  const [username, setUsername] = useState<string | null>(null);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([
    {
      label: "Assets",
      icon: <Bookmark size={18} />,
      count: 0, // mặc định 0
      subMenu: ["Assets", "Projects", "Folders"],
    },
    { label: "Videos", icon: <Play size={18} />, count: 0 },
    { label: "People", icon: <User size={18} />, count: 0 },
    { label: "Favorites", icon: <Star size={18} />, count: 0 },
    { label: "Labels", icon: <Tag size={18} />, count: 0 },
  ]);
  useEffect(() => {
    const fetchCounts = async () => {
      try {
        const assetCount = await AssetService.Count();

        setMenuItems((prev) =>
          prev.map((item) =>
            item.label === "Assets" ? { ...item, count: assetCount } : item
          )
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
  const fetchUser = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      return;
    }

    try {
      const res = await AuthService.GetMe(token);
      setUsername(res.username);
    } catch (error) {
      console.error("Lỗi khi lấy thông tin user:", error);
    }
  };

  // chạy khi app load
  useEffect(() => {
    fetchUser();
  }, []);
  return (
    <div className="flex flex-col sticky top-0 h-screen justify-between  w-60 bg-headline text-main p-4  border border-gray-700">
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
                onClick={() => item.subMenu && toggleMenu(item.label)}
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
          <div className="border-t border-gray-700 pt-4 flex items-center gap-2">
            <div className="w-8 h-8 flex items-center justify-center rounded-full bg-yellow-500 text-black font-bold">
              {username
                ? (() => {
                    const parts = username.trim().split(" ");
                    if (parts.length === 1) return parts[0][0]?.toUpperCase();
                    return (
                      (parts[0][0]?.toUpperCase() || "") +
                      (parts[parts.length - 1][0]?.toUpperCase() || "")
                    );
                  })()
                : ""}
            </div>
            <span>{username}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
