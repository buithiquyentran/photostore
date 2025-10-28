import { Folder, ChevronRight } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import FolderService from "@/components/api/folder.service";
import CreateFolderDialog from "@/components/ui/Modals/CreateFolderDialog";
import { toast } from "@/hooks/use-toast";

type BreadcrumbPathProps = {
  refetchFolders: () => Promise<any> | void;
  setFolderPath: React.Dispatch<React.SetStateAction<string>>;
  setSelectedMenu: React.Dispatch<React.SetStateAction<string>>;
};

export default function BreadcrumbPath({
  refetchFolders,
  setFolderPath,
  setSelectedMenu,
}: BreadcrumbPathProps) {
  const location = useLocation();

  const pathParts = location.pathname
    .replace(/^\/dashboard\/?/, "")
    .split("/")
    .filter(Boolean);

  const buildHref = (index: number) => {
    const p = pathParts.slice(0, index + 1).join("/");
    return `/dashboard/${p}`;
  };

  // chỉ set folderPath khi user click (không làm trong render)
  const handleCrumbClick = (index: number) => {
    const p = pathParts.slice(0, index + 1).join("/");
    setFolderPath(p);
    setSelectedMenu(p);
    console.log(p)
  };

  const handleAddFolder = async (name: string) => {
    const project_slug = pathParts[0];
    const folder_slug =
      pathParts.length > 1 ? pathParts[pathParts.length - 1] : null;

    try {
      await FolderService.Create({
        project_slug,
        folder_slug,
        name,
      });
      toast({ title: "Folder created!" });

      // gọi đúng hàm refetch
      if (refetchFolders) await refetchFolders();
    } catch (err) {
      console.error(err);
      toast({ title: "Folder creation failed!" });
    }
  };

  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center text-xl text-muted-foreground">
        <Folder className="w-4 h-4 mr-3" />
        {pathParts.map((part, index) => (
          <div key={index} className="flex items-center">
            {index === pathParts.length - 1 ? (
              <span className="flex items-center text-foreground font-medium">
                {part}
              </span>
            ) : (
              <>
                <Link
                  to={buildHref(index)}
                  onClick={() => handleCrumbClick(index)}
                  className="flex items-center text-foreground hover:text-foreground hover:underline"
                >
                  {part}
                </Link>
                <ChevronRight className="w-4 h-4 mx-1 text-muted-foreground" />
              </>
            )}
          </div>
        ))}
      </div>
      <span className="mx-4">:</span>
      <CreateFolderDialog onCreate={handleAddFolder} />
    </div>
  );
}
