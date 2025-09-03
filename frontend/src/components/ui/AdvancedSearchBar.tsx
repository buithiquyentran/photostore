import { useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

interface AdvancedSearchBarProps {
  onSearch: (filters: any) => void;
}

export default function AdvancedSearchBar({
  onSearch,
}: AdvancedSearchBarProps) {
  const [filters, setFilters] = useState<any>({});
  const [query, setQuery] = useState("");

  const handleChange = (key: string, value: string) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onSearch(newFilters);
  };

  return (
    <div className="bg-gray-900  text-gray-400 p-4 shadow-md flex flex-wrap items-center gap-3 border-b border-gray-700">
      {/* Search box */}
      <input
        type="text"
        placeholder="Type to filter..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-sm flex-1 min-w-[200px]"
      />

      {/* Filter dropdowns */}
      <Dropdown
        label="Display name"
        options={["asc", "desc"]}
        onChange={(val) => handleChange("displayName", val)}
      />
      <Dropdown
        label="Folders"
        options={["Folder A", "Folder B", "Folder C"]}
        onChange={(val) => handleChange("folder", val)}
      />
      <Dropdown
        label="Creation date"
        options={["Today", "Last 7 days", "Last 30 days", "This year"]}
        onChange={(val) => handleChange("creationDate", val)}
      />
      <Dropdown
        label="Tags"
        options={["tag1", "tag2", "tag3"]}
        onChange={(val) => handleChange("tags", val)}
      />
      <Dropdown
        label="Formats"
        options={["jpg", "png", "webp", "mp4"]}
        onChange={(val) => handleChange("format", val)}
      />
      <Dropdown
        label="Asset types"
        options={["Image", "Video", "Document"]}
        onChange={(val) => handleChange("assetType", val)}
      />
      <Dropdown
        label="Orientations"
        options={["Landscape", "Portrait", "Square"]}
        onChange={(val) => handleChange("orientation", val)}
      />

      {/* Add more */}
      <button className="text-blue-400 text-sm hover:underline">
        + Add more
      </button>
    </div>
  );
}

interface DropdownProps {
  label: string;
  options: string[];
  onChange: (value: string) => void;
}

function Dropdown({ label, options, onChange }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState("");

  const filteredOptions = options.filter((opt) =>
    opt.toLowerCase().includes(search.toLowerCase())
  );

  const handleSelect = (value: string) => {
    setSelected(value);
    onChange(value);
    setIsOpen(false);
    setSearch("");
  };
  return (
    <div>
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-left flex"
      >
        {selected || label} <ChevronDown />
      </button>
      <span></span>

      {/* Dropdown */}
      <div className="relative">
        {isOpen && (
          <div className="absolute  w-64 bg-gray-800 border border-gray-700 rounded mt-1 shadow-lg">
            {/* Search input */}
            <input
              type="text"
              placeholder="Search..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-2 py-1 text-sm bg-gray-700 text-white border-b border-gray-600 outline-none"
            />

            {/* Options */}
            <div className="max-h-40 overflow-y-auto">
              {filteredOptions.length > 0 ? (
                filteredOptions.map((opt) => (
                  <div
                    key={opt}
                    onClick={() => handleSelect(opt)}
                    className="px-2 py-1 text-sm text-white hover:bg-gray-600 cursor-pointer"
                  >
                    {opt}
                  </div>
                ))
              ) : (
                <div className="px-2 py-1 text-sm text-gray-400">
                  No results found
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
