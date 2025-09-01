import { UploadCloud } from "lucide-react";

interface UploadButtonProps {
  onClick: () => void;
}

export default function UploadButton({ onClick }: UploadButtonProps) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md shadow-md transition"
    >
      <UploadCloud size={18} />
      <span>Upload</span>
    </button>
  );
}
