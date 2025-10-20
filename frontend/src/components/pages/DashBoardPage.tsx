import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import AssetsService from "@/components/api/assets.service";
import {
  RotateCcw,
  LayoutDashboard,
  LayoutList,
  LayoutGrid,
} from "lucide-react";
import SortDropdown from "@/components/ui/SortDropdown";

import MosaicView from "@/components/ui/View/MosaicView";
import ListView from "@/components/ui/View/ListView";
import CardView from "@/components/ui/View/CardView";

const Brower = () => {
  const navigate = useNavigate();
  const [view, setView] = useState<"mosaic" | "list" | "card">("mosaic");
  const [assets, setAssets] = useState<any[]>([]);

  const fetchAssets = async () => {
    try {
      const user_assets = await AssetsService.GetAll({ is_deleted: false });
      setAssets(user_assets);
    } catch (error) {
      console.error("Error fetching assets:", error);
    }
  };

  useEffect(() => {
    fetchAssets();
  }, []);
  const handleDelete = async (asset_id) => {
    try {
      await AssetsService.Update(asset_id, { is_deleted: true });
      //  setCardAsset((prev: any) => ({ ...prev, is_deleted: true })); // cập nhật lại state ngay
      setAssets((prev) => prev.filter((p) => p.id !== asset_id));
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  const renderView = () => {
    switch (view) {
      case "list":
        return (
          <ListView
            assets={assets}
            // onSelect={(a) => navigate(`/photos/${a.path}`)}
          />
        );
      case "card":
        return (
          <CardView
            assets={assets}
            onSelect={(a) => navigate(`/photos/${a.path}`)}
            onDelete={handleDelete}
          />
        );
      default:
        return (
          <MosaicView
            assets={assets}
            onSelect={(a) => navigate(`/photos/${a.path}`)}
          />
        );
    }
  };

  return (
    <div className="bg-[rgb(31,36,46)] min-h-full">
      <div className="flex items-center justify-between px-4 border-b border-gray-700 text-white">
        <button
          onClick={fetchAssets}
          className="flex items-center text-gray-400 hover:text-white px-2"
        >
          <RotateCcw size={20} /> &nbsp;
          <span className="text-sm">Refresh</span>
        </button>

        <div className="flex items-center gap-4">
          <SortDropdown />
          <div className="flex gap-3 p-1 shadow-md">
            <button
              onClick={() => setView("mosaic")}
              className={`p-2 rounded-full ${
                view === "mosaic"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutDashboard size={20} />
            </button>
            <button
              onClick={() => setView("list")}
              className={`p-2 rounded-full ${
                view === "list"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutList size={20} />
            </button>
            <button
              onClick={() => setView("card")}
              className={`p-2 rounded-full ${
                view === "card"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutGrid size={20} />
            </button>
          </div>
        </div>
      </div>

      <div className="p-4">{renderView()}</div>
    </div>
  );
};

export default Brower;
