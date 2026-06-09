import { StarterKit } from "@tiptap/starter-kit";
import { Image } from "@tiptap/extension-image";
import { TaskItem, TaskList } from "@tiptap/extension-list";
import { TextAlign } from "@tiptap/extension-text-align";
import { Typography } from "@tiptap/extension-typography";
import { Highlight } from "@tiptap/extension-highlight";
import { Subscript } from "@tiptap/extension-subscript";
import { Superscript } from "@tiptap/extension-superscript";
import { Selection } from "@tiptap/extensions";
import { Youtube } from "@tiptap/extension-youtube";
import { Node } from "@tiptap/core";
import { HorizontalRule } from "@/components/tiptap-node/horizontal-rule-node/horizontal-rule-node-extension";
import { PostImageLightbox } from "@/components/PostImageLightbox";
import { createElement } from "react";
import { renderToReactElement } from "@tiptap/static-renderer/pm/react";
import type { Extensions, JSONContent } from "@tiptap/core";
import hljs from "highlight.js";

const CodeBlockNoRender = Node.create({
  name: "codeBlock",
  content: "text*",
  group: "block",
  code: true,
  defining: true,

  addAttributes() {
    return {
      language: {
        default: null,
        parseHTML: element => {
          const codeEl = element.querySelector("code");
          if (!codeEl) return null;
          const classList = [...codeEl.classList];
          const match = classList.find(c => c.startsWith("language-"));
          return match ? match.replace("language-", "") : null;
        },
        rendered: false,
      },
    };
  },
});

function highlightCodeBlock(props: any): React.ReactNode {
  const node = props.node;
  const text = node.textContent || "";
  const language = node.attrs?.language || "plaintext";
  const highlighted =
    language === "plaintext"
      ? text
      : hljs.highlight(text, { language }).value;

  if (language === "plaintext") {
    return createElement(
      "pre",
      { className: "tiptap-code-block" },
      createElement("code", { className: "hljs", "data-language": language }, text),
    );
  }

  return createElement(
    "pre",
    { className: "tiptap-code-block" },
    createElement("code", { className: "hljs", "data-language": language, dangerouslySetInnerHTML: { __html: highlighted } }),
  );
}

const postExtensions: Extensions = [
  StarterKit.configure({
    horizontalRule: false,
    codeBlock: false,
    link: {
      openOnClick: false,
      enableClickSelection: true,
    },
  }),
  CodeBlockNoRender,
  HorizontalRule,
  TextAlign.configure({ types: ["heading", "paragraph"] }),
  TaskList,
  TaskItem.configure({ nested: true }),
  Highlight.configure({ multicolor: true }),
  Image,
  Youtube.configure({
    nocookie: true,
    controls: true,
    autoplay: false,
    allowFullscreen: true,
  }),
  Typography,
  Superscript,
  Subscript,
  Selection,
] as Extensions;

export function renderPostContent(content: JSONContent): React.ReactNode {
  return (
    <div className="tiptap ProseMirror">
      {renderToReactElement({
        extensions: postExtensions,
        content,
        options: {
          nodeMapping: {
            codeBlock: (node: any) => highlightCodeBlock(node),
            image: (props: any) => {
              const attrs = props.node.attrs;
              return createElement(PostImageLightbox, {
                src: attrs.src,
                alt: attrs.alt,
                title: attrs.title,
              });
            },
          },
        },
      })}
    </div>
  );
}
