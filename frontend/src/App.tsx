import { Routes, Route } from "react-router-dom";
import AnimatedNavbar from "./components/AnimatedNavbar";
import ThemeToggle from "./components/ThemeToggle";
import { HomePage } from "./pages/HomePage";
import { TravelsPage } from "./pages/TravelsPage";
import { DevPage } from "./pages/DevPage";
import { GamingPage } from "./pages/GamingPage";
import { PostPage } from "./pages/PostPage";
import { LoginPage } from "./pages/LoginPage";
import "./index.css";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
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
  );
}

export default App;
