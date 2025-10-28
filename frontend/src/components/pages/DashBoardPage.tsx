import { useEffect, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import AssetsService from "@/components/api/assets.service";

import MosaicView from "@/components/ui/View/MosaicView";
import ListView from "@/components/ui/View/ListView";
import CardView from "@/components/ui/View/CardView";
import empty_message_image from "@/assets/empty_message.png";

const Brower = () => {
  const navigate = useNavigate();
  const { assetsOutlet, view, setFolderPath } = useOutletContext();
  const [assets, setAssets] = useState<any[]>([]);
  useEffect(() => {
    setFolderPath("home");
    setAssets(assetsOutlet);
  }, [assetsOutlet, view, setFolderPath]);

  const handleDelete = async (asset_id) => {
    try {
      await AssetsService.Update(asset_id, { is_deleted: true });
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
      {assets.length > 0 ? (
        renderView()
      ) : (
        <div className=" text-gray-400 text-xl flex flex-col items-center gap-4">
          <img
            src={empty_message_image}
            alt={"empty-state.png"}
            className="flex justify-center"
          />

          <div>
            Try adjusting your search or filter to find what you're looking for
          </div>
        </div>
      )}
    </div>
  );
};

export default Brower;
