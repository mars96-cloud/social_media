#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PREPARE_SCRIPT = Path(r"C:\Users\Administrator\.codex\skills\social-push\scripts\prepare_wechat_article.py")


def run_prepare(folder: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(PREPARE_SCRIPT), str(folder)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def build_render_js(payload: dict) -> str:
    # Use ASCII-only escapes so Windows shell piping cannot corrupt Chinese text.
    payload_json = json.dumps(payload, ensure_ascii=True)
    return f"""(() => {{
  const payload = {payload_json};
  payload.title = (payload.title || "").replace(/^\\uFEFF/, "");

  function dispatchInput(el) {{
    el.dispatchEvent(new InputEvent("input", {{
      bubbles: true,
      inputType: "insertText",
      data: ""
    }}));
  }}

  function makeParagraph(text) {{
    const section = document.createElement("section");
    const p = document.createElement("p");
    const span = document.createElement("span");
    span.setAttribute("leaf", "");
    span.textContent = text;
    p.appendChild(span);
    section.appendChild(p);
    return section;
  }}

  function makeHeading(text) {{
    const isMajor = /^[一二三四五六七八九十]+、/.test(text);
    const section = document.createElement("section");
    const p = document.createElement("p");
    const strong = document.createElement("strong");
    const styleSpan = document.createElement("span");
    const leafSpan = document.createElement("span");

    styleSpan.style.fontSize = isMajor ? "22px" : "16px";
    styleSpan.style.color = isMajor ? "rgb(34, 55, 48)" : "rgb(214, 106, 0)";
    leafSpan.setAttribute("leaf", "");
    leafSpan.textContent = text;

    styleSpan.appendChild(leafSpan);
    strong.appendChild(styleSpan);
    p.appendChild(strong);
    section.appendChild(p);
    return section;
  }}

  function makeImage(imgSection) {{
    const outer = document.createElement("section");
    outer.appendChild(imgSection.cloneNode(true));
    return outer;
  }}

  const editors = Array.from(document.querySelectorAll(".ProseMirror"));
  if (editors.length < 2) {{
    throw new Error("WeChat editor not found");
  }}

  const titleEditor = editors[0];
  const bodyEditor = editors[editors.length - 1];

  titleEditor.innerHTML = "";
  titleEditor.textContent = payload.title;
  dispatchInput(titleEditor);

  const uploadedImageSections = Array.from(
    bodyEditor.querySelectorAll("img.rich_pages.wxw-img.js_insertlocalimg")
  ).map((img) => {{
    const nodeleaf = img.closest("section[nodeleaf]");
    if (nodeleaf) return nodeleaf.cloneNode(true);
    const parentSection = img.closest("section");
    if (parentSection) return parentSection.cloneNode(true);
    throw new Error("Uploaded image section not found");
  }});

  bodyEditor.innerHTML = "";
  let imageIndex = 0;

  for (const block of payload.blocks) {{
    if (block.type === "paragraph") {{
      bodyEditor.appendChild(makeParagraph(block.text));
      continue;
    }}
    if (block.type === "heading") {{
      bodyEditor.appendChild(makeHeading(block.text));
      continue;
    }}
    if (block.type === "image") {{
      const imgSection = uploadedImageSections[imageIndex];
      if (!imgSection) {{
        throw new Error(`Missing uploaded image for block index ${{imageIndex}}`);
      }}
      bodyEditor.appendChild(makeImage(imgSection));
      imageIndex += 1;
      continue;
    }}
    throw new Error(`Unsupported block type: ${{block.type}}`);
  }}

  dispatchInput(bodyEditor);

  return JSON.stringify({{
    title: payload.title,
    uploadedImageCount: uploadedImageSections.length,
    usedImageCount: imageIndex,
    blockCount: payload.blocks.length,
    bodyPreview: bodyEditor.innerText.slice(0, 200)
  }}, null, 2);
}})();
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="公众号文章文件夹")
    parser.add_argument("--out-dir", help="输出目录，默认写到文章文件夹下的.codex_wechat")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else folder / ".codex_wechat"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = run_prepare(folder)
    image_paths = [block["path"] for block in payload["blocks"] if block["type"] == "image"]
    upload_paths = list(reversed(image_paths))

    (out_dir / "payload.json").write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    (out_dir / "render_body.js").write_text(build_render_js(payload), encoding="utf-8")
    (out_dir / "upload_reverse.json").write_text(
        json.dumps(upload_paths, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({
        "folder": str(folder),
        "out_dir": str(out_dir),
        "title": payload["title"],
        "image_upload_count": len(upload_paths),
        "upload_reverse": upload_paths,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
