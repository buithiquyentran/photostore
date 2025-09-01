import { useState } from "react";
import {
  Search,
  Upload,
  Filter,
  LayoutGrid,
  LayoutList,
  Columns,
  MoreVertical,
} from "lucide-react";
import UploadButton from "@/components/ui/UploadButton";
export default function SearchBarFull({
  onSearchText,
  onSearchImage,
  onViewChange,
}) {
  const [query, setQuery] = useState("");

  const handleImageUpload = (e) => {
    const file = e.target.files?.[0];
    if (file && onSearchImage) {
      onSearchImage(file);
    }
  };

  const handleTextSearch = () => {
    if (query.trim() && onSearchText) {
      onSearchText(query);
    }
  };

  return (
    <div className=" sticky top-0 bg-gray-900 ">
      <div className="flex items-center px-2 py-1 gap-2 w-full mx-auto border-b border-gray-700">
        {/* Icon filter */}
        <button className="p-2 text-gray-400 hover:text-white">
          <Search size={20} />
        </button>
        <div className="relative flex flex-1 items-center">
          <input
            type="text"
            placeholder="Search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 h-10 text-white placeholder-gray-400 px-2 bg-gray-800 border border-gray-700 rounded"
          />

          {/* Upload ảnh */}
          <label className=" absolute right-1 cursor-pointer text-gray-400 hover:text-white p-2">
            <Upload size={20} />
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleImageUpload}
            />
          </label>
        </div>
        {/* Input search */}

        {/* Nút search text */}
        <button
          onClick={handleTextSearch}
          className="p-2 text-gray-400 hover:text-white"
        >
          {/* <Search size={20} /> */}
          <UploadButton onClick={() => console.log("upload image")} />
        </button>
        {/* Menu ba chấm */}
        <button className="p-2 text-gray-400 hover:text-white">
          <MoreVertical size={20} />
        </button>
      </div>
    </div>
  );
}
