import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import TagService from "@/components/api/tags.service";
import { toast } from "@/hooks/use-toast";

interface TagInputProps {
  initialTags: object[];
  asset_id: number;
}

export default function TagInput({
  initialTags = [],
  asset_id,
}: TagInputProps) {
  const [tags, setTags] = useState<[]>();
  const [tagList, setTagList] = useState<string[]>();
  const [inputValue, setInputValue] = useState("");

  useEffect(() => {
    setTags(initialTags);
    setTagList(initialTags?.map((tag) => tag.name));
  }, [initialTags]);

  const addTag = async (value: string) => {
    const newTagValue = value.trim();
    if (!newTagValue || tags.some((t) => t.name === newTagValue)) return;

    try {
      const response = await TagService.Add({
        asset_id: Number(asset_id),
        tag_names: [newTagValue],
      });
      const newTag: Tag = { name: response.added_tags[0], id: response.id };
      const newTags = [...tags, newTag];
      setTags(newTags);
      setInputValue("");
      // toast({ title: `Tag "${newTag.name}" created successfully!` });
    } catch (error: any) {
      toast({
        title: "Add tag failed",
        description: error.response?.data?.detail || "Please try again later.",
        variant: "destructive",
      });
    }
  };

  const removeTag = async (tag) => {
    try {
      await TagService.Delete(asset_id, Number(tag.id));
      const newTags = tags?.filter((t) => t.name !== tag.name);
      console.log(newTags);
      setTags(newTags);
    } catch (error: any) {
      toast({
        title: "Delete tag failed",
        description: error.response?.data?.detail || "Please try again later.",
        variant: "destructive",
      });
    }
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
        {tags?.map((tag) => (
          <div
            key={tag.id}
            className="flex items-center gap-1 p-1 rounded-full text-base"
          >
            {tag.name}
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
