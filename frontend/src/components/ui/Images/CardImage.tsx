import React, { useEffect, useState, useRef } from "react";
import {
  Download,
  Trash2,
  Star,
  MoreVertical,
  Globe,
  Lock,
  StarOff,
  CodeXml,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/hooks/use-toast";

import { formatFileSize, formattedDate } from "@/components/utils/format";
import AccessControlModal from "../Modals/AccessControlModal";
import AssetsService from "@/components/api/assets.service";

export interface Asset {
  id: string | number;
  name: string;
  file_url: string;
  type?: string;
  size?: string;
  created_at?: string;
  path: string;
  is_private: boolean;
}

export interface ImageCardProps {
  asset;
  onClick;
  onDelete: (asset_id) => void;
  onDownload?: (asset: Asset) => void;
}

export default function ImageCard({
  asset,
  onClick,
  onDelete,
  onDownload,
}: ImageCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [openAccessModal, setOpenAccessModal] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [cardAsset, setCardAsset] = useState(asset);
  const { toast } = useToast();

  const [imageUrl, setImageUrl] = useState<string | null>(null);

  useEffect(() => {
    let objectUrl: string | null = null;

    const fetchAndSetImage = async () => {
      try {
        const res = await AssetsService.GetThumbnail(asset.id, {
          w: 500,
          h: 500,
        });

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
  const handleDownload = async () => {
    try {
      const res = await AssetsService.GetAsset(asset.path);
      const blob = res.data as Blob;
      const url = URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;

      // Lấy tên file hợp lý — có thể dùng cardAsset.display_name hoặc path
      const fileName =
        cardAsset.system_name ||
        cardAsset.path?.split("/").pop() ||
        `asset_${cardAsset.id}.${cardAsset.format}`;

      a.download = fileName;
      document.body.appendChild(a);
      a.click();

      // 5️⃣ Dọn dẹp
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
      alert("Failed to download image. Please try again.");
    }
  };

  const handleChangeAccessControl = async (is_private: boolean) => {
    try {
      await AssetsService.Update(cardAsset.id, { is_private: is_private });
      setCardAsset((prev: any) => ({ ...prev, is_private })); // cập nhật lại state ngay
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  const handleToggleStar = async (is_favorite: boolean) => {
    try {
      await AssetsService.Update(cardAsset.id, { is_favorite: is_favorite });
      setCardAsset((prev: any) => ({ ...prev, is_favorite })); // cập nhật lại state ngay
    } catch (err) {
      console.error("Toggle star failed", err);
    }
  };
  const handleCopy = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      toast({
        title: "Copied!",
        description: "Image URL copied to clipboard.",
      });
    } catch (err) {
      toast({ title: "Copy failed", description: "Could not copy URL." });
      console.error("Failed to copy: ", err);
    }
  };
  return (
    <Card
      key={cardAsset.id}
      onClick={onClick}
      className="group  overflow-hidden bg-card border border-gray-700 hover:border-primary/50 transition-all cursor-pointer"
    >
      <div className="relative aspect-video bg-muted overflow-hidden">
        <img
          src={imageUrl || "/placeholder.svg"}
          alt={cardAsset.name}
          className="w-full h-full object-cover"
        />
        {/* ✅ Nút ba chấm — đưa vào góc trên phải */}
        <div
          className="absolute top-2 right-2 z-10 transition-opacity"
          onClick={(e) => e.stopPropagation()}
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 shrink-0 bg-background/80 text-foreground hover:bg-background"
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="bg-popover border-border"
            >
              <DropdownMenuItem
                className="text-popover-foreground hover:bg-accent"
                onClick={handleDownload}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-popover-foreground hover:bg-accent"
                onClick={() => handleToggleStar(true)}
              >
                <Star className="h-4 w-4 mr-2" />
                Add to Starred
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive hover:bg-destructive/10"
                onClick={() => {
                  setIsDeleteDialogOpen(true);
                }}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <Button
            size="icon"
            variant="secondary"
            className="h-10 w-10 bg-background/90 hover:bg-background"
            onClick={(e) => {
              e.stopPropagation();
              handleDownload();
            }}
          >
            <Download size={30} />
          </Button>
          <Button
            size="icon"
            variant="secondary"
            onClick={(e) => {
              e.stopPropagation();
              handleToggleStar(!cardAsset.is_favorite);
            }}
            className="h-10 w-10 bg-background/90 hover:bg-background"
          >
            {cardAsset.is_favorite ? (
              <Star size={30} className="text-highlight" />
            ) : (
              <StarOff size={30} />
            )}
          </Button>
          <Button
            onClick={(e) => {
              e.stopPropagation();
              handleCopy(cardAsset.file_url);
            }}
            className="h-10 w-10 bg-background/90 hover:bg-background"
          >
            <CodeXml size={30} />
          </Button>
        </div>
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <div className="flex">
              <div className="text-sm font-medium text-foreground truncate mb-1 mr-5">
                {cardAsset.name}
              </div>
              <div className="text-sm font-medium text-foreground truncate mb-1 mr-5">
                {formatFileSize(cardAsset.file_size)}
              </div>
              <div className="text-sm font-medium text-foreground truncate mb-1">
                {cardAsset.width} x {cardAsset.height}
              </div>
            </div>
            <p className="text-sm ">{cardAsset.folder_path}</p>
            <div className="flex justify-between">
              <p className="text-sm flex items-center">
                {formattedDate(cardAsset.created_at)}
              </p>
              <div
                onClick={(e) => {
                  e.stopPropagation();
                  setOpenAccessModal(true);
                }}
              >
                {cardAsset.is_private ? (
                  <Button
                    size="icon"
                    variant="secondary"
                    className="h-10 w-10 hover:bg-background"
                  >
                    <Lock className="h-5 w-5 text-highlight " />
                  </Button>
                ) : (
                  <Button
                    size="icon"
                    variant="secondary"
                    className="h-10 w-10 hover:bg-background"
                  >
                    <Globe className="h-5 w-5 text-green-500 " />
                  </Button>
                )}
              </div>
            </div>
            <AccessControlModal
              open={openAccessModal}
              onClose={() => setOpenAccessModal(false)}
              onSave={handleChangeAccessControl}
              _is_private={cardAsset.is_private}
            />
          </div>
        </div>
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
              image &quot;{cardAsset?.name}&quot; and remove all associated API
              credentials.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.stopPropagation();
                onDelete(cardAsset.id);
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
