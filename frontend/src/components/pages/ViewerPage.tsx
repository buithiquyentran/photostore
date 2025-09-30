import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  X,
  Share2,
  SlidersHorizontal,
  ZoomIn,
  Info,
  Star,
  StarOff,
  Trash2,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import AssetService from "@/components/api/assets.service";
import UserService from "@/components/api/user.service";
import SidebarMetadata from "@/components/ui/SidebarMetadata";

export default function ViewerPage() {
  const { name } = useParams();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [meta, setMeta] = useState<any>(null);
  const [toggleStar, setToggleStar] = useState<any>(null);
  const [nextName, setNextName] = useState<string>();
  const [prevName, setPrevName] = useState<string>();

  useEffect(() => {
    let objectUrl: string | null = null;

    const fetchAndSetImage = async () => {
      try {
        const res = await AssetService.GetOne(name);
        const metaResponse = await UserService.GetMetadata(name);
        setMeta(metaResponse);
        const blob = res.data as Blob;
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
        setToggleStar(metaResponse.is_favorite);
        objectUrl = url;
        const nextPreName = await UserService.GetNextPre(name);
        setNextName(nextPreName.next?.name);
        setPrevName(nextPreName.prev?.name);
      } catch (err) {
        console.error("Fetch image failed", err);
      }
    };

    fetchAndSetImage();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl); // cleanup tránh leak
    };
  }, [name]);

  const handleDelete = async () => {
    try {
      await UserService.Update(meta.id, { is_deleted: true });
    } catch (err) {
      console.error("Delete failed", err);
    }
  };
  const handleToggleStar = async () => {
    try {
      await UserService.Update(meta.id, { is_favorite: !toggleStar });
      setToggleStar(!toggleStar);
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  const handleChangeAccessControl = async (is_private: boolean) => {
    try {
      await UserService.Update(meta.id, { is_private: is_private });
      setMeta((prev: any) => ({ ...prev, is_private })); // cập nhật lại state ngay
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  return (
    <div className="fixed inset-0 bg-black flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between bg-black/50 px-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
        >
          <X size={24} />
        </button>
        <div className="flex items-center justify-between bg-black/50 ">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            <Share2 size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            <SlidersHorizontal size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            <ZoomIn size={24} />
          </button>
          <button
            onClick={() => handleToggleStar()}
            className="p-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            {toggleStar ? (
              <Star size={24} className="text-highlight" />
            ) : (
              <StarOff size={24} />
            )}
          </button>
          <button
            onClick={() => handleDelete()}
            className="p-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            <Trash2 size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-full hover:bg-white/20 text-white cursor-pointer"
          >
            <Info size={24} />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Ảnh */}
        <div className="flex-1 flex items-center justify-center overflow-hidden">
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Nút Prev */}
            <button
              onClick={() => {
                navigate(`/photos/${prevName}`);
              }}
              disabled={!prevName}
              className="absolute left-4 top-[50%] p-3 bg-white/20 hover:bg-white/40 rounded-full text-white disabled:opacity-0 "
            >
              <ChevronLeft size={32} />
            </button>
            {imageUrl && (
              <img
                src={imageUrl || ""}
                alt="meta.name"
                className="max-h-full max-w-full object-contain"
              />
            )}
            {/* Nút Next */}
            <button
              onClick={() => {
                navigate(`/photos/${nextName}`);
              }}
              disabled={!nextName}
              className="absolute right-4 top-[50%] p-3 bg-white/20 hover:bg-white/40 rounded-full text-white disabled:opacity-0"
            >
              <ChevronRight size={32} />
            </button>
          </div>
        </div>

        {/* Sidebar */}
        {sidebarOpen && (
          <SidebarMetadata
            open={sidebarOpen}
            meta={meta}
            onsave={handleChangeAccessControl}
          />
        )}
      </div>
    </div>
  );
}
