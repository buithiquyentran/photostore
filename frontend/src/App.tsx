import { Route, Routes } from "react-router-dom";
import path from "@/resources/path";
import PublicLayout from "@/components/Layout/Public/PublicLayout";
import DashboardLayout from "@/components/Layout/Dashboard/DashboardLayout";
import HOME from "@/components/pages/welcome/home";
import LOGIN from "@/components/pages/login/login";
import REGISTER from "@/components/pages/login/register";
function App() {
  return (
    <>
      <Routes>
        <Route path={path.HOME} element={<PublicLayout />}>
          <Route path={path.HOME} element={<HOME />} />
          <Route path={path.REGISTER} element={<REGISTER />} />
          <Route path={path.LOGIN} element={<LOGIN />} />
        </Route>

        <Route path="/" element={<DashboardLayout />}></Route>
      </Routes>
    </>
  );
}
export default App;
