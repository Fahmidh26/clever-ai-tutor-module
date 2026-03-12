"use client";

import { Fragment, type ReactNode } from "react";

type ParsedBlock =
  | { type: "text"; content: string }
  | { type: "code"; content: string; language: string }
  | { type: "math"; content: string };

function parseBlocks(input: string): ParsedBlock[] {
  const source = input || "";
  const blocks: ParsedBlock[] = [];

  const codeRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null = codeRegex.exec(source);
  while (match) {
    if (match.index > lastIndex) {
      blocks.push(...parseMathBlocks(source.slice(lastIndex, match.index)));
    }
    blocks.push({
      type: "code",
      language: (match[1] || "").trim(),
      content: (match[2] || "").trimEnd(),
    });
    lastIndex = codeRegex.lastIndex;
    match = codeRegex.exec(source);
  }
  if (lastIndex < source.length) {
    blocks.push(...parseMathBlocks(source.slice(lastIndex)));
  }
  return blocks;
}

function parseMathBlocks(input: string): ParsedBlock[] {
  const blocks: ParsedBlock[] = [];
  const mathRegex = /\$\$([\s\S]*?)\$\$/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null = mathRegex.exec(input);
  while (match) {
    if (match.index > lastIndex) {
      blocks.push({ type: "text", content: input.slice(lastIndex, match.index) });
    }
    blocks.push({ type: "math", content: (match[1] || "").trim() });
    lastIndex = mathRegex.lastIndex;
    match = mathRegex.exec(input);
  }
  if (lastIndex < input.length) {
    blocks.push({ type: "text", content: input.slice(lastIndex) });
  }
  return blocks;
}

function renderInline(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  const tokenRegex = /(`[^`]+`|\$\S[\s\S]*?\$|\*\*[^*]+\*\*|\*[^*\n]+\*)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null = tokenRegex.exec(text);
  while (match) {
    if (match.index > lastIndex) {
      parts.push(renderPlainWithBreaks(text.slice(lastIndex, match.index), `plain-${lastIndex}`));
    }
    const token = match[0];
    if (token.startsWith("`")) {
      parts.push(
        <code key={`code-${match.index}`} className="inline-code">
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("**")) {
      parts.push(<strong key={`strong-${match.index}`}>{token.slice(2, -2)}</strong>);
    } else if (token.startsWith("*")) {
      parts.push(<em key={`em-${match.index}`}>{token.slice(1, -1)}</em>);
    } else if (token.startsWith("$")) {
      parts.push(
        <span key={`math-${match.index}`} className="inline-math">
          {token.slice(1, -1)}
        </span>
      );
    } else {
      parts.push(token);
    }
    lastIndex = tokenRegex.lastIndex;
    match = tokenRegex.exec(text);
  }
  if (lastIndex < text.length) {
    parts.push(renderPlainWithBreaks(text.slice(lastIndex), `plain-tail-${lastIndex}`));
  }
  return parts;
}

function renderPlainWithBreaks(value: string, keyBase: string): ReactNode {
  const lines = value.split("\n");
  if (lines.length === 1) {
    return <Fragment key={keyBase}>{value}</Fragment>;
  }
  return (
    <Fragment key={keyBase}>
      {lines.map((line, idx) => (
        <Fragment key={`${keyBase}-${idx}`}>
          {line}
          {idx < lines.length - 1 ? <br /> : null}
        </Fragment>
      ))}
    </Fragment>
  );
}

export function MessageRenderer({ content }: { content: string }) {
  const blocks = parseBlocks(content);
  if (blocks.length === 0) {
    return null;
  }

  return (
    <div className="message-rendered">
      {blocks.map((block, index) => {
        if (block.type === "code") {
          return (
            <div key={`code-block-${index}`} className="code-block-wrap">
              {block.language ? <div className="code-block-lang">{block.language}</div> : null}
              <pre className="code-block">
                <code>{block.content}</code>
              </pre>
            </div>
          );
        }
        if (block.type === "math") {
          return (
            <pre key={`math-block-${index}`} className="math-block">
              {block.content}
            </pre>
          );
        }
        const paragraphs = block.content.split("\n\n").filter((p) => p.trim().length > 0);
        return (
          <div key={`text-block-${index}`}>
            {paragraphs.map((paragraph, pidx) => (
              <p key={`p-${index}-${pidx}`}>{renderInline(paragraph)}</p>
            ))}
          </div>
        );
      })}
    </div>
  );
}

