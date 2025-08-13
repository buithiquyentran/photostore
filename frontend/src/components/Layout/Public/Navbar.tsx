import { Search, Camera } from "lucide-react";
import { useNavigate } from "react-router-dom";
import path from "@/resources/path";
const Navbar = () => {
  const navigate = useNavigate();
  return (
    <nav className="bg-headline text-white px-6 py-3 flex items-center justify-between">
      <div className="flex items-center justify-center gap-2 underline underline-offset-4 decoration-4 decoration-highlight">
        <div>
          <Camera className="w-10 h-10 text-tertiary" />
        </div>
        <span className="font-semibold text-2xl text-tertiary">photostore</span>
      </div>

      {/* Menu trái */}
      <ul className="flex items-center space-x-6 text-sm font-medium">
        <li className="hover:text-highlight cursor-pointer">Platform</li>
        <li className="hover:text-highlight cursor-pointer">Solutions</li>
        <li className="hover:text-highlight cursor-pointer">Developers</li>
        <li className="hover:text-highlight cursor-pointer">Resources</li>
        <li className="hover:text-highlight cursor-pointer">About Us</li>
        <li className="hover:text-highlight cursor-pointer">Pricing</li>
      </ul>

      {/* Menu phải */}
      <ul className="flex items-center space-x-4 text-sm font-medium">
        <li>
          <Search className="w-4 h-4 cursor-pointer hover:text-highlight" />
        </li>
        <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
          Contact
        </li>
        <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
          Support
        </li>
        <li className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer">
          Documentation
        </li>
        <li
          className="border-l border-white/40 pl-4 hover:text-highlight cursor-pointer"
          onClick={() => navigate(path.LOGIN)}
        >
          Login
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
