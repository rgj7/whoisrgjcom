import { StarterKit } from "@tiptap/starter-kit";
import { Image } from "@tiptap/extension-image";
import { TaskItem, TaskList } from "@tiptap/extension-list";
import { TextAlign } from "@tiptap/extension-text-align";
import { Typography } from "@tiptap/extension-typography";
import { Highlight } from "@tiptap/extension-highlight";
import { Subscript } from "@tiptap/extension-subscript";
import { Superscript } from "@tiptap/extension-superscript";
import { Selection } from "@tiptap/extensions";
import { HorizontalRule } from "@/components/tiptap-node/horizontal-rule-node/horizontal-rule-node-extension";
import { ImageUploadNode } from "@/components/tiptap-node/image-upload-node/image-upload-node-extension";
import { MAX_FILE_SIZE, handleImageUpload } from "@/lib/tiptap-utils";
import { renderToReactElement } from "@tiptap/static-renderer/pm/react";
import type { Extensions, JSONContent } from "@tiptap/core";

// Import editor node CSS so rendered post content gets the same styles
import "@/components/tiptap-node/blockquote-node/blockquote-node.css";
import "@/components/tiptap-node/code-block-node/code-block-node.css";
import "@/components/tiptap-node/horizontal-rule-node/horizontal-rule-node.css";
import "@/components/tiptap-node/list-node/list-node.css";
import "@/components/tiptap-node/image-node/image-node.css";
import "@/components/tiptap-node/heading-node/heading-node.css";
import "@/components/tiptap-node/paragraph-node/paragraph-node.css";

const postExtensions: Extensions = [
  StarterKit.configure({
    horizontalRule: false,
    link: {
      openOnClick: false,
      enableClickSelection: true,
    },
  }),
  HorizontalRule,
  TextAlign.configure({ types: ["heading", "paragraph"] }),
  TaskList,
  TaskItem.configure({ nested: true }),
  Highlight.configure({ multicolor: true }),
  Image,
  Typography,
  Superscript,
  Subscript,
  Selection,
  ImageUploadNode.configure({
    accept: "image/*",
    maxSize: MAX_FILE_SIZE,
    limit: 3,
    upload: handleImageUpload,
    onError: (error) => console.error("Upload failed:", error),
  }),
] as Extensions;

export function renderPostContent(content: JSONContent): React.ReactNode {
  return (
    <div className="tiptap ProseMirror">
      {renderToReactElement({
        extensions: postExtensions,
        content,
      })}
    </div>
  );
}
