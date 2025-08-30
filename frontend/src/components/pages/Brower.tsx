import React, { useEffect } from "react";
import AsssetService from "../util/photostore.api";

const Brower = () => {
  const [assets, setAssets] = React.useState<any[]>([]);
  const fetchAssets = async () => {
    try {
      const response = await AsssetService.GetAllAssets();
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
  return (
    <div className="columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4">
      {assets?.map((src, idx) => (
        <img
          key={idx}
          src={src}
          alt=""
          className="w-full mb-4 break-inside-avoid rounded-lg shadow"
        />
      ))}
    </div>
  );
};

export default Brower;
