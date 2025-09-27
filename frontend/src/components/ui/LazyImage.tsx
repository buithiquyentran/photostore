import React, { useEffect, useState, useRef } from "react";
import AssetsService from "@/components/api/assets.service";

function LazyImage({ asset }: { asset: any }) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef<HTMLDivElement | null>(null);

  const token = localStorage.getItem("access_token");
  const fetchImage = async () => {
    const res = await fetch(asset.url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    console.log(res.url);
    if (!res.ok) throw new Error("Failed to fetch image");
    const blob = await res.blob();
    setImageUrl(URL.createObjectURL(blob));
    // setImageUrl(res.url);
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      async (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting) {
          // Gọi API để lấy signed url
          try {
            // const url = await AssetsService.GetOne(asset.id);
            // console.log(url);
            if (!asset.is_private) {
              setImageUrl(asset.url);
            } else fetchImage();
          } catch (err) {
            console.error("Error fetching signed url", err);
          } finally {
            observer.disconnect(); // ngắt sau khi load
          }
        }
      },
      { threshold: 0.2 } // load khi 20% ảnh vào viewport
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, []);

  return (
    <div
      ref={imgRef}
      style={{ aspectRatio: `${asset.width} / ${asset.height}` }}
      className="bg-gray-700 overflow-hidden"
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
