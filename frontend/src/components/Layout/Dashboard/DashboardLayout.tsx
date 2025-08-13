// import Footer from "@/components/TracNghiem9231/Layout/Footer";
import Sidebar from "@/components/Layout/Dashboard/Sidebar";
import { Outlet } from "react-router-dom";

const Layout = () => {
  return (
    <>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="grow">
          <Outlet />
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default Layout;
