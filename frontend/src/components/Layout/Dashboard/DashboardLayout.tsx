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
const handleUpload = async (e) => {
  const files = e.target.files;
  if (files && files.length > 0) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]); // phải trùng với tên param trong BE
    }

    try {
      const res = await AssetsService.Upload(formData);

      console.log("Upload results:", res.data);
      alert("Upload thành công");
    } catch (err) {
      console.error(err);
      alert("Upload thất bại");
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
