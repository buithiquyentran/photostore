import { useEffect, useState } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";

import path from "@/resources/path";
import PublicLayout from "@/components/Layout/Public/PublicLayout";
import DashboardLayout from "@/components/Layout/Dashboard/DashboardLayout";
import HOME from "@/components/pages/welcome/home";
import LOGIN from "@/components/pages/loginPage/loginPage";
import REGISTER from "@/components/pages/loginPage/registerPage";
import BROWER from "@/components/pages/browerPage";
import VIEWER from "@/components/pages/ViewerPage";
import FAVORITE from "@/components/pages/favoritePage"
import TEST from "@/components/pages/Dashboard";
import { Toaster } from "@/components/ui/toaster";
import keycloak from "@/keycloak";
import { Loading } from "@/components/ui/Loading";

function App() {
  const [keycloakReady, setKeycloakReady] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    keycloak
      .init({ onLoad: "check-sso", pkceMethod: "S256" })
      .then(async (auth) => {
        setKeycloakReady(true);
        if (auth) {
          localStorage.setItem("access_token", keycloak.token || "");
          localStorage.setItem("refresh_token", keycloak.refreshToken || "");
        }
      })
      .catch((err) => {
        console.error("Keycloak init error", err);
        navigate("/login");
      });
  }, []);

  if (!keycloakReady) return <Loading />;

  return (
    <>
      <Routes>
        <Route path={path.HOME} element={<PublicLayout />}>
          <Route path={path.HOME} element={<HOME />} />
          <Route path={path.REGISTER} element={<REGISTER />} />
          <Route path={path.LOGIN} element={<LOGIN />} />{" "}
        </Route>

        <Route path="/" element={<DashboardLayout />}>
          <Route path={path.BROWER} element={<BROWER />} />
          <Route path={path.FAVORITE} element={<FAVORITE />} />
          <Route path={path.TEST} element={<TEST />} />
        </Route>
        <Route path="/">
          <Route path="/photos/*" element={<VIEWER />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}
export default App;
