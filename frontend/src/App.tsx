import { Route, Routes } from "react-router-dom";
import path from "@/components/resources/path";
import Layout from "@/components//pages/Layout.tsx";
import Home from "@/components/pages/home.tsx";
function App() {
  return (
    <>
      <Routes>
        <Route path={path.HOME} element={<Home />} />
        <Route path="/" element={<Layout />}></Route>
      </Routes>
    </>
  );
}
export default App;
