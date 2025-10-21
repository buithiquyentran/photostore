import { useState } from "react";
import { X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface TagInputProps {
  initialTags?: string[];
  onChange?: (tags: string[]) => void;
}

export default function TagInput({
  initialTags = [],
  onChange,
}: TagInputProps) {
  const [tags, setTags] = useState<string[]>(initialTags);
  const [inputValue, setInputValue] = useState("");

  const addTag = (value: string) => {
    const newTag = value.trim();
    if (!newTag || tags.includes(newTag)) return;
    const newTags = [...tags, newTag];
    setTags(newTags);
    onChange?.(newTags);
    setInputValue("");
  };

  const removeTag = (tag: string) => {
    const newTags = tags.filter((t) => t !== tag);
    setTags(newTags);
    onChange?.(newTags);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addTag(inputValue);
    }
  };

  return (
    <div className="space-y-2">
      <label className="text-gray-400 text-base">Tags</label>

      <div
        className={cn(
          "flex flex-wrap items-center border rounded-md p-2",
          "focus-within:ring-1 focus-within:ring-primary"
        )}
      >
        {tags.map((tag) => (
          <div
            key={tag}
            className="flex items-center gap-1 p-1 rounded-full text-base"
          >
            {tag}
            <button
              onClick={() => removeTag(tag)}
              className="hover:text-destructive focus:outline-none"
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        ))}
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Add tag..."
          className="border-none focus-visible:ring-0 flex-1 min-w-[120px]"
        />
      </div>

      {inputValue && !tags.includes(inputValue.trim()) && (
        <div
          className="text-base text-muted-foreground border rounded-md px-3 py-2 cursor-pointer hover:bg-accent"
          onClick={() => addTag(inputValue)}
        >
          Add a new tag:{" "}
          <span className="text-foreground font-medium">{inputValue}</span>
        </div>
      )}
    </div>
  );
}
