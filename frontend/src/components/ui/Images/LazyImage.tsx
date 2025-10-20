import React, { useEffect, useState, useRef } from "react";
import AssetsService from "@/components/api/assets.service";
function LazyImage({ asset }: { asset: any }) {
  const [loaded, setLoaded] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const imgRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    let objectUrl: string | null = null;

    const fetchAndSetImage = async () => {
      try {
        const res = await AssetsService.GetAsset(asset.path);
        const blob = res.data as Blob;
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
        objectUrl = url;
      } catch (err) {
        console.error("Fetch image failed", err);
      }
    };

    fetchAndSetImage();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl); // cleanup tránh leak
    };
  }, [asset]);

  return (
    <div
      ref={imgRef}
      style={{ aspectRatio: `${asset.width} / ${asset.height}` }}
      className="bg-gray-700 overflow-hidden cursor-pointer"
    >
      {/* Placeholder mờ */}
      <div
        className={`w-full inset-0 bg-gray-800 transition-opacity duration-500 ${
          loaded ? "opacity-0" : "opacity-100"
        }`}
      />
      {imageUrl && (
        <img
          src={imageUrl}
          alt={asset.name}
          onLoad={() => setLoaded(true)}
          className={`w-full transition-opacity duration-700 ${
            loaded ? "opacity-100" : "opacity-0 blur-sm"
          }`}
        />
      )}
    </div>
  );
}
export default LazyImage;
