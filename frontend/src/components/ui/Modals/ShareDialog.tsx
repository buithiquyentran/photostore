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
      <DialogContent className="sm:max-w-[500px] p-0 overflow-hidden bg-white border-gray-700">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r bg-[#005095] px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-white text-xl font-semibold">
              Chia sẻ "{folder.name}"
            </DialogTitle>
          </DialogHeader>
        </div>

        {/* Content */}
        <div className="px-6 space-y-2 bg-white/5">
          {/* Chủ sở hữu */}
          <div>
            <div className="text-sm text-gray-500 font-medium mb-2">
              Chủ sở hữu
            </div>
            <div className="flex items-center justify-between border border-gray-300 rounded-lg py-2 px-1 bg-white">
              <div className="flex items-center gap-3">
                {/* Avatar (chữ cái đầu tên user) */}
                <div className="w-10 h-10 rounded-full bg-yellow-500 text-black font-semibold flex items-center justify-center ring-2 ring-yellow-500/20">
                  T
                </div>

                <div>
                  <div className="text-base font-medium text-gray-900">
                    My Test (you)
                  </div>
                  <div className="text-sm text-gray-600">test1@gmail.com</div>
                </div>
              </div>

              <span className="text-sm font-medium border border-gray-300 rounded-md px-3 py-1 bg-gray-50 text-gray-700">
                Chủ sở hữu
              </span>
            </div>
          </div>

          {/* Quyền truy cập */}
          <div>
            <label className="text-sm text-gray-500 font-medium mb-2 block">
              Quyền truy cập
            </label>
            <select className="w-full rounded-lg border border-gray-300 bg-white p-2.5 text-gray-900 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20">
              <option>Chỉ người được mời</option>
              <option>Bất kỳ ai có liên kết</option>
            </select>
          </div>
        </div>

        {/* Footer */}
        <DialogFooter className="px-6 pb-2">
          <Button
            variant="outline"
            onClick={onClose}
            className="border-gray-200 text-gray-700 bg-gray-100 hover:border-gray-400"
          >
            Cancel
          </Button>
          <Button
            onClick={onClose}
            variant="outline"
            className=" border-blue-200 text-[#005095] bg-blue-100 hover:border-[#005095] w-32"
          >
            Xong
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
