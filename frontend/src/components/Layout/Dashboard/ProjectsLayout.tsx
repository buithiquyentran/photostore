import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/Layout/Dashboard/Sidebar/Sidebar";
const ProjectsLayout = () => {
  const pathParts = location.pathname.replace(/^\/dashboard\/?/, "");
  const [selectedMenu, setSelectedMenu] = useState<string>("");
  const [, setFolderPath] = useState<string>(pathParts);

  return (
    <>
      <div className="flex min-h-screen ">
        <Sidebar
          selectedMenu={selectedMenu}
          setSelectedMenu={setSelectedMenu}
          setFolderPath={setFolderPath}
        />
        <div className="grow flex flex-col bg-background">
          <div className="grow">
            <Outlet />
          </div>
        </div>

        {/* <Footer /> */}
      </div>
    </>
  );
};

export default ProjectsLayout;
