// import Footer from "@/components/TracNghiem9231/Layout/Footer";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
const Layout = () => {
  const handleSearchText = (text) => {
    console.log("Searching by text:", text);
    // Gọi API backend tìm kiếm text
  };

  const handleSearchImage = (file) => {
    console.log("Searching by image:", file);
    // Upload file -> backend -> search AI
  };
  const handleViewChange = (view) => {
    console.log("View changed to:", view);
  };

  return (
    <>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="grow flex flex-col bg-bg">
          <SearchBar
            onSearchText={handleSearchText}
            onSearchImage={handleSearchImage}
            onViewChange={handleViewChange}
          />
          <div className="grow">
            <Outlet />
          </div>
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default Layout;
