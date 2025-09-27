import React, { useEffect, useState, useRef, use } from "react";
import Masonry from "react-masonry-css";
import AssetsService from "@/components/api/assets.service";
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
import { useOutletContext } from "react-router-dom";
import LazyImage from "@/components/ui/LazyImage";
type LayoutContext = { assets: any[] };
const Brower = () => {
  const { assets } = useOutletContext<LayoutContext>();
  const [view, setView] = useState("columns");

  const breakpointColumns = { default: 4, 1024: 3, 768: 2, 500: 1 };
  const changeView = (newView) => {
    setView(newView);
    if (onViewChange) onViewChange(newView);
  };
  return (
    <div className=" bg-[rgb(31,36,46)] min-h-full">
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
        {assets.map((asset) => (
          <LazyImage key={asset.id} asset={asset} />
        ))}
      </Masonry>
    </div>
  );
};

export default Brower;
