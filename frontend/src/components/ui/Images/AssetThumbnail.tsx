import { useEffect, useState } from "react";
import { Skeleton } from "@/components/ui/skeleton"; // shadcn skeleton nếu có
import AssetsService from "@/components/api/assets.service";



const AssetThumbnail = ({ asset, size = 48 }) => {
  const [imgUrl, setImgUrl] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;

    const fetchImage = async () => {
      try {
        if (!asset?.path) return;
        setLoading(true);

        // ✅ check cache trước khi fetch
        // if (typeof window !== "undefined") {
        //   const cacheKey = `asset-cache-${asset.path}`;
        //   const cached = sessionStorage.getItem(cacheKey);
        //   if (cached && isMounted) {
        //     setImgUrl(cached);
        //     setLoading(false);
        //     return;
        //   }
        // }

        const res = await AssetsService.GetAsset(asset.path); 
        const blob = res.data as Blob;
        const url = URL.createObjectURL(blob);

        if (isMounted) {
          setImgUrl(url);
          setLoading(false);

          // if (typeof window !== "undefined") {
          //   sessionStorage.setItem(`asset-cache-${asset.path}`, url);
          // }
        }
      } catch (err) {
        console.error("Fetch image failed:", err);
        setLoading(false);
      }
    };


    fetchImage();

    return () => {
      isMounted = false;
    };
  }, [asset]);

  return (
    <div className="flex items-center">
      <div
        className="mr-3 rounded overflow-hidden bg-muted flex-shrink-0"
        style={{ width: size, height: size }}
      >
        {loading ? (
          <Skeleton className="w-full h-full" />
        ) : (
          <img
            src={imgUrl || "/placeholder.png"}
            alt={asset.name}
            className="object-cover w-full h-full"
            loading="lazy"
          />
        )}
      </div>

      <div className="truncate max-w-[200px] text-sm text-foreground">
        {asset.name}
      </div>
    </div>
  );
};

export default AssetThumbnail;
