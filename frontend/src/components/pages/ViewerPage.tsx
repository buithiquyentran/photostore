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
          className="p-2 rounded-full hover:bg-white/20 text-white"
        >
          <X size={24} />
        </button>
        <div className="flex items-center justify-between bg-black/50 ">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white"
          >
            <Share2 size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white"
          >
            <SlidersHorizontal size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 m-2 rounded-full hover:bg-white/20 text-white"
          >
            <ZoomIn size={24} />
          </button>
          <button
            onClick={() => handleToggleStar()}
            className="p-2 rounded-full hover:bg-white/20 text-white"
          >
            {toggleStar ? <Star size={24} className="text-highlight" /> : <StarOff size={24} />}
          </button>
          <button
            onClick={() => handleDelete()}
            className="p-2 rounded-full hover:bg-white/20 text-white"
          >
            <Trash2 size={24} />
          </button>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-full hover:bg-white/20 text-white"
          >
            <Info size={24} />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Ảnh */}
        <div className="flex-1 flex items-center justify-center overflow-hidden">
          {imageUrl && (
            <img
              src={imageUrl || ""}
              alt="meta.name"
              className="max-h-full max-w-full object-contain"
            />
          )}
        </div>

        {/* Sidebar */}
        {sidebarOpen && <SidebarMetadata open={sidebarOpen} meta={meta} onsave ={handleChangeAccessControl}/>}
      </div>
    </div>
  );
}
