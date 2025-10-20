import React, { useState } from "react";

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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="w-full max-w-md rounded-lg bg-gray-900 p-6 shadow-lg">
        {/* Header */}
        <h2 className="text-lg font-semibold text-white">
          Set Access Control (1 Asset)
        </h2>

        {/* Options */}
        <div className="mt-4 space-y-4">
          {/* Public */}
          <label className="flex cursor-pointer items-start space-x-3">
            <input
              type="radio"
              name="access"
              value="public"
              checked={is_private === false}
              onChange={() => {
                setIs_private(false);
              }}
              className="mt-1"
            />
            <div>
              <span className="font-medium text-white">Public</span>
              <p className="text-sm text-gray-400">
                Asset can be accessed by everyone.
              </p>
            </div>
          </label>

          {/* Restricted */}
          <label className="flex cursor-pointer items-start space-x-3">
            <input
              type="radio"
              name="access"
              value="restricted"
              checked={is_private === true}
              onChange={() => setIs_private(true)}
              className="mt-1"
            />
            <div>
              <span className="font-medium text-white">Restricted</span>
              <p className="text-sm text-gray-400">
                Asset can be publicly accessed only between (or until/from) the
                specified dates. At other times, only those with an
                authentication token can access it.
              </p>
            </div>
          </label>
        </div>

        {/* Footer */}
        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="rounded bg-gray-700 px-4 py-2 text-sm text-white hover:bg-gray-600"
          >
            Cancel
          </button>
          <button
            onClick={() => {
              onSave(is_private);
              onClose();
            }}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-500"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccessControlModal;
