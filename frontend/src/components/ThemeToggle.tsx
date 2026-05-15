import { useState, useEffect } from "react";

import BrightnessDownIcon from "./ui/brightness-down-icon";
import MoonIcon from "./ui/moon-icon";

export function ThemeToggle() {
  const [dark, setDark] = useState(() =>
    document.documentElement.classList.contains("dark"),
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <button
      onClick={() => setDark((d) => !d)}
      className="fixed top-4 right-4 z-50 rounded-full bg-white/10 p-2 text-foreground backdrop-blur-md transition-colors hover:bg-white/20 dark:bg-black/10 dark:hover:bg-black/20"
      aria-label="Toggle dark mode"
    >
      {dark ? (
        <BrightnessDownIcon />
      ) : (
        <MoonIcon />
      )}
    </button>
  );
}

export default ThemeToggle;
