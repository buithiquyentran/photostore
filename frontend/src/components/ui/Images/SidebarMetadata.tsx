import { useState } from "react";
import AccessControlModal from "../Modals/AccessControlModal";
import { motion } from "framer-motion";
import { Globe, Lock } from "lucide-react";
import { formatFileSize, formattedDate } from "@/components/utils/format";
import TagInput from "@/components/ui/TagInput";
interface SidebarMetadataProps {
  open: boolean;
  meta: {
    id: number;
    folder_path: string;
    format: string;
    file_size: number;
    width: string;
    height: string;
    created_at: string;
    updated_at: string;
    name: string;
    system_name: string;
    is_private: boolean;
    tags: any[]
  };
  onsave: (is_private: boolean) => void;
}

export default function SidebarMetadata({
  open,
  meta,
  onsave,
}: SidebarMetadataProps) {
  const [openModal, setOpenModal] = useState(false);

  return (
    <motion.div
      initial={{ x: "100%" }}
      animate={{ x: open ? "0%" : "100%" }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className="top-0 right-0 h-full w-96 bg-gray-900 text-white shadow-xl z-50 flex flex-col overflow-y-auto"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
        <h2 className="text-lg font-semibold">Summary</h2>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4 overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-400 text-base">File name</p>
            <p className="font-medium">{meta?.name}</p>
          </div>
          <div>
            <p className="text-gray-400 text-base">Format</p>
            <p className="font-medium">{meta?.format}</p>
          </div>
          <div>
            <p className="text-gray-400 text-base">File size</p>
            <p className="font-medium">{formatFileSize(meta?.file_size)}</p>
          </div>
          <div>
            <p className="text-gray-400 text-base">Dimensions</p>
            <p className="font-medium">
              {meta?.width} x {meta?.height}
            </p>
          </div>
        </div>

        <div>
          <p className="text-gray-400 text-base">Created</p>
          <p className="font-medium">{formattedDate(meta?.created_at)}</p>
        </div>

        <div>
          <p className="text-gray-400 text-base">Last replaced</p>
          <p className="font-medium">{formattedDate(meta?.updated_at)}</p>
        </div>
        <div>
          <p className="text-gray-400 text-base">Location</p>
          <p className="font-medium">{meta?.folder_path}</p>
        </div>
        <div>
          <p className="text-gray-400 text-base">Public ID</p>
          <p className="font-medium">{meta?.system_name}</p>
        </div>
        <TagInput
          initialTags={meta?.tags.map((tag)=>({name: tag.name, id: tag.id}))}
          asset_id = {meta.id}
        />

        <div>
          <div className="flex items-center cursor-pointer">
            <div className="text-gray-400 text-base mr-2">Access control</div>
            <div
              className="px-2 py-1 rounded bg-gray-800 text-xs"
              onClick={() => setOpenModal(true)}
            >
              {meta?.is_private ? (
                <div className="flex items-center gap-1">
                  <Lock className="h-5 w-5 text-highlight" />{" "}
                  <span>Private</span>
                </div>
              ) : (
                <div className="flex items-center gap-1">
                  <Globe className="h-5 w-5 text-green-500" />{" "}
                  <span>Public</span>
                </div>
              )}
            </div>
          </div>
          <AccessControlModal
            open={openModal}
            onClose={() => setOpenModal(false)}
            onSave={onsave}
            _is_private={meta?.is_private}
          />
        </div>
      </div>
    </motion.div>
  );
}
