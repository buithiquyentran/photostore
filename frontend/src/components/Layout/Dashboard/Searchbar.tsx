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

export default function SearchBarFull({
  onSearchText,
  onSearchImage,
  onViewChange,
}) {
  const [query, setQuery] = useState("");
  const [view, setView] = useState("columns");

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

  const changeView = (newView) => {
    setView(newView);
    if (onViewChange) onViewChange(newView);
  };

  return (
    <div className="flex items-center bg-gray-900  px-2 py-1 gap-2 w-full mx-auto border border-gray-700">
      {/* Icon filter */}
      <button className="p-2 text-gray-400 hover:text-white">
        <Filter size={20} />
      </button>

      {/* Input search */}
      <input
        type="text"
        placeholder="Search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="flex-1 bg-transparent outline-none text-white placeholder-gray-400 px-2"
      />

      {/* Upload ảnh */}
      <label className="cursor-pointer text-gray-400 hover:text-white p-2">
        <Upload size={20} />
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleImageUpload}
        />
      </label>

      {/* View toggle */}
      <div className="flex items-center gap-1 bg-gray-800 rounded-full px-1">
        <button
          onClick={() => changeView("columns")}
          className={`p-2 rounded-full ${
            view === "columns"
              ? "text-highlight"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <Columns size={20} />
        </button>
        <button
          onClick={() => changeView("list")}
          className={`p-2 rounded-full ${
            view === "list"
              ? "text-highlight"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <LayoutList size={20} />
        </button>
        <button
          onClick={() => changeView("grid")}
          className={`p-2 rounded-full ${
            view === "grid"
              ? "text-highlight"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <LayoutGrid size={20} />
        </button>
      </div>

      {/* Menu ba chấm */}
      <button className="p-2 text-gray-400 hover:text-white">
        <MoreVertical size={20} />
      </button>

      {/* Nút search text */}
      <button
        onClick={handleTextSearch}
        className="p-2 text-gray-400 hover:text-white"
      >
        <Search size={20} />
      </button>
    </div>
  );
}
