import React from "react";
import Masonry from "react-masonry-css";
import LazyImage from "../Images/LazyImage";

const MosaicView = ({ assets, onSelect }) => {
  const breakpointColumns = { default: 4, 1024: 3, 768: 2, 500: 1 };

  return (
    <Masonry
      breakpointCols={breakpointColumns}
      className="flex gap-4"
      columnClassName="flex flex-col gap-4"
    >
      {assets?.map((asset) => (
        <div
          key={asset.id}
          onClick={() => onSelect(asset)}
          className="cursor-pointer hover:opacity-80 transition"
        >
          <LazyImage asset={asset} />
        </div>
      ))}
    </Masonry>
  );
};

export default MosaicView;
