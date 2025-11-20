import { UploadCloud } from "lucide-react";
interface UploadButtonProps {
  onUpload: (e: React.ChangeEvent<HTMLInputElement> | File[]) => void;
}

export default function UploadButton({ onUpload }: UploadButtonProps) {
  return (
    <label className=" flex items-center cursor-pointer gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md shadow-md transition">
      <input
        type="file"
        multiple
        accept="image/*"
        onChange={onUpload}
        className="hidden"
      />
      <UploadCloud size={18} />
      <span>Upload</span>
    </label>
  );
}
