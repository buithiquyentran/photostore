import React, { use, useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, Star, Trash } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Globe, Lock, Folder } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { formatFileSize } from "@/components/utils/format";
import AssetThumbnail from "../Images/AssetThumbnail";
import AccessControlModal from "../Modals/AccessControlModal";
import AssetsService from "@/components/api/assets.service";

const ListView = ({ assets }) => {
  const navigate = useNavigate();
  const [openAccessModal, setOpenAccessModal] = useState(false);
  const [listAssets, setListAssets] = useState(assets);
  const [editAsset, setEditAsset] = useState(null);
  useEffect(() => {
    setListAssets(assets);
  }, [assets]);
  // ✅ State chọn nhiều ảnh
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  // 🧠 Toggle chọn 1 ảnh
  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  // 🧠 Toggle chọn tất cả
  const handleToggleSelectAll = () => {
    if (selectedIds.length === listAssets.length) setSelectedIds([]);
    else setSelectedIds(listAssets.map((a) => a.id));
  };

  // ⚙️ Đổi quyền truy cập
  const handleChangeAccessControl = async (is_private: boolean) => {
    try {
      if (!editAsset) return;
      await AssetsService.Update(editAsset.id, { is_private });
      setListAssets((prev) =>
        prev.map((a) => (a.id === editAsset.id ? { ...a, is_private } : a))
      );
    } catch (err) {
      console.error("Toggle access failed", err);
    }
  };

  // ⚙️ Hành động bulk
  const handleBulkStar = async () => {
    try {
      await Promise.all(
        selectedIds.map((id) => AssetsService.Update(id, { starred: true }))
      );
      setSelectedIds([]);
    } catch (err) {
      console.error("Star failed:", err);
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm("Delete selected assets?")) return;
    try {
      await Promise.all(selectedIds.map((id) => AssetsService.Delete(id)));
      setListAssets((prev) => prev.filter((a) => !selectedIds.includes(a.id)));
      setSelectedIds([]);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const handleBulkDownload = async () => {
    const selectedAssets = listAssets.filter((a) => selectedIds.includes(a.id));
    for (const asset of selectedAssets) {
      const link = document.createElement("a");
      link.href = asset.file_url;
      link.download = asset.display_name || "asset";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  useEffect(() => {
    if (editAsset) setOpenAccessModal(true);
  }, [editAsset]);

  return (
    <div className="divide-y divide-gray-700 text-gray-300">
      {/* ✅ Bulk Actions */}
      {selectedIds.length > 0 && (
        <div className="flex items-center justify-between bg-gray-800 p-3 rounded mb-4">
          <div className="text-sm text-gray-300">
            {selectedIds.length} selected
          </div>
          <div className="flex gap-2">
            <button
              className="px-3 py-1 rounded  hover:bg-yellow-600 text-white flex items-center"
              onClick={handleBulkStar}
            >
              <Star className="mr-2 h-4 w-4" /> <div>Star</div>
            </button>
            <button
              className="px-3 py-1 rounded  hover:bg-blue-600 text-white flex items-center"
              onClick={handleBulkDownload}
            >
              <Download className="mr-2 h-4 w-4 " /> <div>Download</div>
            </button>
            <button
              className="px-3 py-1 rounded  hover:bg-red-600 text-white flex items-center"
              onClick={handleBulkDelete}
            >
              <Trash className="mr-2 h-4 w-4" /> <div>Delete</div>
            </button>
          </div>
        </div>
      )}

      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent text-lg">
            <TableHead className="font-semibold text-white">
              <Checkbox
                checked={
                  selectedIds.length > 0 &&
                  selectedIds.length === listAssets.length
                }
                onCheckedChange={handleToggleSelectAll}
              />
            </TableHead>
            <TableHead className="font-semibold text-white">
              Display name
            </TableHead>
            <TableHead className="font-semibold text-white">
              Container folder
            </TableHead>
            <TableHead className="font-semibold text-white">
              Format
            </TableHead>
            <TableHead className="font-semibold text-white">
              Size
            </TableHead>
            <TableHead className="font-semibold text-white">
              Dimensions
            </TableHead>
            <TableHead className="font-semibold text-white min-w-[140px]">
              Access control
            </TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {listAssets.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="h-32 text-center">
                <p className="text-muted-foreground">
                  No projects yet. Create your first project to get started.
                </p>
              </TableCell>
            </TableRow>
          ) : (
            listAssets.map((asset) => (
              <TableRow
                key={asset.id}
                className="p-3 hover:bg-gray-800 cursor-pointer rounded text-base"
              >
                <TableCell>
                  <Checkbox
                    checked={selectedIds.includes(asset.id)}
                    onCheckedChange={() => handleToggleSelect(asset.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </TableCell>

                <TableCell className="font-medium">
                  <div onClick={() => navigate(`/photos/${asset.path}`)}>
                    <AssetThumbnail asset={asset} size={64} />
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex">
                    <Folder className="w-5 h-5 mr-2" />
                    <div>{asset.folder_path}</div>
                  </div>
                </TableCell>
                <TableCell>{asset.format}</TableCell>
                <TableCell>{formatFileSize(asset.file_size)}</TableCell>
                <TableCell>
                  {asset.width} x {asset.height}
                </TableCell>
                <TableCell>
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditAsset(asset);
                    }}
                  >
                    {asset.is_private ? (
                      <div className="flex">
                        <Lock className="h-5 w-5 text-highlight mr-2" />{" "}
                        Restricted
                      </div>
                    ) : (
                      <div className="flex">
                        <Globe className="h-5 w-5 text-green-500 mr-2" /> Public
                      </div>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>

      {editAsset && (
        <AccessControlModal
          open={openAccessModal}
          onClose={() => {
            setOpenAccessModal(false);
            setEditAsset(null);
          }}
          onSave={handleChangeAccessControl}
          _is_private={editAsset.is_private}
        />
      )}
    </div>
  );
};

export default ListView;
