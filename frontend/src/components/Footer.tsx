import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="mx-auto flex w-full max-w-5xl items-center justify-center gap-2 border-t border-border/60 px-4 py-6 text-xs text-muted-foreground">
      <span>© {new Date().getFullYear()}. Built by</span>
      <Link to="/" aria-label="Go to home page" className="transition-opacity hover:opacity-80">
        <img
          src="/images/whoisrgj_logo_invert.png"
          alt="whoisrgj.com"
          className="h-6 w-auto dark:hidden"
        />
        <img
          src="/images/whoisrgj_logo.png"
          alt="whoisrgj.com"
          className="hidden h-6 w-auto dark:block"
        />
      </Link>
    </footer>
  );
}

export default Footer;
