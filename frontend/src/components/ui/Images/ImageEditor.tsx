import { useState, useCallback } from "react";
import Cropper, { Area } from "react-easy-crop";
import {
  RotateCw,
  Crop,
  X,
  Check,
  RotateCcw,
  ZoomOut,
} from "lucide-react";

interface ImageEditorProps {
  imageUrl: string;
  onSave: (editedImageBlob: Blob) => void;
  onCancel: () => void;
}

const createImage = (url: string): Promise<HTMLImageElement> =>
  new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener("load", () => resolve(image));
    image.addEventListener("error", (error) => reject(error));
    // Quan trọng: Thêm crossOrigin để tránh lỗi CORS khi vẽ lên canvas
    image.setAttribute("crossOrigin", "anonymous");
    image.src = url;
  });

async function getCroppedImg(
  imageSrc: string,
  pixelCrop: Area,
  rotation = 0
): Promise<Blob> {
  const image = await createImage(imageSrc);
  const canvas = document.createElement("canvas");
  const ctx = canvas.getContext("2d");

  if (!ctx) {
    throw new Error("No 2d context");
  }

  // Sử dụng kích thước gốc (natural dimensions)
  const imageWidth = image.naturalWidth;
  const imageHeight = image.naturalHeight;

  // Tính toán kích thước canvas sau khi rotate (giữ nguyên logic của bạn vì nó đúng)
  const rad = (rotation * Math.PI) / 180;
  const sin = Math.abs(Math.sin(rad));
  const cos = Math.abs(Math.cos(rad));
  const newWidth = imageWidth * cos + imageHeight * sin;
  const newHeight = imageWidth * sin + imageHeight * cos;

  canvas.width = newWidth;
  canvas.height = newHeight;

  // Apply transformations
  ctx.translate(newWidth / 2, newHeight / 2);
  ctx.rotate(rad);
  ctx.translate(-imageWidth / 2, -imageHeight / 2);

  // Vẽ ảnh gốc lên canvas đã xoay
  ctx.drawImage(image, 0, 0);

  // Lấy dữ liệu từ vùng crop
  const croppedCanvas = document.createElement("canvas");
  const croppedCtx = croppedCanvas.getContext("2d");

  if (!croppedCtx) {
    throw new Error("No 2d context for cropped canvas");
  }

  // Set kích thước canvas đích bằng đúng kích thước vùng crop
  croppedCanvas.width = pixelCrop.width;
  croppedCanvas.height = pixelCrop.height;

  // Vẽ phần ảnh đã crop sang canvas mới
  croppedCtx.drawImage(
    canvas,
    pixelCrop.x,
    pixelCrop.y,
    pixelCrop.width,
    pixelCrop.height,
    0,
    0,
    pixelCrop.width,
    pixelCrop.height
  );

  return new Promise((resolve, reject) => {
    croppedCanvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
        } else {
          reject(new Error("Canvas is empty"));
        }
      },
      "image/jpeg",
      0.95
    ); // Có thể đổi sang 'image/png' nếu muốn giữ trong suốt
  });
}
export default function ImageEditor({
  imageUrl,
  onSave,
  onCancel,
}: ImageEditorProps) {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [aspect, setAspect] = useState<number | undefined>(undefined); // Free aspect
  const [activeTab, setActiveTab] = useState<"crop" | "rotate">("crop");

  const onCropComplete = useCallback(
    (croppedArea: Area, croppedAreaPixels: Area) => {
      console.log("Percent:", croppedArea); // Kết quả sẽ là ~ {width: 100, height: 100...} -> Đây là cái bạn đang bị dính
      console.log("Pixels:", croppedAreaPixels); // Kết quả sẽ là ~ {width: 2048, height: 2048...} -> Đây là cái ta cần

      setCroppedAreaPixels(croppedAreaPixels);
    },
    []
  );

  const handleSave = useCallback(async () => {
    try {
      if (!croppedAreaPixels) return;
      const croppedImage = await getCroppedImg(
        imageUrl,
        croppedAreaPixels,
        rotation
      );
      onSave(croppedImage);
    } catch (e) {
      console.error(e);
    }
  }, [croppedAreaPixels, rotation, imageUrl, onSave]);

  return (
    <div className="fixed inset-0 bg-black z-[100] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between bg-black/80 px-4 py-3 border-b border-white/10">
        <button
          onClick={onCancel}
          className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/10 text-white transition-colors"
        >
          <X size={20} />
          <span>Cancel</span>
        </button>

        <h2 className="text-white text-lg font-medium">Edit Image</h2>

        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors"
        >
          <Check size={20} />
          <span>Save</span>
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Crop Area */}
        <div className="flex-1 relative">
          <Cropper
            image={imageUrl}
            crop={crop}
            zoom={zoom}
            rotation={rotation}
            aspect={aspect}
            onCropChange={setCrop}
            onCropComplete={onCropComplete}
            onZoomChange={setZoom}
            onRotationChange={setRotation}
            style={{
              containerStyle: {
                backgroundColor: "#000",
              },
            }}
          />
        </div>

        {/* Toolbar */}
        <div className="bg-black/90 border-t border-white/10">
          {/* Tabs */}
          <div className="flex items-center justify-center gap-2 px-4 py-3 border-b border-white/10">
            <button
              onClick={() => setActiveTab("crop")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === "crop"
                  ? "bg-blue-600 text-white"
                  : "text-white/60 hover:text-white hover:bg-white/10"
              }`}
            >
              <Crop size={20} />
              <span>Crop</span>
            </button>
            <button
              onClick={() => setActiveTab("rotate")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === "rotate"
                  ? "bg-blue-600 text-white"
                  : "text-white/60 hover:text-white hover:bg-white/10"
              }`}
            >
              <RotateCw size={20} />
              <span>Rotate</span>
            </button>
          </div>

          {/* Controls */}
          <div className="px-4 py-4">
            {activeTab === "crop" && (
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-2">
                  <button
                    onClick={() => setAspect(undefined)}
                    className={`px-3 py-1.5 rounded text-sm ${
                      aspect === undefined
                        ? "bg-blue-600 text-white"
                        : "bg-white/10 text-white/60 hover:text-white"
                    }`}
                  >
                    Free
                  </button>
                  <button
                    onClick={() => setAspect(1)}
                    className={`px-3 py-1.5 rounded text-sm ${
                      aspect === 1
                        ? "bg-blue-600 text-white"
                        : "bg-white/10 text-white/60 hover:text-white"
                    }`}
                  >
                    1:1
                  </button>
                  <button
                    onClick={() => setAspect(4 / 3)}
                    className={`px-3 py-1.5 rounded text-sm ${
                      aspect === 4 / 3
                        ? "bg-blue-600 text-white"
                        : "bg-white/10 text-white/60 hover:text-white"
                    }`}
                  >
                    4:3
                  </button>
                  <button
                    onClick={() => setAspect(16 / 9)}
                    className={`px-3 py-1.5 rounded text-sm ${
                      aspect === 16 / 9
                        ? "bg-blue-600 text-white"
                        : "bg-white/10 text-white/60 hover:text-white"
                    }`}
                  >
                    16:9
                  </button>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-white/60 text-sm">
                    <span className="flex items-center gap-2">
                      <ZoomOut size={16} />
                      Zoom
                    </span>
                    <span>{Math.round(zoom * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={3}
                    step={0.1}
                    value={zoom}
                    onChange={(e) => setZoom(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            )}

            {activeTab === "rotate" && (
              <div className="space-y-4">
                <div className="flex items-center justify-center gap-3">
                  <button
                    onClick={() => setRotation((r) => r - 90)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white"
                  >
                    <RotateCcw size={20} />
                    <span>-90°</span>
                  </button>
                  <button
                    onClick={() => setRotation((r) => r + 90)}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white"
                  >
                    <RotateCw size={20} />
                    <span>+90°</span>
                  </button>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-white/60 text-sm">
                    <span>Angle</span>
                    <span>{rotation}°</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={360}
                    step={1}
                    value={rotation}
                    onChange={(e) => setRotation(Number(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
