import { type ReactNode } from "react";

interface DefaultLayoutProps {
  children: ReactNode;
}

/**
 * Full-width, single-column layout matching the page container.
 * Use this as the root wrapper for standard pages.
 */
export function DefaultLayout({ children }: DefaultLayoutProps) {
  return <div className="mx-auto min-w-4xl max-w-4xl space-y-8">{children}</div>;
}

export default DefaultLayout;
