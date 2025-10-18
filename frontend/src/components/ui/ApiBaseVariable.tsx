import { useState } from "react";
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";

export default function ApiBaseVariable() {
  const [copied, setCopied] = useState(false);
  const API_BASE = "http://localhost:8000/api/external";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(API_BASE);
      setCopied(true);
      toast({ title: "Copied to clipboard!" });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  return (
    <div className=" rounded-md p-3  my-4">
      <div className="text-base text-gray-400 mb-1">
        API environment variable
      </div>
      <div className="flex justify-between bg-[#1a1a1a] p-2">
        <div className="font-mono text-base px-3 py-2 rounded-md text-gray-100 ">
          API_BASE = {API_BASE}
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={handleCopy}
          className="ml-3 hover:bg-gray-800"
          title="Copy"
        >
          <Copy
            className={`h-4 w-4 ${copied ? "text-green-400" : "text-gray-400"}`}
          />
        </Button>
      </div>
    </div>
  );
}
