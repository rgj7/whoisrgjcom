import React, { useRef, useState, useEffect } from "react";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import type { AnimatedIconHandle, AnimatedIconProps } from "./ui/types";
import AirplaneIcon from "./ui/airplane-icon";
import CodeIcon from "./ui/code-icon";
import GamepadIcon from "./ui/gamepad-icon";
import HomeIcon from "./ui/home-icon";

const navItems = [
  { icon: HomeIcon, label: "HOME", href: "#" },
  { icon: AirplaneIcon, label: "TRAVELS", href: "#" },
  { icon: CodeIcon, label: "DEV", href: "#" },
  { icon: GamepadIcon, label: "GAMING", href: "#" },
];

interface AnimatedNavbarProps {
  className?: string;
  isAnimated?: boolean;
}

const AnimatedNavbar = ({
  className,
  isAnimated = true,
}: AnimatedNavbarProps) => {
  const [activeTab, setActiveTab] = useState("HOME");

  return (
    <div className={cn("flex w-full justify-center p-4", className)}>
      <nav className="relative flex w-full max-w-2xl items-center justify-between">
        {navItems.map((item) => (
          <NavItem
            key={item.label}
            {...item}
            isActive={activeTab === item.label}
            onClick={() => setActiveTab(item.label)}
            isAnimated={isAnimated}
          />
        ))}
      </nav>
    </div>
  );
};

interface NavItemProps {
  icon: React.ForwardRefExoticComponent<
    AnimatedIconProps & React.RefAttributes<AnimatedIconHandle>
  >;
  label: string;
  href: string;
  isActive: boolean;
  onClick: () => void;
  isAnimated: boolean;
}

const NavItem = ({
  icon: Icon,
  label,
  href,
  isActive,
  onClick,
  isAnimated,
}: NavItemProps) => {
  const iconRef = useRef<AnimatedIconHandle>(null);

  const handleMouseEnter = () => {
    if (isAnimated) {
      iconRef.current?.startAnimation();
    }
  };

  const handleMouseLeave = () => {
    if (isAnimated) {
      iconRef.current?.stopAnimation();
    }
  };

  useEffect(() => {
    if (!isAnimated) {
      iconRef.current?.stopAnimation();
    }
  }, [isAnimated]);

  return (
    <a
      href={href}
      onClick={(e) => {
        e.preventDefault();
        onClick();
      }}
      className={cn(
        "relative flex flex-1 items-center justify-center px-4 py-3 text-sm font-medium transition-colors sm:flex-none",
        isActive
          ? "text-neutral-900 dark:text-white"
          : "text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200",
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {isActive && (
        <motion.div
          layoutId="active-pill"
          className="absolute inset-0 bg-white shadow-sm dark:bg-neutral-800"
          transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
        />
      )}

      <div className="relative z-10 flex items-center gap-2">
        <Icon
          ref={iconRef}
          className={cn("h-5 w-5", isActive ? "text-current" : "")}
        />
        <span className="hidden sm:inline-block">{label}</span>
      </div>
    </a>
  );
};

export default AnimatedNavbar;
