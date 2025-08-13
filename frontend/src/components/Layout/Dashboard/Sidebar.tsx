import { useState } from "react";
import {
  Search,
  Bookmark,
  Play,
  User,
  Star,
  MapPin,
  Calendar,
  Film,
  Tag,
  Folder,
  Library,
  Settings,
  Camera,
} from "lucide-react";

interface MenuItem {
  label: string;
  icon: React.ReactNode;
  count?: number;
  subMenu?: string[];
}
export default function Sidebar() {
  const [openMenus, setOpenMenus] = useState<string[]>([]);

  const menuItems: MenuItem[] = [
    { label: "Search", icon: <Search size={18} />, count: 151 },
    {
      label: "Albums",
      icon: <Bookmark size={18} />,
      count: 3,
      subMenu: ["Album 1", "Album 2"],
    },
    { label: "Media", icon: <Play size={18} />, count: 8 },
    { label: "People", icon: <User size={18} /> },
    { label: "Favorites", icon: <Star size={18} />, count: 2 },
    { label: "Places", icon: <MapPin size={18} />, count: 51 },
    { label: "Calendar", icon: <Calendar size={18} />, count: 50 },
    { label: "Moments", icon: <Film size={18} />, count: 4 },
    { label: "Labels", icon: <Tag size={18} />, count: 35 },
    { label: "Folders", icon: <Folder size={18} />, count: 24 },
    { label: "Library", icon: <Library size={18} /> },
    { label: "Settings", icon: <Settings size={18} /> },
  ];

  const toggleMenu = (label: string) => {
    setOpenMenus((prev) =>
      prev.includes(label) ? prev.filter((m) => m !== label) : [...prev, label]
    );
  };

  return (
    <div className="flex flex-col justify-between h-screen w-60 bg-headline text-main p-4">
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
            <div key={item.label} className="mb-2">
              <div
                className="flex items-center justify-between px-2 py-1 rounded-lg hover:bg-gray-800 cursor-pointer"
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
        <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
          <div className="bg-purple-500 h-2" style={{ width: "10%" }}></div>
        </div>
      </div>
    </div>
  );
}
