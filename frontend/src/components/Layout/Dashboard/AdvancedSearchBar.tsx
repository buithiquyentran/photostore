import { useEffect, useState } from "react";
import dayjs from "dayjs";
import {
  ChevronDown,
  ChevronUp,
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
interface AdvancedSearchBarProps {
  fetchContent: (filters: any) => void;
}

export default function AdvancedSearchBar({
  fetchContent,
}: AdvancedSearchBarProps) {
  const [filters, setFilters] = useState<any>({});
  const [query, setQuery] = useState("");
  const [tags, setTags] = useState<Array<{ id: number; name: string }>>([]);
  const [folders, setFolders] = useState<Array<any>>([]);

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
        start_date,
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
      />

      <Dropdown
        label="Folders"
        options={folders}
        onChange={(val) => handleChange("folder_path", val)}
        withInput={true}
        showPath={true}
      />
      <Dropdown
        label="Creation date"
        options={["Today", "Last 7 days", "Last 30 days", "This year"]}
        onChange={(val) => handleChange("creationDate", val)}
      />
      <Dropdown
        label="Tags"
        options={tags?.map((tag) => tag.name)}
        onChange={(val) => handleChange("tag", val)}
        withInput={true}
      />
      <Dropdown
        label="Formats"
        options={["jpg", "png", "webp", "mp4"]}
        onChange={(val) => handleChange("file_extension", val)}
      />
      <Dropdown
        label="Asset types"
        options={["Image", "Video"]}
        onChange={(val) => {
          const is_image = val === "Image" ? "true" : "false";
          handleChange("is_image", is_image);
        }}
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
  options?: Array<string | {}>;
  onChange: (value: string) => void;
  isDisplayName?: boolean;
  withInput?: boolean;
  onSelectMatchType?: (value: string) => void;
  showPath?: boolean; // ✅ thêm prop mới
}
function Dropdown({
  label,
  options,
  isDisplayName = false,
  onChange,
  onSelectMatchType,
  withInput = false,
  showPath = false, // ✅ thêm prop mới
}: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState("");
  const [selectedMatchType, setSelectedMatchType] = useState("start-with");
  const [displayName, setDisplayName] = useState("");
  const filteredOptions = options?.filter((opt) => {
    const text = typeof opt === "string" ? opt : opt.label ?? opt.value ?? "";
    return text.toLowerCase().includes(search.toLowerCase());
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

  return (
    <div>
      {/* Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-base text-left flex"
      >
        {selected || label} <ChevronDown />
      </button>
      <span></span>

      {/* Dropdown */}
      <div className="relative">
        {isOpen &&
          (isDisplayName ? (
            <div className="absolute w-60 bg-gray-800 border border-gray-700 rounded mt-1 shadow-lg">
              <Select
                value={selectedMatchType}
                onValueChange={(v) => {
                  setSelectedMatchType(v);
                  onSelectMatchType?.(v);
                }}
              >
                <SelectTrigger className="bg-gray-800 text-white">
                  <SelectValue placeholder="Choose match type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="start-with">Start with</SelectItem>
                  <SelectItem value="equal-to">Equal to</SelectItem>
                </SelectContent>
              </Select>
              <input
                type="text"
                placeholder="Enter name..."
                value={displayName}
                onChange={(e) => {
                  handleChangeDisplayName(e.target.value);
                  setDisplayName(e.target.value);
                }}
                className="w-full px-2 py-1 bg-gray-700 text-white rounded outline-none border-gray-600"
              />
            </div>
          ) : (
            <div className="absolute  w-60 bg-gray-800 border border-gray-600 rounded mt-1 shadow-lg">
              {/* Search input */}
              {withInput && (
                <input
                  type="text"
                  placeholder="Search..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full px-2 py-1 text-base bg-gray-700 text-white border-b border-gray-600 outline-none"
                />
              )}

              {/* Options */}
              <div className="max-h-40 overflow-y-auto">
                {filteredOptions && filteredOptions.length > 0 ? (
                  filteredOptions.map((opt) => {
                    const key =
                      typeof opt === "string" ? opt : opt.value || opt.path;
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
                        key={key}
                        onClick={() => handleSelectOption(key)}
                        className="px-2 py-1 text-sm text-white hover:bg-gray-600 cursor-pointer flex flex-col"
                      >
                        <div className="flex items-center">
                          {icon && <span className="mr-2">{icon}</span>}
                          <span>{labelText}</span>
                        </div>
                        {showPath && path && (
                          <span className="text-xs text-gray-400 ml-2 truncate">
                            {path}
                          </span>
                        )}
                      </div>
                    );
                  })
                ) : (
                  <div className="px-2 py-1 text-gray-400">
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
