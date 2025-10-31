import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Folder } from "@/interfaces/interfaces";


export default function ShareDialog({
  folder,
  onClose,
}: {
  folder: Folder;
  onClose: () => void;
}) {
  // const [shareLink] = useState(
  //   `${window.location.origin}/share/${folder.slug}`
  // );

  return (
    <Dialog open={!!folder} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Chia sẻ "{folder.name}"</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-2">
          {/* Chủ sở hữu */}
          <div>
            <div className="text-base text-muted-foreground mb-2">
              Chủ sở hữu
            </div>
            <div className="flex items-center justify-between border border-border rounded-md p-3 ">
              <div className="flex items-center gap-3">
                {/* Avatar (chữ cái đầu tên user) */}
                <div className="w-9 h-9 rounded-full bg-yellow-500 text-black font-semibold flex items-center justify-center">
                  T
                </div>

                <div>
                  <div className="text-base font-medium text-foreground">
                    My Test (you)
                  </div>
                  <div className="text-base ">test1@gmail.com</div>
                </div>
              </div>

              <span className="text-base font-medium  border border-border rounded-md px-2 py-1">
                Chủ sở hữu
              </span>
            </div>
          </div>

          {/* Quyền truy cập */}
          <div>
            <label className="text-base text-muted-foreground mb-1 block">
              Quyền truy cập
            </label>
            <select className="w-full rounded-md border bg-background p-2">
              <option>Chỉ người được mời</option>
              <option>Bất kỳ ai có liên kết</option>
            </select>
          </div>
        </div>

        <DialogFooter>
          <Button className="text-black" onClick={onClose}>
            Xong
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
