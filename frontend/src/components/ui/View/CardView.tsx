import ImageCard from "@/components/ui/Images/CardImage";
import { Asset } from "@/interfaces/interfaces";

interface Props {
  assets: Asset[];
  onSelect: (asset: Asset) => void;
  onDelete: (asset_id: number) => void;
}

const CardView = ({ assets, onSelect, onDelete }: Props) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {assets.map((asset) => (
        <div
          key={asset.id}
          className="bg-gray-800  overflow-hidden hover:ring-2 hover:ring-highlight cursor-pointer transition"
        >
          <ImageCard
            asset={asset}
            onDelete={onDelete}
            onClick={() => onSelect(asset)}
          />
        </div>
      ))}
    </div>
  );
};

export default CardView;
