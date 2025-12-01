import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FolderPlus } from "lucide-react";

export default function CreateFolderDialog({
  onCreate,
}: {
  onCreate: (name: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [folderName, setFolderName] = useState("New folder");

  const handleCreate = () => {
    if (!folderName.trim()) return;
    onCreate(folderName);
    setFolderName("");
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <FolderPlus className="h-4 w-4" />
          Add Folder
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] p-0 overflow-hidden bg-white border-gray-700">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r bg-[#005095] px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-white text-xl font-semibold flex items-center gap-2">
              <FolderPlus className="h-5 w-5" />
              Create New Folder
            </DialogTitle>
          </DialogHeader>
        </div>

        {/* Content */}
        <div className="px-4 space-y-2 bg-white/5">
          <div className="">
            <Label htmlFor="folderName" className="text-gray-700 font-medium">
              Folder name
            </Label>
            <Input
              id="folderName"
              placeholder="Enter folder name"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              className="bg-white border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 text-black mt-1"
            />
          </div>
        </div>

        {/* Footer */}
        <DialogFooter className="px-6 pb-4">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            className="border-gray-200 text-gray-700 bg-gray-100 hover:border-gray-400"
          >
            Cancel
          </Button>
          <Button
            variant="outline"
            onClick={handleCreate}
            className=" border-blue-200 text-[#005095] bg-blue-100 hover:border-[#005095]"
          >
            Create Folder
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
