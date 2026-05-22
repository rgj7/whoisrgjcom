"use client"

import { forwardRef, useCallback, useState } from "react"

// --- Icons ---
import { Code2Icon } from "@/components/tiptap-icons/code2-icon"
import { ChevronDownIcon } from "@/components/tiptap-icons/chevron-down-icon"

// --- Hooks ---
import { useCodeBlockLanguage } from "@/components/tiptap-ui/code-block-language"

// --- UI Primitives ---
import type { ButtonProps } from "@/components/tiptap-ui-primitive/button"
import { Button } from "@/components/tiptap-ui-primitive/button"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuGroup,
} from "@/components/tiptap-ui-primitive/dropdown-menu"

/**
 * Props for the language dropdown component
 */
export interface LanguageDropdownProps extends ButtonProps {
  /**
   * List of available languages to show in the dropdown.
   */
  languages: string[]
  /**
   * Whether to hide the dropdown when no code block is active.
   * @default true
   */
  hideWhenInactive?: boolean
  /**
   * Callback for when the dropdown opens or closes
   */
  onOpenChange?: (isOpen: boolean) => void
}

/**
 * Dropdown menu component for selecting the language of a code block in a Tiptap editor.
 *
 * Shows when a code block is active, allowing users to pick a language for syntax highlighting.
 */
export const LanguageDropdown = forwardRef<
  HTMLButtonElement,
  LanguageDropdownProps
>(
  (
    {
      languages,
      hideWhenInactive = true,
      onOpenChange,
      ...buttonProps
    },
    ref,
  ) => {
    const [isOpen, setIsOpen] = useState<boolean>(false)

    const {
      isVisible,
      isActive,
      activeLanguage,
      handleSetLanguage,
    } = useCodeBlockLanguage({
      languages,
      hideWhenInactive,
    })

    const handleOpenChange = useCallback(
      (open: boolean) => {
        setIsOpen(open)
        onOpenChange?.(open)
      },
      [onOpenChange],
    )

    const handleSelectLanguage = useCallback(
      (language: string) => {
        handleSetLanguage(language)
      },
      [handleSetLanguage],
    )

    if (!isVisible) {
      return null
    }

    const displayLabel = activeLanguage
      ? activeLanguage.charAt(0).toUpperCase() + activeLanguage.slice(1)
      : "Auto"

    return (
      <DropdownMenu
        modal={false}
        open={isOpen}
        onOpenChange={handleOpenChange}
      >
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            data-active-state={isActive ? "on" : "off"}
            role="button"
            tabIndex={-1}
            aria-label="Code block language"
            tooltip="Code Block Language"
            {...buttonProps}
            ref={ref}
          >
            <Code2Icon className="tiptap-button-icon" />
            <span className="tiptap-button-text">{displayLabel}</span>
            <ChevronDownIcon className="tiptap-button-dropdown-small" />
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="start">
          <DropdownMenuGroup>
            {/* "Auto" option — removes language attribute */}
            <DropdownMenuItem asChild>
              <button
                type="button"
                data-active-item={activeLanguage === null}
                onClick={() => handleSelectLanguage("plaintext")}
              >
                <span className="tiptap-dropdown-menu-item-indicator">
                  {activeLanguage === null ? (
                    <span className="tiptap-dropdown-menu-item-check">
                      <span className="tiptap-dropdown-menu-item-check-icon" />
                    </span>
                  ) : null}
                </span>
                Auto
              </button>
            </DropdownMenuItem>

            {/* Language options */}
            {languages.map((lang) => (
              <DropdownMenuItem key={lang} asChild>
                <button
                  type="button"
                  data-active-item={activeLanguage === lang}
                  onClick={() => handleSelectLanguage(lang)}
                >
                  <span className="tiptap-dropdown-menu-item-indicator">
                    {activeLanguage === lang ? (
                      <span className="tiptap-dropdown-menu-item-check">
                        <span className="tiptap-dropdown-menu-item-check-icon" />
                      </span>
                    ) : null}
                  </span>
                  {lang.charAt(0).toUpperCase() + lang.slice(1)}
                </button>
              </DropdownMenuItem>
            ))}
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    )
  },
)

LanguageDropdown.displayName = "LanguageDropdown"

export default LanguageDropdown
