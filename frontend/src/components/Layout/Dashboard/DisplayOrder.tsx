import { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, ArrowUp, ArrowDown } from "lucide-react";
import { Filter } from "@/interfaces/interfaces";

interface Props {
  fetchContent: (filters: Filter) => void;
  filters: Filter;
  setFilters: React.Dispatch<React.SetStateAction<Filter>>;
}
const sortOptions = [
  { label: "Creation date", value: "date" },
  { label: "Display name", value: "name" },
  { label: "Size", value: "size" },
];

export default function DisplayOrder({
  fetchContent,
  filters,
  setFilters,
}: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState("Creation date");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const toggleDropdown = () => setIsOpen(!isOpen);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const handleChange = (key: string, value: string, label?: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    fetchContent(newFilters);
    if (label) setSelected(label);
    setIsOpen(false);
  };
  const toggleOrder = (direction: "asc" | "desc") => {
    setOrder(direction);
  };
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  return (
    <div className="w-50">
      {/* Nút mở */}
      <button
        onClick={toggleDropdown}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 min-w-[200px]"
      >
        <div>Sort by: {selected} </div>
        {order === "asc" ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
        <ChevronDown size={16} />
      </button>

      {/* Menu dropdown */}
      <div ref={dropdownRef} className="relative">
        {isOpen && (
          <div className="absolute mt-2 w-full  bg-white border border-gray-300 rounded overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
            <div className="text-gray-900 text-sm">
              {/* Sort options section */}
              <div className="px-3 py-2 bg-gray-50">
                <span className="text-xs text-gray-500 font-semibold uppercase tracking-wide">
                  Sort Options
                </span>
              </div>
              {/* </div> */}

              {/* Danh sách sort */}
              <div className="py-1">
                {sortOptions.map((option) => (
                  <div
                    key={option.value}
                    onClick={() =>
                      handleChange("sort-by", option.value, option.label)
                    }
                    className={`flex items-center justify-between px-3 py-2 hover:bg-blue-50 cursor-pointer transition-colors ${
                      selected === option.label
                        ? "bg-blue-100 text-blue-700"
                        : "text-gray-700"
                    }`}
                  >
                    <span className="font-medium">{option.label}</span>
                    {selected === option.label && (
                      <Check size={16} className="text-blue-600" />
                    )}
                  </div>
                ))}
              </div>

              {/* Order section */}
              <div className="border-t border-gray-200">
                <div className="px-3 py-2 bg-gray-50">
                  <span className="text-xs text-gray-500 font-semibold uppercase tracking-wide">
                    Order
                  </span>
                </div>
                <div
                  className={`flex items-center justify-between px-3 py-2 hover:bg-blue-50 cursor-pointer transition-colors ${
                    order === "asc"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-700"
                  }`}
                  onClick={() => {
                    toggleOrder("asc");
                    handleChange("sort_order", "asc");
                  }}
                >
                  <span className="font-medium">Ascending (A-Z)</span>
                  <ArrowUp
                    size={16}
                    className={
                      order === "asc" ? "text-blue-600" : "text-gray-400"
                    }
                  />
                </div>
                <div
                  className={`flex items-center justify-between px-3 py-2 hover:bg-blue-50 cursor-pointer transition-colors ${
                    order === "desc"
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-700"
                  }`}
                  onClick={() => {
                    toggleOrder("desc");
                    handleChange("sort_order", "desc");
                  }}
                >
                  <span className="font-medium">Descending (Z-A)</span>
                  <ArrowDown
                    size={16}
                    className={
                      order === "desc" ? "text-blue-600" : "text-gray-400"
                    }
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
