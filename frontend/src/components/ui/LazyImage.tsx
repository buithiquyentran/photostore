import React, { useEffect, useState, useRef } from "react";
import AssetsService from "@/components/services/assets.service";

function LazyImage({ asset }: { asset: any }) {
  const [signedUrl, setSignedUrl] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      async (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting) {
          // Gọi API để lấy signed url
          try {
            const signed_url = await AssetsService.GetSignedUrl(asset.id);
            setSignedUrl(signed_url);
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
  }, [asset.id]);

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
      {signedUrl && (
        <img
          src={signedUrl}
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
