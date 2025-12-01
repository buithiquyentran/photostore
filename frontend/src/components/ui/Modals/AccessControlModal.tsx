import React, { useState } from "react";
import { Button } from "../button";

type Props = {
  open: boolean;
  onClose: () => void;
  onSave: (is_private: boolean) => void;
  _is_private: boolean;
};

const AccessControlModal: React.FC<Props> = ({
  open,
  onClose,
  onSave,
  _is_private,
}) => {
  const [is_private, setIs_private] = useState<boolean>(_is_private);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="w-full max-w-md rounded-lg bg-white shadow-2xl border border-gray-700 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-200">
        {/* Header with gradient */}
        <div className="bg-gradient-to-r bg-[#005095] px-6 py-4">
          <h2 className="text-xl font-semibold text-white">
            Set Access Control (1 Asset)
          </h2>
        </div>

        {/* Options */}
        <div className="p-4 space-y-2 bg-white/5">
          {/* Public */}
          <label className="flex cursor-pointer items-start space-x-3 p-1 rounded-lg border border-gray-300 hover:border-blue-500 hover:bg-blue-50/50 transition-all">
            <input
              type="radio"
              name="access"
              value="public"
              checked={is_private === false}
              onChange={() => {
                setIs_private(false);
              }}
              className="mt-1 w-4 h-4 text-blue-600"
            />
            <div className="flex-1">
              <span className="font-medium text-gray-900 block">Public</span>
              <p className="text-sm text-gray-600 mt-1">
                Asset can be accessed by everyone.
              </p>
            </div>
          </label>

          {/* Restricted */}
          <label className="flex cursor-pointer items-start space-x-3 p-1 rounded-lg border border-gray-300 hover:border-blue-500 hover:bg-blue-50/50 transition-all">
            <input
              type="radio"
              name="access"
              value="restricted"
              checked={is_private === true}
              onChange={() => setIs_private(true)}
              className="mt-1 w-4 h-4 text-blue-600"
            />
            <div className="flex-1">
              <span className="font-medium text-gray-900 block">
                Restricted
              </span>
              <p className="text-sm text-gray-600 mt-1">
                Asset can be publicly accessed only between (or until/from) the
                specified dates. At other times, only those with an
                authentication token can access it.
              </p>
            </div>
          </label>
        </div>

        {/* Footer */}
        <div className="px-4 pb-2 flex justify-end gap-3">
          <Button
            variant="outline"
            onClick={onClose}
            className="border-gray-200 text-gray-700 bg-gray-100 hover:border-gray-400"
          >
            Cancel
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              onSave(is_private);
              onClose();
            }}
            className="border-blue-200 text-[#005095] bg-blue-100 hover:border-[#005095] w-32"
          >
            Save
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AccessControlModal;
