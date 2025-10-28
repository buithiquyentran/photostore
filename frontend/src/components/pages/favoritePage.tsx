
import { useEffect, useState } from "react";

import { useNavigate, useOutletContext } from "react-router-dom";
import empty_message_image from "@/assets/empty_message.png";

import MosaicView from "@/components/ui/View/MosaicView";
import ListView from "@/components/ui/View/ListView";
import CardView from "@/components/ui/View/CardView";
const Brower = () => {
  const { assetsOutlet, view, setFolderPath } = useOutletContext();
  const [assets, setAssets] = useState<any[]>(assetsOutlet);
  const navigate = useNavigate();

  useEffect(() => {
    setFolderPath("favorite");
    setAssets(assetsOutlet);
  }, [assetsOutlet, view, setFolderPath]);
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
              // onDelete={handleDelete}
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
