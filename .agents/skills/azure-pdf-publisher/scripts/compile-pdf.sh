#!/usr/bin/env bash
# =============================================================================
# compile-pdf.sh: Automated compilation and verification pipeline for A4 PDFs
# =============================================================================
set -euo pipefail

HTML_FILE="${1:-}"
PDF_FILE="${2:-}"

if [[ -z "$HTML_FILE" ]]; then
  echo "Usage: $0 <input.html> [output.pdf]"
  exit 1
fi

if [[ -z "$PDF_FILE" ]]; then
  PDF_FILE="${HTML_FILE%.html}.pdf"
fi

CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if [[ ! -x "$CHROME_BIN" ]]; then
  echo "Error: Google Chrome not found at '$CHROME_BIN'"
  exit 1
fi

mkdir -p "$(dirname "$PDF_FILE")"
HTML_ABS_PATH="$(cd "$(dirname "$HTML_FILE")" && pwd)/$(basename "$HTML_FILE")"
PDF_ABS_PATH="$(cd "$(dirname "$PDF_FILE")" && pwd)/$(basename "$PDF_FILE")"

echo "==> Compiling HTML to PDF using Chrome Headless..."
echo "    Source: $HTML_ABS_PATH"
echo "    Target: $PDF_ABS_PATH"

"$CHROME_BIN" --headless --disable-gpu --print-to-pdf="$PDF_ABS_PATH" "file://$HTML_ABS_PATH"

if [[ ! -f "$PDF_ABS_PATH" ]]; then
  echo "Error: PDF was not generated at '$PDF_ABS_PATH'"
  exit 1
fi

PAGE_COUNT=$(python3 -c "
with open('$PDF_ABS_PATH', 'rb') as f:
    import re
    pages = re.findall(rb'/Type\s*/Page[^s]', f.read())
    print(len(pages))
")

echo "==> Compilation successful. Total Pages: $PAGE_COUNT"

echo "==> Rasterizing pages for visual verification using Swift/PDFKit..."
swift -e "
import Foundation
import PDFKit
import AppKit

let pdfURL = URL(fileURLWithPath: \"$PDF_ABS_PATH\")
guard let doc = PDFDocument(url: pdfURL) else { exit(1) }
let outDir = URL(fileURLWithPath: \"$(dirname "$PDF_ABS_PATH")\")

for i in 0..<doc.pageCount {
    guard let page = doc.page(at: i) else { continue }
    let rect = page.bounds(for: .mediaBox)
    let renderer = NSImage(size: rect.size)
    renderer.lockFocus()
    guard let ctx = NSGraphicsContext.current?.cgContext else { continue }
    ctx.setFillColor(NSColor.white.cgColor)
    ctx.fill(rect)
    page.draw(with: .mediaBox, to: ctx)
    renderer.unlockFocus()

    if let tiff = renderer.tiffRepresentation,
       let rep = NSBitmapImageRep(data: tiff),
       let png = rep.representation(using: .png, properties: [:]) {
        let path = outDir.appendingPathComponent(String(format: \".verify_page_%d.png\", i + 1))
        try? png.write(to: path)
    }
}
print(\"    Rendered \(doc.pageCount) verification thumbnail(s) into \(outDir.path)\")
"

echo "==> Ready for inspection. Run clean-up when done: rm -f \"$(dirname "$PDF_ABS_PATH")\"/.verify_page_*.png"
