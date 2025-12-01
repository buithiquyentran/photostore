import { useEffect, useState, useRef } from "react";
import dayjs from "dayjs";
import {
  ChevronDown,
  Square,
  RectangleHorizontal,
  RectangleVertical,
} from "lucide-react";
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import TagsService from "@/components/api/tags.service";
import FolderSerivce from "@/components/api/folder.service";
import { Filter, Tag, Folder } from "@/interfaces/interfaces";
interface Props {
  fetchContent: (filters: Filter) => void;
  filters: Filter;
  setFilters: React.Dispatch<React.SetStateAction<Filter>>;
  resetSignal: number;
}

export default function AdvancedSearchBar({
  fetchContent,
  filters,
  setFilters,
  resetSignal,
}: Props) {
  const [query, setQuery] = useState("");
  const [tags, setTags] = useState<Array<Tag>>([]);
  const [folders, setFolders] = useState<Array<Folder>>([]);

  useEffect(() => {
    const loadTags = async () => {
      try {
        const response = await TagsService.Get();
        setTags(response.data);
      } catch (error) {
        console.error("Error fetching tags:", error);
      }
    };
    const loadFolders = async () => {
      try {
        const response = await FolderSerivce.GetAll();
        setFolders(response.data);
      } catch (error) {
        console.error("Error fetching tags:", error);
      }
    };
    loadTags();
    loadFolders();
  }, []);
  const handleChange = (key: string, value: string) => {
    if (key == "creationDate") {
      let start_date = null;
      const end_date = new Date(); // mặc định là hiện tại
      switch (value) {
        case "Today":
          start_date = dayjs().startOf("day").toISOString();
          break;
        case "Last 7 days":
          start_date = dayjs().subtract(7, "day").startOf("day").toISOString();
          break;
        case "Last 30 days":
          start_date = dayjs().subtract(30, "day").startOf("day").toISOString();
          break;
        case "This year":
          start_date = dayjs().startOf("year").toISOString();
          break;
        default:
          start_date = null;
      }

      const newFilters = {
        ...filters,
        start_date: start_date ? start_date.toString() : undefined,
        end_date: end_date.toISOString(),
      };

      setFilters(newFilters);
      fetchContent(newFilters);
      return;
    }
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    fetchContent(newFilters);
    return;
  };

  return (
    <div className="bg-gray-900  text-gray-400 p-2 shadow-md flex flex-wrap items-center gap-3 border-b border-gray-700">
      {/* Search box */}
      <input
        type="text"
        placeholder="Type to filter..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-1 text-base flex-1 min-w-[200px]"
      />

      {/* Filter dropdowns */}
      <Dropdown
        label="Display name"
        onChange={(val) => handleChange("keyword", val)}
        onSelectMatchType={(val) => handleChange("match_type", val)}
        isDisplayName={true}
        resetSignal={resetSignal}
      />

      <Dropdown
        label="Folders"
        options={folders}
        onChange={(val) => handleChange("folder_path", val)}
        withInput={true}
        showPath={true}
        resetSignal={resetSignal}
      />
      <Dropdown
        label="Creation date"
        options={["Today", "Last 7 days", "Last 30 days", "This year"]}
        onChange={(val) => handleChange("creationDate", val)}
        resetSignal={resetSignal}
      />
      <Dropdown
        label="Tags"
        options={tags?.map((tag) => tag.name)}
        onChange={(val) => handleChange("tag", val)}
        withInput={true}
        resetSignal={resetSignal}
      />
      <Dropdown
        label="Formats"
        options={["jpg", "png", "webp", "mp4"]}
        onChange={(val) => handleChange("file_extension", val)}
        resetSignal={resetSignal}
      />
      <Dropdown
        label="Asset types"
        options={["Image", "Video"]}
        onChange={(val) => {
          const is_image = val === "Image" ? "true" : "false";
          handleChange("is_image", is_image);
        }}
        resetSignal={resetSignal}
      />

      <Dropdown
        label="Orientations"
        options={[
          {
            value: "landscape",
            label: "Landscape",
            icon: <RectangleHorizontal className="w-4 h-4" />,
          },
          {
            value: "portrait",
            label: "Portrait",
            icon: <RectangleVertical className="w-4 h-4" />,
          },
          {
            value: "square",
            label: "Square",
            icon: <Square className="w-4 h-4" />,
          },
        ]}
        onChange={(val) => handleChange("shape", val)}
        resetSignal={resetSignal}
      />

      {/* Add more */}
      <button className="text-blue-400 text-base hover:underline">
        + Add more
      </button>
    </div>
  );
}

interface DropdownProps {
  label: string;
  options?: Array<
    | string
    | {
        value?: string;
        label?: string;
        icon?: React.ReactNode;
        path?: string;
        slug?: string;
        name?: string;
      }
  >;
  onChange: (value: string) => void;
  isDisplayName?: boolean;
  withInput?: boolean;
  onSelectMatchType?: (value: string) => void;
  showPath?: boolean; // ✅ thêm prop mới
  resetSignal: number;
}

function Dropdown({
  label,
  options,
  isDisplayName = false,
  onChange,
  onSelectMatchType,
  withInput = false,
  showPath = false, // ✅ thêm prop mới
  resetSignal,
}: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState("");
  const [selectedMatchType, setSelectedMatchType] = useState("start-with");
  const [displayName, setDisplayName] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredOptions = options?.filter((opt) => {
    const text =
      typeof opt === "string" ? opt : opt.label ?? opt.value ?? opt.name;
    return text?.toLowerCase().includes(search.toLowerCase());
  });

  const handleSelectOption = (value: string) => {
    setSelected(value);

    onChange(value);

    setIsOpen(false);
    setSearch("");
  };

  const handleChangeDisplayName = (value: string) => {
    setSelected(value);
    onChange(value);
  };
  useEffect(() => {
    setSelected("");
    setSearch("");
    setDisplayName("");
  }, [resetSignal]);

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
    <div ref={dropdownRef} className="relative">
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-base text-left flex items-center justify-between hover:bg-gray-700 transition-colors"
      >
        <span className={selected ? "text-white font-medium" : "text-gray-400"}>
          {selected || label}
        </span>
        <ChevronDown className="w-4 h-4" />
      </button>

      {/* Dropdown */}
      <div className="relative">
        {isOpen &&
          (isDisplayName ? (
            <div className="absolute w-50 bg-white border border-gray-300 rounded mt-1 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
              <div className="p-1 space-y-2">
                <Select
                  value={selectedMatchType}
                  onValueChange={(v) => {
                    setSelectedMatchType(v);
                    onSelectMatchType?.(v);
                  }}
                >
                  <SelectTrigger className="bg-white border-gray-300 text-gray-900">
                    <SelectValue placeholder="Choose match type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="start-with">Start with</SelectItem>
                    <SelectItem value="equal-to">Equal to</SelectItem>
                  </SelectContent>
                </Select>
                <input
                  type="text"
                  placeholder="Search..."
                  value={displayName}
                  onChange={(e) => {
                    handleChangeDisplayName(e.target.value);
                    setDisplayName(e.target.value);
                  }}
                  className="w-full px-3 py-2 bg-gray-100 border border-gray-300 text-gray-900 rounded outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>
          ) : (
            <div className="absolute w-40 bg-white border border-gray-300 rounded mt-1 shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 z-50">
              {/* Search input */}
              {withInput && (
                <div className="border-b border-gray-100">
                  <input
                    type="text"
                    placeholder="Search..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-gray-100 border border-gray-300 text-gray-900 rounded outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                  />
                </div>
              )}

              {/* Options */}
              <div className="max-h-40 overflow-y-auto">
                {filteredOptions && filteredOptions.length > 0 ? (
                  filteredOptions.map((opt) => {
                    const itemKey =
                      typeof opt === "string"
                        ? opt
                        : opt.value ?? opt.path ?? opt.name ?? opt.label ?? "";
                    const labelText =
                      typeof opt === "string" ? opt : opt.label || opt.name;
                    const icon = typeof opt === "string" ? null : opt.icon;
                    const path =
                      typeof opt === "string"
                        ? null
                        : opt.path == opt.slug
                        ? "/"
                        : opt.path;

                    return (
                      <div
                        key={itemKey}
                        onClick={() => handleSelectOption(itemKey)}
                        className="px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 cursor-pointer flex flex-col transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          {icon && <span>{icon}</span>}
                          <span className="font-medium">{labelText}</span>
                        </div>
                        {showPath && path && (
                          <span className="text-xs text-gray-500 ml-2 truncate mt-0.5">
                            {path}
                          </span>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="px-3 py-2 text-sm text-gray-400">
                    No results found
                  </div>
                )}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
