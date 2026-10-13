---
name: azure-pdf-publisher
description: >-
  Standardized protocol to author, format, compile, and visually verify enterprise A4 lab guides and technical documentation PDFs in Azure AI-200.
---

# Azure PDF Publisher & Lab Documentation Protocol

Use this skill whenever authoring, updating, or compiling technical PDFs or lab guides for Azure AI-200.

---

## 1. Curriculum Enumeration & Directory Structure

All documents MUST be organized according to the course lesson enumeration:
- **Target Folder:** `PDFs/<N>/` where `<N>` is the lesson number (e.g., `1`, `2`, `3`).
- **File Names:** `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`.
- **Cross-Workspace Alignment:**
  - `PDFs/<N>/<N>. <Topic Name>.html`
  - `OBSIDIAN/LESSON <N>/`
  - `videos/<N>. <Topic>.mp4`
  - `CODE/<N>. <Project-Name>/`
  - `PPTs/` (Module `<N>`)

### Authoring Step 0 (Pre-flight):
Before creating any files:
1. Identify the module index `<N>` from the user request or the curriculum structure (`PDFs/`, `OBSIDIAN/`, `videos/`).
2. Verify that directory `PDFs/<N>/` exists. If not, create it: `mkdir -p "PDFs/<N>"`.
3. Never write HTML or PDF files directly to the root of `PDFs/`.

---

## 2. Document Authoring Criteria

Whenever creating or editing a lab document (HTML/PDF):
1. **Decouple from Lab VMs:**
   - Omit `Admin` / `Pa55w.rd` and virtual lab UI navigation.
   - Specify universal prerequisites: Azure CLI 2.50+, Python 3.10+, RBAC permissions (`Contributor`, `AcrPush`), and subscription support.
   - Emphasize cloud-native value (e.g., zero local Docker daemon).
2. **Beginner-Friendly Command Explanations:**
   - Explain the hierarchy: `az <service> <subgroup> <action> [--parameters]`.
   - Provide a table explaining all flags used (`--resource-group`, `--name`, `--registry`, `--image`, `--output`, `--query`, `--no-wait`, etc.).
   - Explicitly document PowerShell (`` ` ``) vs Bash (`\`) line-continuation syntax.
3. **Exhaustive Source Code Breakdown:**
   - Analyze all project files (`azdeploy.py`, `Dockerfile`, `app.py`).
   - Detail the architectural reasoning (DNS global uniqueness requiring SHA-1 hashing, slim base images, `--no-cache-dir`, decoupled `ENV` configuration, health probes for container orchestrators).
4. **Certification Exam Q&A Bank:**
   - Include high-yield multiple-choice questions aligned with AI-200 / AI-102 / AZ-204.
   - Provide clear keys and in-depth rationales for correct answers and distractors.

---

## 3. Page Budget & Layout Hygiene

Strict A4 page constraints:
- `.page { width: 210mm; height: 297mm; max-height: 297mm; overflow: hidden; padding: 7.5mm 12mm 5.5mm 12mm; display: flex; flex-direction: column; justify-content: space-between; page-break-after: always; }`
- Budget exactly N pages and ensure every page has a header, content, and footer: `PÁGINA X DE N`.
- Verify zero overflow before delivery.

---

## 4. Automated Compilation & Verification

Use the bundled compilation script:
```bash
./.agents/skills/azure-pdf-publisher/scripts/compile-pdf.sh "PDFs/<N>/<N>. <Topic Name>.html"
```

The script:
1. Calls headless Google Chrome with `--print-to-pdf` outputting directly into `PDFs/<N>/<N>. <Topic Name>.pdf`.
2. Validates the generated page count against the budget.
3. Uses native Swift/PDFKit to render `.verify_page_*.png` thumbnails in `PDFs/<N>/`.
4. Allows inspecting thumbnails with `view_file` to verify zero clipping or styling bugs before cleaning up.
5. Clean up temporary thumbnails once verified: `rm -f "PDFs/<N>/.verify_page_*.png"`.

