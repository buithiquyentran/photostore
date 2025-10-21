
import { useEffect, useState } from "react";

import { useNavigate, useOutletContext } from "react-router-dom";

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
    <div className=" bg-[rgb(31,36,46)] min-h-full">
      <div className="p-4">{renderView()}</div>
    </div>
  );
};

export default Brower;
