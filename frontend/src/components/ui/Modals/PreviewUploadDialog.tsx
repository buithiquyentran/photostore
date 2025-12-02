import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Upload, X, FileImage } from "lucide-react";

interface PreviewUploadDialogProps {
  files: File[];
  open: boolean;
  onClose: () => void;
  onConfirm: (files: File[], isPrivate: boolean) => void;
}

export default function PreviewUploadDialog({
  files,
  open,
  onClose,
  onConfirm,
}: PreviewUploadDialogProps) {
  const [previews, setPreviews] = useState<string[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>(files);
  const [isPrivate, setIsPrivate] = useState(false);

  useEffect(() => {
    if (files.length > 0) {
      setSelectedFiles(files);
      // Create preview URLs
      const urls = files.map((file) => URL.createObjectURL(file));
      setPreviews(urls);

      // Cleanup function
      return () => {
        urls.forEach((url) => URL.revokeObjectURL(url));
      };
    }
  }, [files]);

  const handleRemoveFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);

    // Revoke the removed preview URL
    if (previews[index]) {
      URL.revokeObjectURL(previews[index]);
    }
    const newPreviews = previews.filter((_, i) => i !== index);
    setPreviews(newPreviews);
  };

  const handleConfirm = () => {
    onConfirm(selectedFiles, isPrivate);
    setIsPrivate(false); // Reset after upload
    onClose();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[700px] max-h-[100vh] p-0 overflow-hidden bg-white border-gray-700">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r bg-[#4172dc] px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-white text-xl font-semibold flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Review Files Before Upload ({selectedFiles.length}{" "}
              {selectedFiles.length === 1 ? "file" : "files"})
            </DialogTitle>
          </DialogHeader>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4 bg-white/5 overflow-y-auto max-h-[50vh]">
          {selectedFiles.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileImage className="h-12 w-12 mx-auto mb-2 text-gray-400" />
              <p>No files selected</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
              {selectedFiles.map((file, index) => (
                <div
                  key={index}
                  className="relative group border border-gray-300 rounded overflow-hidden bg-white hover:border-blue-500 transition-all"
                >
                  {/* Preview Image */}
                  <div className="aspect-square bg-gray-100 flex items-center justify-center overflow-hidden">
                    {previews[index] ? (
                      <img
                        src={previews[index]}
                        alt={file.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <FileImage className="h-8 w-8 text-gray-400" />
                    )}
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemoveFile(index)}
                    className="absolute top-2 right-2 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full text-white flex items-center justify-center shadow-lg transition-all duration-200 hover:scale-110 opacity-0 group-hover:opacity-100"
                    title="Remove file"
                  >
                    <X size={14} />
                  </button>

                  {/* File Info */}
                  <div className="p-2 bg-white border-t border-gray-200">
                    <p
                      className="text-xs font-medium text-gray-900 truncate"
                      title={file.name}
                    >
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Summary */}
        {selectedFiles.length > 0 && (
          <div className="px-6 py-3 bg-blue-50 border-t border-blue-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-700">
                Total: <strong>{selectedFiles.length}</strong> file(s)
              </span>
              <span className="text-gray-700">
                Size:{" "}
                <strong>
                  {formatFileSize(
                    selectedFiles.reduce((acc, file) => acc + file.size, 0)
                  )}
                </strong>
              </span>
            </div>
          </div>
        )}

        {/* Privacy Settings */}
        <div className="px-6 py-3 border-t border-gray-200">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input
              type="checkbox"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
            />
            <div className="flex-1">
              <span className="text-sm font-medium text-gray-900 group-hover:text-blue-700 transition-colors">
                Private
              </span>
              <p className="text-xs text-gray-500 mt-0.5">
                Only you can access these files. They will be restricted from
                public viewing.
              </p>
            </div>
          </label>
        </div>

        {/* Footer */}
        <DialogFooter className="px-6 pb-4">
          <Button
            variant="outline"
            onClick={onClose}
            className="border-gray-200 text-gray-700 bg-gray-100 hover:border-gray-400"
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={selectedFiles.length === 0}
            className="bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 text-white border-0 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload {selectedFiles.length > 0 && `(${selectedFiles.length})`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
