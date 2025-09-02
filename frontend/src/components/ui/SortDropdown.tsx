import { useState } from "react";
import { ChevronDown, Check, ArrowUp, ArrowDown } from "lucide-react";

const sortOptions = [
  "Relevance",
  "Last replaced",
  "Public ID",
  "Creation date",
  "Display name",
  "Size",
];

export default function SortDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState("Creation date");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const toggleDropdown = () => setIsOpen(!isOpen);

  const handleSelect = (option: string) => {
    setSelected(option);
    setIsOpen(false);
  };

  const toggleOrder = (direction: "asc" | "desc") => {
    setOrder(direction);
  };

  return (
    <div className="text-left">
      {/* Nút mở */}
      <button
        onClick={toggleDropdown}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded hover:bg-gray-700"
      >
        Sort by: {selected}{" "}
        {order === "asc" ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
        <ChevronDown size={16} />
      </button>

      {/* Menu dropdown */}
      <div className="relative">
        {isOpen && (
          <div className="absolute right-10 mt-2 w-48 bg-gray-900 border border-gray-700 rounded shadow-lg">
            <div className="text-gray-300 text-sm">
              {/* Danh sách sort */}
              {sortOptions.map((option) => (
                <div
                  key={option}
                  onClick={() => handleSelect(option)}
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    selected === option ? "bg-gray-800" : ""
                  }`}
                >
                  <span>{option}</span>
                  {selected === option && <Check size={14} />}
                </div>
              ))}

              {/* Order section */}
              <div className="border-t border-gray-700 mt-1">
                <div
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    order === "asc" ? "bg-gray-800" : ""
                  }`}
                  onClick={() => toggleOrder("asc")}
                >
                  <span>A-Z</span>
                  <ArrowUp size={14} />
                </div>
                <div
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    order === "desc" ? "bg-gray-800" : ""
                  }`}
                  onClick={() => toggleOrder("desc")}
                >
                  <span>Z-A</span>
                  <ArrowDown size={14} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
