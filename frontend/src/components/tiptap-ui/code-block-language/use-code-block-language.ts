"use client"

import { useCallback, useEffect, useState } from "react"
import type { Editor } from "@tiptap/react"

// --- Hooks ---
import { useTiptapEditor } from "@/hooks/use-tiptap-editor"

/**
 * Configuration for the code block language functionality
 */
export interface UseCodeBlockLanguageConfig {
  /**
   * The Tiptap editor instance.
   */
  editor?: Editor | null
  /**
   * List of available languages to show in the dropdown.
   */
  languages: string[]
  /**
   * Whether to hide the dropdown when no code block is active.
   * @default true
   */
  hideWhenInactive?: boolean
}

/**
 * Gets the currently active language from the code block
 */
export function getActiveLanguage(editor: Editor | null): string | null {
  if (!editor || !editor.isEditable) return null
  return editor.getAttributes("codeBlock").language as string | null
}

/**
 * Custom hook that provides code block language selection functionality
 */
export function useCodeBlockLanguage(config?: UseCodeBlockLanguageConfig) {
  const {
    editor: providedEditor,
    languages,
    hideWhenInactive = true,
  } = config || {}

  const { editor } = useTiptapEditor(providedEditor)
  const [isVisible, setIsVisible] = useState<boolean>(true)
  const [activeLanguage, setActiveLanguage] = useState<string | null>(null)

  const isActive = editor?.isActive("codeBlock") || false

  useEffect(() => {
    if (!editor) return

    const handleSelectionUpdate = () => {
      const lang = getActiveLanguage(editor)
      setActiveLanguage(lang)
      setIsVisible(!hideWhenInactive || isActive)
    }

    handleSelectionUpdate()

    editor.on("selectionUpdate", handleSelectionUpdate)

    return () => {
      editor.off("selectionUpdate", handleSelectionUpdate)
    }
  }, [editor, hideWhenInactive, isActive])

  const handleSetLanguage = useCallback(
    (language: string) => {
      if (!editor) return
      editor.commands.toggleCodeBlock({ language })
    },
    [editor],
  )

  return {
    isVisible,
    isActive,
    activeLanguage,
    languages,
    handleSetLanguage,
  }
}
