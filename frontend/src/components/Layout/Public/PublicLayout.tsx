// import Footer from "@/components/TracNghiem9231/Layout/Footer";
import Navbar from "./Navbar";
import Footer from "./Footer";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <>
      <div className="flex flex-col min-h-screen">
        <Navbar />
        <div className="grow ">
          <Outlet />
        </div>

        <Footer />
      </div>
    </>
  );
};

export default Layout;
