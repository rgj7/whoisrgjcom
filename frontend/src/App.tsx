import { Routes, Route } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import AnimatedNavbar from "./components/AnimatedNavbar";
import ThemeToggle from "./components/ThemeToggle";
import { AdminLayout } from "./layouts/AdminLayout";
import { HomePage } from "./pages/HomePage";
import { TravelsPage } from "./pages/TravelsPage";
import { DevPage } from "./pages/DevPage";
import { GamingPage } from "./pages/GamingPage";
import { PostPage } from "./pages/PostPage";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/admin/DashboardPage";
import { PostsPage } from "./pages/admin/PostsPage";
import { SettingsPage } from "./pages/admin/SettingsPage";
import { CreatePostPage } from "./pages/admin/CreatePostPage";
import { EditPostPage } from "./pages/admin/EditPostPage";
import "./index.css";

export function App() {
  return (
    <TooltipProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/dashboard"
          element={<AdminLayout />}
        >
          <Route index element={<DashboardPage />} />
          <Route path="posts" element={<PostsPage />} />
          <Route path="posts/new" element={<CreatePostPage />} />
          <Route path="posts/:id/edit" element={<EditPostPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route
          path="/*"
          element={
            <div className="min-h-screen flex flex-col">
              <ThemeToggle />
              <header className="w-full">
                <AnimatedNavbar />
              </header>
              <main className="mx-auto flex-1 w-full max-w-5xl px-4 py-8">
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/travels" element={<TravelsPage />} />
                  <Route path="/dev" element={<DevPage />} />
                  <Route path="/gaming" element={<GamingPage />} />
                  <Route path="/posts/:slug" element={<PostPage />} />
                </Routes>
              </main>
            </div>
          }
        />
      </Routes>
    </TooltipProvider>
  );
}

export default App;
