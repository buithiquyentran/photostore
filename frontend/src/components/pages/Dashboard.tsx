import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";

export default function Dashboard() {
  return (
    <div className="p-6 space-y-4">
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">My Projects</h2>
        </CardHeader>
        <CardContent>
          <p>Danh sách project sẽ hiển thị ở đây.</p>
          <Button className="mt-4">Tạo project mới</Button>
        </CardContent>
      </Card>
      <Button variant="default">Tạo project mới</Button>
    </div>
  );
}
