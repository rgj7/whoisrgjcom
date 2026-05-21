import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMe } from "@/lib/api";

export function DashboardPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState<string | null>(null);


  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }

    getMe(token)
      .then((user) => setUsername(user.username))
      .catch(handleLogout);
  }, [navigate]);

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    navigate("/login");
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="w-full border-b">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <button
            onClick={handleLogout}
            className="text-sm text-muted-foreground underline-offset-4 hover:underline"
          >
            Logout
          </button>
        </div>
      </header>
      <main className="mx-auto flex-1 w-full max-w-5xl px-4 py-8">
        <div className="grid gap-2">
          <h2 className="text-2xl font-bold">
            Welcome, {username ?? "loading..."}!
          </h2>
          <p className="text-muted-foreground">
            This is your admin dashboard. More features coming soon.
          </p>
        </div>
      </main>
    </div>
  );
}
