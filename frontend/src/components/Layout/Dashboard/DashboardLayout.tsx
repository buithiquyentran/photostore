// import Footer from "@/components/TracNghiem9231/Layout/Footer";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar";
import SearchBar from "@/components/Layout/Dashboard/SearchBar";
import AssetsService from "@/components/services/assets.service";
const Layout = () => {
  const handleSearchText = (text) => {
    console.log("Searching by text:", text);
    // Gọi API backend tìm kiếm text
  };

  const handleSearchImage = (e) => {
    console.log("Searching by image:", file);
    // Upload file -> backend -> search AI
  };
  // const handleUpload = async (e) => {
  //   const file = e.target.files?.[0];
  //   if (file){
  //     const response = await AssetsService.Upload(file);
  //     if (response.status === 1){
  //       alert("Upload thành công");
  //     }else
  //     {
  //       alert("Upload thất bại");
  //     }
  //   }

  // };
const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (file) {
    try {
      const response = await AssetsService.Upload(file);
      if (response.status == 1) {
        alert("Upload thành công");
      } else {
        alert("Upload thất bại");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert(`Lỗi upload file ${error}` );
    }
  }
};

  return (
    <>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="grow flex flex-col bg-bg">
          <SearchBar
            onSearchText={handleSearchText}
            onSearchImage={handleSearchImage} 
            onUpload={handleUpload}
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
