import { XIcon } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface PostImageLightboxProps {
  src: string;
  alt?: string | null;
  title?: string | null;
}

export function PostImageLightbox({ src, alt, title }: PostImageLightboxProps) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const caption = alt?.trim();

  const close = useCallback(() => {
    setOpen(false);
    requestAnimationFrame(() => triggerRef.current?.focus());
  }, []);

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    closeButtonRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") close();
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, close]);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        className="group my-8 block max-w-full cursor-zoom-in rounded-sm border-0 bg-transparent p-0 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        aria-label={caption ? `Open image: ${caption}` : "Open image"}
        onClick={() => setOpen(true)}
      >
        <img
          src={src}
          alt={alt ?? ""}
          title={title ?? undefined}
          className="transition-opacity group-hover:opacity-95"
        />
      </button>

      {open &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            aria-label={caption ? `Image: ${caption}` : "Image lightbox"}
            onClick={close}
          >
            <button
              ref={closeButtonRef}
              type="button"
              className="absolute right-4 top-4 inline-flex size-10 items-center justify-center rounded-full bg-background/90 text-foreground shadow-lg transition-colors hover:bg-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-black"
              aria-label="Close image lightbox"
              onClick={close}
            >
              <XIcon className="size-5" aria-hidden="true" />
            </button>

            <figure
              className="flex max-h-[90vh] max-w-[min(96vw,72rem)] flex-col items-center gap-3"
              onClick={(event) => event.stopPropagation()}
            >
              <img
                src={src}
                alt={alt ?? ""}
                title={title ?? undefined}
                className="max-h-[85vh] max-w-full rounded-lg object-contain shadow-2xl"
              />
              {caption && (
                <figcaption className="max-w-3xl text-center text-sm text-white/85">
                  {caption}
                </figcaption>
              )}
            </figure>
          </div>,
          document.body,
        )}
    </>
  );
}
