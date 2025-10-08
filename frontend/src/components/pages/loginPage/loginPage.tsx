import { useEffect, useState } from "react";
import { Eye, EyeOff, Facebook } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label";
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
        navigate(path.BROWER);
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
      redirectUri: window.location.origin + path.BROWER,
    });
  };
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#fff] text-foreground px-4">
      <Card className="w-full max-w-md border border-border shadow-lg">
        <CardHeader>
          <CardTitle className="text-center text-3xl font-bold text-[#272343] ">
            Log in
          </CardTitle>
          <p className="text-center text-muted-foreground text-sm">
            Sign in to save your moments!
          </p>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value.trim())}
            />
          </div>

          <div className="space-y-2 relative">
            <Label htmlFor="password">Password</Label>
            <div className="flex items-center">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? "Hide password" : "Show password"}
                className="absolute right-3 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <Button className="w-full bg-[#272343]" onClick={handleSubmit}>
            Log in
          </Button>

          <Button
            variant="outline"
            className="w-full flex items-center justify-center space-x-2 bg-[#fff] text-[#1877F2]"
            onClick={handleFacebookLogin}
          >
            <Facebook className="w-4 h-4 " />
            <span>Continue with Facebook</span>
          </Button>
        </CardContent>

        <CardFooter className="flex justify-center text-sm text-muted-foreground">
          <p>
            New to Photostore?{" "}
            <span
              className="underline cursor-pointer text-[#ffd803]"
              onClick={() => navigate(path.REGISTER)}
            >
              Register
            </span>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default DangNhapPage;
