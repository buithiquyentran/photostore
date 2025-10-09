import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
// Update the import path to match your actual toast utility location
import { toast } from "@/hooks/use-toast";
import path from "@/resources/path";
import LoginService from "@/components/api/login.service";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState({
    name: "",
    email: "",
    firstName: "",
    lastName: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setForm((prev) => ({ ...prev, [id]: value.trim() }));
  };

  const handleSubmit = async () => {
    const { name, email, firstName, lastName, password, confirmPassword } =
      form;

    if (!email || !password || !name) {
      toast({
        title: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }
    if (password !== confirmPassword) {
      toast({ title: "Passwords do not match", variant: "destructive" });
      return;
    }

    try {
      await LoginService.Register({
        username: name,
        email,
        first_name: firstName,
        last_name: lastName,
        password,
      });
      toast({ title: "Account created successfully!" });
      navigate(path.LOGIN);
    } catch (error: any) {
      toast({
        title: "Registration failed",
        description: error.response?.data?.detail || "Please try again later.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fff]">
      <Card className="w-[90%] sm:w-[480px] shadow-2xl rounded-3xl">
        <CardHeader className="space-y-2 text-center">
          <CardTitle className="text-4xl font-bold text-[#272343]">
            Register
          </CardTitle>
          <CardDescription>Welcome to Photostore!</CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col gap-3 text-[#272343]">
          <div>
            <Label htmlFor="name">Username</Label>
            <Input id="name" value={form.name} onChange={handleChange} />
          </div>

          <div>
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
          </div>

          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="firstName">First name</Label>
              <Input
                id="firstName"
                value={form.firstName}
                onChange={handleChange}
              />
            </div>
            <div className="flex-1">
              <Label htmlFor="lastName">Last name</Label>
              <Input
                id="lastName"
                value={form.lastName}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="relative">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              value={form.password}
              onChange={handleChange}
            />
            <Button
              variant="ghost"
              size="icon"
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-1 top-7"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </Button>
          </div>

          <div className="relative">
            <Label htmlFor="confirmPassword">Confirm password</Label>
            <Input
              id="confirmPassword"
              type={showPassword ? "text" : "password"}
              value={form.confirmPassword}
              onChange={handleChange}
            />
          </div>
        </CardContent>

        <CardFooter className="flex flex-col gap-3">
          <Button className="w-full h-12 bg-[#272343]" onClick={handleSubmit}>
            REGISTER
          </Button>

          <p className="text-sm text-center text-muted-foreground">
            Already have an account?{" "}
            <span
              className="text-primary underline hover:text-highlight cursor-pointer"
              onClick={() => navigate(path.LOGIN)}
            >
              Log in
            </span>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
