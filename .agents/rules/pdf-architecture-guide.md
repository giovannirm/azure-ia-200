# Harness Engineering Protocol: Technical PDF & Lab Documentation

This harness defines the mandatory engineering protocol for authoring, structuring, and publishing technical lab guides, architecture documents, and PDF manuals across the Azure certification and cloud curriculum.

---

## 1. Scope & Core Objectives
Every technical document generated in this workspace must fulfill the following architectural and structural criteria:
1. **Curriculum Enumeration & Directory Structure:** Organized under `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`, where `<N>` strictly matches the course lesson index.
2. **Universal Execution Context:** Decoupled from transient lab virtual machines.
3. **Command Anatomy & Didactic Explanations:** Deep explanation of Azure CLI / Bash / PowerShell syntax for all skill levels.
4. **Exhaustive Code & Asset Breakdown:** Line-by-line architectural analysis of all project files and scripts.
5. **High-Yield Certification Exam Q&A Bank:** Real-world scenario questions with comprehensive technical justifications.

---

## 2. Directory Structure & Curriculum Enumeration Protocol

All printable documents and compiled artifacts in `PDFs/` MUST strictly mirror the module numbering of the course:

```text
PDFs/
├── 1/
│   ├── 1. Azure CLI y ACR Tasks.html
│   └── 1. Azure CLI y ACR Tasks.pdf
├── 2/
│   ├── 2. Azure App Service.html
│   └── 2. Azure App Service.pdf
└── <N>/
    ├── <N>. <Topic Name>.html
    └── <N>. <Topic Name>.pdf
```

### Alignment Matrix Across Workspace:
- **PDF Artifacts:** `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`
- **Obsidian Lesson Vault:** `OBSIDIAN/LESSON <N>/`
- **Class Videos:** `videos/<N>. <Topic>.mp4`
- **Lab Code:** `CODE/<N>. <Project-Name>/`
- **Presentation Slides:** `PPTs/AI-200 PARTE <X>.pptx` (Module `<N>`)

### Non-Negotiable Naming Rules:
1. **Never Save in Root `PDFs/`:** Files must ALWAYS reside in their corresponding numerical folder `PDFs/<N>/`.
2. **File Prefix Consistency:** The HTML and PDF filename must start with `<N>. ` matching the parent folder `<N>`.
3. **Automatic Folder Creation:** If generating documentation for lesson `<N>` and `PDFs/<N>/` does not exist, create the directory prior to writing.

---

## 3. Document Architecture & Content Standards

### Criterion 1: Universal Execution Context (Decouple from VMs)
- **Eliminate Lab VM Ephemera:** Never include VM login credentials (`Admin`, `Pa55w.rd`), ephemeral lab desktop access steps, or Cloud Express Pass tabs unless specifically requested by the user.
- **Universal Prerequisites:** Frame setup around standard developer workstations (macOS, Linux, WSL, PowerShell) and Azure Cloud Shell:
  - Active Azure Subscription (highlighting ACR Tasks Pay-As-You-Go requirement).
  - Azure CLI version (e.g., `az --version` >= 2.50).
  - Runtime dependencies (e.g., Python 3.10+).
  - Identity & RBAC roles (`Contributor`, `AcrPush`, `AcrPull`).
- **Cloud-Native Value Proposition:** Explicitly highlight the operational advantage (e.g., *zero local Docker daemon* required with ACR Tasks).

### Criterion 2: Azure CLI Command Anatomy (Beginner-Friendly)
- **Hierarchical Syntax Pattern:** Always introduce the command anatomy:
  `az <service> <subgroup> <action> [--parameters]`
- **Flag Glossary:** Document every flag used:
  - Lifecycle flags (`--resource-group` / `-g`, `--name` / `-n`, `--location` / `-l`).
  - Service-specific targets (`--registry`, `--image`, `--sku`).
  - Output formatting (`--output table|json|tsv`).
  - Client-side queries (`--query` with JMESPath expressions).
  - Automation flags (`--no-wait`, `--yes` / `-y`).
- **Cross-Shell Discipline:** Provide side-by-side multiline syntax:
  - PowerShell: Line continuation with backtick (`` ` ``).
  - Bash/Zsh/macOS: Line continuation with backslash (`\`).
- **Provider Registration:** Explain *why* resource providers must be registered (e.g., `Microsoft.ContainerRegistry`).

### Criterion 3: Exhaustive Source Code Breakdown
- For any lab or downloaded code (e.g., `azdeploy.py`, `Dockerfile`, `app.py`):
  - **Automation Scripts:** Explain executable resolution across OSs, identity retrieval via Entra ID, cryptographic hashing for globally unique DNS endpoints (`<name>.azurecr.io`), idempotency checks, and clean multi-shell environment generation (`.env` and `.env.ps1`).
  - **Container Definitions (`Dockerfile`):** Explain base image selection (`python:3.11-slim`), layer caching hygiene (`--no-cache-dir`), decoupled configuration via `ENV`, and exposed networking.
  - **Application Microservices (`app.py`):** Detail each endpoint (`/health` probes for orchestrator liveness/readiness, `/predict` simulated inference with confidence scoring, `/` discovery), and the necessity of binding to `0.0.0.0`.

### Criterion 4: Certification Exam Q&A Bank (AI-200 / AI-102 / AZ-204)
- Dedicate a full page or section to official exam-grade questions:
  - **Structure:** Scenario Description -> Multiple Choice (A, B, C, D) -> Correct Key -> Detailed Technical Rationale.
  - **Rationale Quality:** Must explain both *why* the correct answer is architecturally valid and *why each distractor fails* according to Microsoft official documentation.
  - **Core Exam Focus Areas:**
    - Serverless container compilation without local Docker (`az acr build`).
    - Immutability and production protection (`--write-enabled false` and SHA-256 Digest references).
    - Automated base image patching triggers (ACR Tasks Base Image Update Trigger).
    - Ephemeral cloud validation (`az acr run --cmd ... /dev/null`).
    - ACR naming rules and global DNS restrictions.

---

## 4. Strict Layout & Print Budgeting Protocol

### CSS & Page Layout Rules
Every printable HTML document must follow these physical constraints:
```css
@page {
  size: A4 portrait;
  margin: 0;
}

.page {
  width: 210mm;
  height: 297mm;
  max-height: 297mm;
  overflow: hidden;
  margin: 0 auto;
  background: #ffffff;
  padding: 7.5mm 12mm 5.5mm 12mm;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  page-break-after: always;
  break-after: page;
  position: relative;
}
```

### Layout Hygiene Checklist
1. **Zero Vertical Overflow:** Content inside each `.page` must fit comfortably within the 297mm budget. Never let cards or terminal boxes cross over into an unplanned page.
2. **Explicit Page Numbering:** Every page footer must state: `PÁGINA X DE N`.
3. **Contrast & Theme:** Use Azure enterprise palette:
   - Primary: `#0078d4` (Azure Blue).
   - Backgrounds: `#ffffff` for paper, `#f8fafc` for cards, `#0f172a` for terminal windows.
   - Accents: `#16a34a` (Success/Verified), `#d97706` (Warning), `#7c3aed` (Governance/OCI).
   - Monospace: `'JetBrains Mono', monospace` for all code and commands.

---

## 5. Compilation & Verification Pipeline

### Compilation Command
Compile HTML to PDF using the automated harness script or headless Chromium/Google Chrome:
```bash
# Recommended: Harness automated script with validation & thumbnail generation
./.agents/skills/azure-pdf-publisher/scripts/compile-pdf.sh "PDFs/<N>/<N>. <Topic Name>.html"

# Direct headless Chrome invocation:
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf="PDFs/<N>/<N>. <Topic Name>.pdf" \
  "file://$(pwd)/PDFs/<N>/<N>. <Topic Name>.html"
```

### Visual Verification Gate
Before presenting any generated PDF to the user:
1. Verify total page count matches the intended page budget:
   ```bash
   python3 -c "import re; pages = re.findall(rb'/Type\s*/Page[^s]', open('output.pdf', 'rb').read()); print(len(pages))"
   ```
2. Rasterize pages to PNG using the native Swift/PDFKit tool and inspect with `view_file` to verify text alignment, padding, and zero clipping.
