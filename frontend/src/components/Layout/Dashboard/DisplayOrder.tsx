import { useState } from "react";
import { ChevronDown, Check, ArrowUp, ArrowDown } from "lucide-react";

interface AdvancedSearchBarProps {
  fetchContent: (filters: any) => void;
}
const sortOptions = [{"label": "Creation date", "value": "date"}, {"label": "Display name", "value": "name"}, {"label": "Size", "value": "size"}];

export default function DisplayOrder({ fetchContent }: AdvancedSearchBarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState("Creation date");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  const toggleDropdown = () => setIsOpen(!isOpen);
  const [filters, setFilters] = useState<any>({});

  // const handleChange = (option: string) => {
  //   setSelected(option);
  //   setIsOpen(false);
  // };
  const handleChange = (key: string, value: string, label?: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    fetchContent(newFilters);
    if (label)
      setSelected(label);
    setIsOpen(false);
  };
  const toggleOrder = (direction: "asc" | "desc") => {
    setOrder(direction);
  };

  return (
    <div className="w-50">
      {/* Nút mở */}
      <button
        onClick={toggleDropdown}
        className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded hover:bg-gray-700"
      >
        <div>Sort by: {selected} </div>
        {order === "asc" ? <ArrowUp size={16} /> : <ArrowDown size={16} />}
        <ChevronDown size={16} />
      </button>

      {/* Menu dropdown */}
      <div className="relative">
        {isOpen && (
          <div className="absolute mt-2 w-full bg-gray-900 border border-gray-700 rounded shadow-lg">
            <div className="text-gray-300 text-sm">
              {/* Danh sách sort */}
              {sortOptions.map((option) => (
                <div
                  key={option.value}
                  onClick={() => handleChange("sort-by", option.value, option.label)}
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    selected === option.label ? "bg-gray-800" : ""
                  }`}
                >
                  <span>{option.label}</span>
                  {selected === option.label && <Check size={14} />}
                </div>
              ))}

              {/* Order section */}
              <div className="border-t border-gray-700 mt-1">
                <div
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    order === "asc" ? "bg-gray-800" : ""
                  }`}
                  onClick={() => {
                    toggleOrder("asc");
                    handleChange("sort_order", "asc");
                  }}
                >
                  <span>A-Z</span>
                  <ArrowUp size={14} />
                </div>
                <div
                  className={`flex items-center justify-between px-3 py-1.5 hover:bg-gray-700 cursor-pointer ${
                    order === "desc" ? "bg-gray-800" : ""
                  }`}
                  onClick={() => {
                    toggleOrder("desc");
                    handleChange("sort_order", "desc");
                  }}
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
