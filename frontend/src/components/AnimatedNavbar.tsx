import React, { useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import type { AnimatedIconHandle, AnimatedIconProps } from "./ui/types";
import AirplaneIcon from "./ui/icons/airplane-icon";
import CodeIcon from "./ui/icons/code-icon";
import GamepadIcon from "./ui/icons/gamepad-icon";
import HomeIcon from "./ui/icons/home-icon";

const navItems = [
  { icon: HomeIcon, label: "HOME", to: "/" },
  { icon: AirplaneIcon, label: "TRAVELS", to: "/travels" },
  { icon: CodeIcon, label: "DEV", to: "/dev" },
  { icon: GamepadIcon, label: "HOBBIES", to: "/hobbies" },
];

interface AnimatedNavbarProps {
  className?: string;
  isAnimated?: boolean;
}

const AnimatedNavbar = ({
  className,
  isAnimated = true,
}: AnimatedNavbarProps) => {
  const location = useLocation();

  return (
    <div className={cn("relative flex w-full items-center justify-center p-6", className)}>
      <Link
        to="/"
        aria-label="Go to home page"
        className="absolute left-6 z-20 transition-opacity hover:opacity-80"
      >
        <img
          src="/images/whoisrgj_logo_invert.png"
          alt=""
          className="h-8 w-auto dark:hidden sm:h-10"
        />
        <img
          src="/images/whoisrgj_logo.png"
          alt=""
          className="hidden h-8 w-auto dark:block sm:h-10"
        />
      </Link>
      <nav className="relative flex items-center justify-center">
        {navItems.map((item) => (
          <NavItem
            key={item.label}
            {...item}
            isActive={
              item.to === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(item.to)
            }
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
  to: string;
  isActive: boolean;
  isAnimated: boolean;
}

const NavItem = ({
  icon: Icon,
  label,
  to,
  isActive,
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
    <Link
      to={to}
      className={cn(
        "relative flex flex-1 items-center justify-center px-3 py-3 text-sm font-medium transition-colors sm:flex-none sm:px-4",
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
    </Link>
  );
};

export default AnimatedNavbar;
