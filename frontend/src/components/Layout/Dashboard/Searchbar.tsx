import { useState, useCallback } from "react";
import { Search, Upload, MoreVertical } from "lucide-react";
import UploadButton from "@/components/ui/Images/UploadButton";
import AdvancedSearchBar from "@/components/Layout/Dashboard/AdvancedSearchBar";
import {
  RotateCcw,
  LayoutDashboard,
  LayoutList,
  LayoutGrid,
} from "lucide-react";
import DisplayOrder from "@/components/Layout/Dashboard/DisplayOrder";

export default function SearchBar({ onSearch, onUpload, fetchContent, view, setView }) {
  const [query, setQuery] = useState("");

  // Debounce (chỉ gọi API sau khi ngừng gõ 500ms)
  const debounce = (func, delay) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func(...args), delay);
    };
  };
  // Wrap search với debounce
  const debouncedSearch = useCallback(debounce(onSearch, 500), []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const text = e.target.value;
    setQuery(text);
    debouncedSearch(null, text); // gọi search khi ngưng gõ
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      console.log(query);
      onSearch(query); // gọi search khi nhấn Enter
    }
  };

  return (
    <div className=" sticky top-0 bg-gray-900 z-20">
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
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            className="flex-1 h-10 text-white placeholder-gray-400 px-2 bg-gray-800 border border-gray-700 rounded"
          />

          {/* Upload ảnh for search*/}
          <label className=" absolute right-1 cursor-pointer text-gray-400 hover:text-white p-2">
            <Upload size={20} />
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onSearch}
            />
          </label>
        </div>
        {/* Upload ảnh */}
        <button className="p-2 text-gray-400 hover:text-white">
          <UploadButton onClick={onUpload} />
        </button>
        {/* Menu ba chấm */}
        <button className="p-2 text-gray-400 hover:text-white">
          <MoreVertical size={20} />
        </button>
      </div>
      <AdvancedSearchBar fetchContent={fetchContent} />
      <div className="flex items-center justify-between px-4 py-1 border-b border-gray-700 text-white">
        <button
          // onClick={fetchAssets}
          className="flex items-center text-gray-400 hover:text-white px-2"
        >
          <RotateCcw size={20} /> &nbsp;
          <span className="text-sm">Refresh</span>
        </button>

        <div className="flex items-center gap-4">
          <DisplayOrder fetchContent={fetchContent} />
          <div className="flex gap-3 p-1 shadow-md">
            <button
              onClick={() => setView("mosaic")}
              className={`p-2 rounded-full ${
                view === "mosaic"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutDashboard size={20} />
            </button>
            <button
              onClick={() => setView("list")}
              className={`p-2 rounded-full ${
                view === "list"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutList size={20} />
            </button>
            <button
              onClick={() => setView("card")}
              className={`p-2 rounded-full ${
                view === "card"
                  ? "text-highlight"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              <LayoutGrid size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
