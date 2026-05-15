import React, { useRef, useEffect } from "react";

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
  activeTab: string;
  onTabChange: (label: string) => void;
}

const AnimatedNavbar = ({
  className,
  isAnimated = true,
  activeTab,
  onTabChange,
}: AnimatedNavbarProps) => {
  return (
    <div className={cn("flex w-full justify-center p-4", className)}>
      <nav className="relative flex w-full items-center justify-center">
        {navItems.map((item) => (
          <NavItem
            key={item.label}
            {...item}
            isActive={activeTab === item.label}
            onClick={() => onTabChange(item.label)}
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
          ? "text-white dark:text-white"
          : "text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200",
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {isActive && (
        <motion.div
          layoutId="active-pill"
          className="absolute inset-0 bg-black shadow-sm dark:bg-neutral-800"
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
