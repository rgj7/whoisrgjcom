import { type ReactNode } from "react";

interface LoginLayoutProps {
  children: ReactNode;
  title: string;
  description: string;
}

export function LoginLayout({ children, title, description }: LoginLayoutProps) {
  return (
    <div className="page-scroll-container flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm">
        {children}
        <p className="mt-6 text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} whoisrgj.com
        </p>
      </div>
    </div>
  );
}
