import { useState } from "react";
import AnimatedNavbar from "./components/AnimatedNavbar";
import ThemeToggle from "./components/ThemeToggle";
import { HomePage } from "./pages/HomePage";
import { TravelsPage } from "./pages/TravelsPage";
import { DevPage } from "./pages/DevPage";
import { GamingPage } from "./pages/GamingPage";
import "./index.css";

const pageMap: Record<string, React.ComponentType> = {
  HOME: HomePage,
  TRAVELS: TravelsPage,
  DEV: DevPage,
  GAMING: GamingPage,
};

export function App() {
  const [activeTab, setActiveTab] = useState("HOME");

  const ActivePage = pageMap[activeTab] ?? HomePage;

  return (
    <div className="min-h-screen flex flex-col">
      <ThemeToggle />
      <header className="w-full">
        <AnimatedNavbar activeTab={activeTab} onTabChange={setActiveTab} />
      </header>
      <main className="mx-auto flex-1 w-full max-w-5xl px-4 py-8">
        <ActivePage />
      </main>
    </div>
  );
}

export default App;
