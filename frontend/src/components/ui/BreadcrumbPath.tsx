import { Folder, ChevronRight, Plus } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

export default function BreadcrumbPath() {
  const location = useLocation();
  const navigate = useNavigate();

  // Lấy path từ URL và loại bỏ phần đầu `/dashboard/`
  const pathParts = location.pathname
    .replace(/^\/dashboard\//, "")
    .split("/")
    .filter(Boolean);

  const buildPath = (index: number) =>
    `/dashboard/${pathParts.slice(0, index + 1).join("/")}`;

  const handleAddFolder = () => {
    // Tuỳ logic em có thể mở modal hoặc gọi API
    console.log("Add folder tại:", location.pathname);
  };

  return (
    <div className="flex items-center justify-between mb-4">
      {/* Breadcrumb */}
      <div className="flex items-center text-xl text-muted-foreground">
        <Link
          to="/dashboard"
          className="flex items-center font-medium text-foreground hover:underline"
        >
          Projects
        </Link>

        {pathParts.map((part, index) => (
          <div key={index} className="flex items-center">
            <ChevronRight className="w-4 h-4 mx-1 text-muted-foreground" />
            {index === pathParts.length - 1 ? (
              <span className="flex items-center text-foreground font-medium">
                <Folder className="w-4 h-4 mr-1" />
                {part}
              </span>
            ) : (
              <Link
                to={buildPath(index)}
                className="flex items-center text-muted-foreground hover:text-foreground hover:underline"
              >
                <Folder className="w-4 h-4 mr-1" />
                {part}
              </Link>
            )}
          </div>
        ))}
      </div>
        <span className="mx-4">:</span>
      {/* Nút Add Folder */}
      <Button
        onClick={handleAddFolder}
        variant="default"
        className=" bg-gray-800 border border-gray-700 rounded px-2 py-1 text-sm text-left flex"
      >
        <Plus className="w-4 h-4" />
        Add Folder
      </Button>
    </div>
  );
}
