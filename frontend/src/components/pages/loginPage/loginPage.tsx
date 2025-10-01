import { useEffect, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
// import { FaLock } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import FormGroup from "@/components/ui/FormGroup";
// import ModalThongBao from "@/components/TracNghiem9231/shared/ModalThongBao";
import path from "@/resources/path";
import LoginService from "@/components/api/login.service";
import UserService from "@/components/api/user.service";

import keycloak from "@/keycloak";
const DangNhapPage: React.FC = () => {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState<{
    message: string;
    warningMessage?: string;
    success: boolean; // Dùng để xác định trạng thái
  } | null>(null);

  // useEffect(() => {
  //   // Kiểm tra xem người dùng đã đăng nhập hay chưa
  //   const accessToken = localStorage.getItem("access_token");
  //   if (accessToken) {
  //     // Nếu đã đăng nhập, chuyển hướng đến trang
  //     navigate(path.HOME);
  //   }
  // }, [navigate]);

  const handleSubmit = async () => {
    if (!email) {
      setIsModalOpen({
        message: "Vui lòng nhập email trước khi xác nhận!",
        success: false,
      });
      return;
    }

    if (!password) {
      setIsModalOpen({
        message: "Vui lòng nhập mật khẩu trước khi xác nhận!",
        success: false,
      });
      return;
    }

    try {
      const response = await LoginService.Login({
        username: email,
        password: password,
      });

      console.log(response);
      if (response.access_token) {
        localStorage.setItem("access_token", response.access_token);
        localStorage.setItem("refresh_token", response.refresh_token);
        setIsModalOpen(null);
        try {
          const userRes = await UserService.SocialLogin();
          console.log("SocialLogin response:", userRes);
        } catch (err) {
          console.error("SocialLogin error:", err);
        }
        // Refresh trang sau khi đăng nhập thành công
        navigate("/brower");
      } else {
        if (response.data.code === "2222") {
          setIsModalOpen({
            message: "Tài khoản hoặc mật khẩu không hợp lệ!",
            success: false,
          });
          return;
        }
        setIsModalOpen({
          message: response.data.mess,
          success: false,
        });
      }
    } catch (error: unknown) {
      if (error instanceof Error) {
        setIsModalOpen({
          message:
            error.message ||
            "Tài khoản / Mật khẩu không đúng hoặc đã hết hạn. Vui lòng thử lại!",
          success: false,
        });
      }
    }
  };

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      await handleSubmit();
    }
  };
  const handleFacebookLogin = () => {
    if (!keycloak) {
      console.error("Keycloak chưa khởi tạo!");
      return;
    }
    keycloak.login({
      idpHint: "facebook",
      prompt: "login",
      redirectUri: window.location.origin + "/brower",
    });
  };
  return (
    <div className="h-screen bg-bg">
      <div
        className="absolute top-1/2 left-1/2 w-[90%] md:w-[564px] h-fit -translate-x-1/2 -translate-y-1/2
            bg-secondary  rounded-3xl p-10 flex flex-col gap-8 justify-center shadow-2xl"
      >
        <div className="w-full sm:w-[425px] h-[84px] self-center text-headline">
          <h1 className="text-center text-4xl md:text-5xl font-bold mt-2 underline underline-offset-4 decoration-4 decoration-highlight no-wrap">
            Log in
          </h1>
          <p className="text-center text-gray-600 mt-2 text-[14px] md:text-[16px]">
            Sign in to save your moments!
          </p>
        </div>

        <div className="w-full flex flex-col gap-[10px] md:gap-4">
          <FormGroup
            label="Email"
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value.trim())}
          />

          <FormGroup
            label="Password"
            id="password"
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
          >
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              title={showPassword ? "Show password" : "Hide password"}
              className="text-headline"
            >
              {showPassword ? <EyeOff /> : <Eye />}
            </button>
          </FormGroup>

          <button
            type="button" // ngăn form submit tự động
            className="hover:bg-highlight hover:text-headline font-normal rounded-[32px] 
                text-center bg-headline text-[16px] md:text-xl w-full text-white h-12 md:h-14"
            onClick={() => handleSubmit()}
          >
            LOG IN
          </button>

          {/* Login bằng Facebook */}
          <button
            onClick={handleFacebookLogin}
            className="flex w-full items-center justify-center space-x-2 rounded-lg border-1  border-headline py-2 "
          >
            <span>📘</span>
            <span className="text-headline ">Tiếp tục với Facebook</span>
          </button>
          <p className=" text-headline mt-4 max-w-sm mx-auto">
            New to Photostore?{" "}
            <a
              className="underline hover:text-tertiary cursor-pointer"
              onClick={() => navigate(path.REGISTER)}
            >
              Register
            </a>
            .
          </p>
        </div>
      </div>
    </div>
  );
};

export default DangNhapPage;
