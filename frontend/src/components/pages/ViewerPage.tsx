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
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/Modals/alert-dialog";
import AssetService from "@/components/api/assets.service";
import SidebarMetadata from "@/components/ui/Images/SidebarMetadata";
import path from "@/resources/path";
export default function ViewerPage() {
  const { "*": file_url } = useParams();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [meta, setMeta] = useState<any>(null);
  const [toggleStar, setToggleStar] = useState<any>(null);
  const [nextPath, setNextPath] = useState<string>();
  const [prevPath, setPrevPath] = useState<string>();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  useEffect(() => {
    let objectUrl: string | null = null;
    const fetchAndSetImage = async () => {
      try {
        if (!file_url) {
          console.error("No image path provided");
          alert(file_url);

          return;
        }

        const res = await AssetService.GetAsset(file_url);
        const blob = res.data as Blob;
        const url = URL.createObjectURL(blob);
        setImageUrl(url);

        const metaResponse = await AssetService.GetMetadata(file_url);
        setMeta(metaResponse);

        setToggleStar(metaResponse.is_favorite);
        objectUrl = url;
        const nextPreName = await AssetService.GetNextPre(file_url);
        setNextPath(nextPreName.next?.path);
        setPrevPath(nextPreName.prev?.path);
      } catch (err) {
        console.error("Fetch image failed", err);
      }
    };

    fetchAndSetImage();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl); // cleanup tránh leak
    };
  }, [file_url]);

  const handleDelete = async () => {
    try {
      await AssetService.Update(meta.id, { is_deleted: true });
    } catch (err) {
      console.error("Delete failed", err);
    }
  };
  const handleToggleStar = async () => {
    try {
      await AssetService.Update(meta.id, { is_favorite: !toggleStar });
      setToggleStar(!toggleStar);
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  const handleChangeAccessControl = async (is_private: boolean) => {
    try {
      await AssetService.Update(meta.id, { is_private: is_private });
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
          onClick={() => navigate(path.DASHBOARD)}
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
            // onClick={() => handleDelete()}
            onClick={() => {
              setIsDeleteDialogOpen(true);
            }}
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
                navigate(`/photos/${prevPath}`);
              }}
              disabled={!prevPath}
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
                navigate(`/photos/${nextPath}`);
              }}
              disabled={!nextPath}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the
              image &quot;{meta?.name}&quot; and remove all associated API
              credentials.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.stopPropagation();
                handleDelete();
                navigate(path.DASHBOARD);
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
