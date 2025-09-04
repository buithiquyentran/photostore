import React, { useEffect, useState } from "react";
import Masonry from "react-masonry-css";
import AssetsService from "@/components/services/assets.service";
import AdvancedSearchBar from "@/components/ui/AdvancedSearchBar";
import {
  Search,
  Upload,
  Filter,
  LayoutGrid,
  LayoutList,
  Columns,
  MoreVertical,
  RotateCcw,
} from "lucide-react";
import SortDropdown from "@/components/ui/SortDropdown";
const Brower = () => {
  const [assets, setAssets] = React.useState<any[]>([]);
  const [view, setView] = useState("columns");

  const fetchAssets = async () => {
    try {
      const pubic_assets = await AssetsService.GetPublicAssets();
      const user_assets = await AssetsService.GetAll();
      const response = [...pubic_assets, ...user_assets];
      setAssets(response);
      console.log(response);
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  };
  // chạy khi app load
  useEffect(() => {
    fetchAssets();
  }, []);
  const breakpointColumns = { default: 4, 1024: 3, 768: 2, 500: 1 };
  const changeView = (newView) => {
    setView(newView);
    if (onViewChange) onViewChange(newView);
  };
  interface DropdownProps {
    label: string;
    options: string[];
    onChange: (value: string) => void;
  }

  function Dropdown({ label, options, onChange }: DropdownProps) {
    return (
      <select
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm"
      >
        <option value="">{label}</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div>
      <div className=" bg-[rgb(31,36,46)]">
        <div className="flex items-center justify-between px-4 border-b border-gray-700 text-white ">
          <button className="flex  items-center text-gray-400  hover:text-white px-2">
            <RotateCcw size={20} /> &nbsp;{" "}
            <div className="text-sm "> Refresh </div>
          </button>
          <div className="flex items-center gap-4">
            {/* Sort */}

            <SortDropdown />
            {/* View toggle */}
            <div className=" items-center p-1 shadow-md flex flex-wrap  gap-3 ">
              <button
                onClick={() => changeView("grid")}
                className={`p-2 rounded-full ${
                  view === "grid"
                    ? "text-highlight"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <LayoutGrid size={20} />
              </button>
              <button
                // onClick={() => changeView("list")}
                className={`p-2 rounded-full ${
                  view === "list"
                    ? "text-highlight"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <LayoutList size={20} />
              </button>

              <button
                // onClick={() => changeView("columns")}
                className={`p-2 rounded-full ${
                  view === "columns"
                    ? "text-highlight"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                <Columns size={20} />
              </button>
            </div>
          </div>
        </div>
        <Masonry
          breakpointCols={breakpointColumns}
          className="flex gap-4 px-4"
          columnClassName="flex flex-col gap-4"
        >
          {assets?.map((asset, index) => (
            <img key={index} src={asset.url} className="w-full" />
          ))}
        </Masonry>
      </div>
    </div>
  );
};

export default Brower;
