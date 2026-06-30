#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PREPARE_SCRIPT = Path(r"C:\Users\adv\.codex\skills\wechat-push-skill\scripts\prepare_wechat_article.py")


def run_prepare(folder: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(PREPARE_SCRIPT), str(folder)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def prefer_horizontal_cover(folder: Path, payload: dict) -> dict:
    images_dir = folder / "images"
    priority_names = [
        "01_公众号封面_标题版_2.35比1.png",
        "01_公众号封面_标题版_2.35比.png",
        "01_公众号封面_标题版_2.35比1.jpg",
        "01_公众号封面_标题版_2.35比.jpg",
        "01_公众号封面_标题版_2.35比1.jpeg",
        "01_公众号封面_标题版_2.35比.jpeg",
        "01_公众号封面_底图_2.35比1.png",
        "01_公众号封面_底图_2.35比.png",
        "01_公众号封面_底图_2.35比1.jpg",
        "01_公众号封面_底图_2.35比.jpg",
        "01_公众号封面_底图_2.35比1.jpeg",
        "01_公众号封面_底图_2.35比.jpeg",
    ]

    for name in priority_names:
        candidate = images_dir / name
        if candidate.exists():
            payload["cover_path"] = str(candidate)
            return payload

    return payload


def build_render_js(payload: dict) -> str:
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
    p.style.margin = "0 0 18px";
    p.style.lineHeight = "1.9";
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

    p.style.margin = isMajor ? "30px 0 14px" : "24px 0 12px";
    p.style.lineHeight = "1.7";
    styleSpan.style.fontSize = isMajor ? "21px" : "17px";
    styleSpan.style.color = isMajor ? "rgb(34, 55, 48)" : "rgb(130, 72, 12)";
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
    outer.style.margin = "22px 0";
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
  bodyEditor.dispatchEvent(new Event("change", {{ bubbles: true }}));

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
    parser.add_argument("folder", help="wechat article folder")
    parser.add_argument("--out-dir", help="output dir, defaults to .codex_wechat under article folder")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    out_dir = Path(args.out_dir).resolve() if args.out_dir else folder / ".codex_wechat"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = prefer_horizontal_cover(folder, run_prepare(folder))
    image_paths = [block["path"] for block in payload["blocks"] if block["type"] == "image"]
    cover_path = payload.get("cover_path")
    body_upload_paths = [p for p in image_paths if p != cover_path]
    upload_paths = list(reversed(body_upload_paths))

    (out_dir / "payload.json").write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    (out_dir / "render_body.js").write_text(build_render_js(payload), encoding="utf-8")
    (out_dir / "upload_reverse.json").write_text(
        json.dumps(upload_paths, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "folder": str(folder),
                "out_dir": str(out_dir),
                "title": payload["title"],
                "image_upload_count": len(upload_paths),
                "upload_reverse": upload_paths,
                "cover_path": cover_path,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
