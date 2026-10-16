# Harness Engineering Protocol: Technical PDF & Lab Documentation

This harness defines the mandatory engineering protocol for authoring, structuring, formatting, and publishing technical lab guides, architecture documents, and PDF manuals across the Azure certification and cloud curriculum (specifically tailored for **Azure AI-200: Microsoft Certified: Azure AI Cloud Developer Associate**).

Every document must achieve the gold-standard quality established in `PDFs/1/1. Azure CLI y ACR Tasks.html`.

---

## 1. Scope & Core Architectural Principles

Every technical guide in this repository is an enterprise-grade learning asset. It must never read like a raw script dump or an ephemeral lab handout. It must strictly adhere to:
1. **Curriculum Enumeration & Directory Mirroring:** Organized under `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`.
2. **Official Microsoft Learn Alignment:** Explicit integration of the official course (`AI-200T00-A: Desarrollo de soluciones en la nube de IA en Azure`), certification exam (`AI-200`), and official Study Guide domain weightings.
3. **Universal Execution Context:** Decoupled from transient lab virtual machines (`Admin` / `Pa55w.rd`) and cloud pass sandboxes.
4. **Didactic Command Anatomy & GUI Walkthroughs:** Exhaustive parameter breakdowns (PowerShell vs Bash) combined with Azure Portal GUI navigation steps.
5. **Dual Architecture Blueprints with Official Azure Icons:** Dedicated Logical Architecture Diagram (business use case & flow) AND dedicated Physical Architecture & Network Topology Diagram (TLS 1.3, Private Endpoints, Data Endpoints, RBAC). Never invent icons; use official Azure SVGs.
6. **Exhaustive Code & Asset Breakdown:** Line-by-line architectural dissection of all automation scripts, Dockerfiles, and application microservices.
7. **Certification Exam Q&A Bank & Skills Matrix:** Inclusion of official exam scenario questions and the 4-Domain Weighting Matrix from the AI-200 Study Guide.
8. **Normative Technical Glossary, Acronym Dictionary & 9-Module Roadmap:** Mandatory concluding page with architectural concepts, 2-column acronym dictionary, and the complete 9-module curriculum learning path.
9. **Physical Page Budgeting & Zero-Clipping Layout:** Exact A4 dimensions with `PÁGINA X DE N` footers and strict vertical containment.
10. **Automated Compilation & Visual Verification Gate:** Headless Chrome compilation and Swift/PDFKit thumbnail inspection before delivery.

---

## 2. Directory Structure & Curriculum Enumeration Protocol

All printable documents and compiled artifacts in `PDFs/` MUST strictly mirror the module numbering of the course:

```text
PDFs/
├── assets/
│   └── icons/              <-- Shared official Azure SVG vector icons
├── 1/
│   ├── 1. Azure CLI y ACR Tasks.html
│   └── 1. Azure CLI y ACR Tasks.pdf
├── 2/
│   ├── 2. Azure App Service.html
│   └── 2. Azure App Service.pdf
├── 3/
│   ├── 3. Azure Container Apps.html
│   └── 3. Azure Container Apps.pdf
└── <N>/
    ├── <N>. <Topic Name>.html
    └── <N>. <Topic Name>.pdf
```

### Workspace Cross-Alignment Matrix:
- **PDF Artifacts:** `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`
- **Obsidian Lesson Vault:** `OBSIDIAN/LESSON <N>/`
- **Class Videos:** `videos/<N>. <Topic>.webloc` / `videos/<N>. <Topic>.url` / `videos/<N>. <Topic>.mp4`
- **Lab Source Code:** `CODE/<N>. <Project-Name>/`
- **Presentation Slides:** `PPTs/AI-200 PARTE <X>.pptx` (Module `<N>`)

### Non-Negotiable Naming Rules:
1. **Never Save in Root `PDFs/`:** Files must ALWAYS reside in their corresponding numerical folder `PDFs/<N>/`.
2. **File Prefix Consistency:** The HTML and PDF filename must start with `<N>. ` matching the parent folder `<N>`.
3. **Automatic Folder Creation:** If generating documentation for lesson `<N>` and `PDFs/<N>/` does not exist, create the directory prior to writing: `mkdir -p "PDFs/<N>"`.

---

## 3. Mandatory Document Anatomy & Structural Blueprint

Every lab guide must contain the following structural components in logical order:

### 3.1. Page 1: Portada, Metadatos Oficiales y Fase 1
- **Header Badge:** `AZURE AI-200 / AI-102 • GUÍA GENERAL DE LABORATORIO Y ARQUITECTURA`.
- **Title & Subtitle:** Clear module title and subtitle summarizing cloud-native competencies.
- **Alineación Curricular Oficial Microsoft Learn (Banner):**
  - Course Title: `Curso AI-200T00-A: Desarrollo de soluciones en la nube de IA en Azure` (5 días / 120 hrs).
  - Associated Certification: `Microsoft Certified: Azure AI Cloud Developer Associate (Examen AI-200)`.
  - Specific Exam Domain & Weighting (e.g., `Dominio 1: Desarrollo de soluciones en contenedores en Azure (20% – 25%)`).
  - Clickable link to official Microsoft Learn Study Guide: `https://learn.microsoft.com/es-es/credentials/certifications/resources/study-guides/ai-200`.
- **Universal Prerequisites & Critical Azure Notices (2-Column Grid):**
  - *Prerequisites:* Azure Subscription (Pay-As-You-Go), Azure CLI 2.50+, Python 3.10+, RBAC roles (`Contributor`, `AcrPush`), zero local Docker daemon.
  - *Critical Notices:* Subscription tier limits, DNS global uniqueness, CLI propagation latency, PowerShell (`` ` ``) vs Bash (`\`) line continuation.
- **Starter Project Structure (Banner):** Location and file inventory in `CODE/<N>. <project>/`.
- **Anatomía de Comandos Azure CLI (Didactic Table):**
  - Hierarchy pattern: `az <service> <subgroup> <action> [--parameters]`.
  - Table explaining flags: `--resource-group` (`-g`), `--name` (`-n`), `--registry`, `--image`, `--output` (`-o`), `--query` (JMESPath), `--no-wait`, etc.
- **Fase 1: Preparación del Entorno:** Resource Provider registration (`az provider register --namespace ...`), identity authentication (`az login`), and **Azure Portal GUI Inspection steps** (Subscriptions -> Resource providers -> Status check).

### 3.2. Intermediate Pages: Ejecución Técnica, Automatización y Portal GUI
- **Step-by-Step Practical Phases:** Modular task cards with:
  - Command syntax in styled terminal boxes (`cmd`, `flag`, `val`, `comment`).
  - Dual-shell syntax (PowerShell backtick vs Bash backslash).
  - Explicit explanation of *why* each flag or command is executed.
- **Dual Verification (CLI + Azure Portal):**
  - For every major cloud resource created (registries, tasks, web apps, clústeres), document both the CLI verification command AND the step-by-step Azure Portal GUI navigation (Search bar -> Blade menus -> Settings -> Repositories -> Webhooks -> Task Runs).

### 3.3. Architecture Blueprint Pages (Logical & Physical)
Every guide must include **two distinct, dedicated architecture blueprint pages**:
1. **Diagrama de Arquitectura Lógica (Página dedicada):**
   - *Caso de Uso y Problemática Empresarial:* Real-world business problem (e.g., fragmented builds across developer machines, security vulnerabilities, lack of auditing).
   - *Flujo Lógico:* Step-by-step data and instruction flow from developer commit to serverless build, container storage, and deployment.
   - *Canvas de Arquitectura:* Draw.io style layout featuring clear visual zones (Estación de Desarrollo, Servicio Administrado en la Nube, Consumidores Downstream, Gobernanza & Seguridad).
   - *Iconografía Oficial:* **Mandatory use of official Azure SVG vector icons** sourced from the centralized repository `PDFs/assets/icons/`. **NEVER duplicate assets inside individual lesson directories, and NEVER invent or draw generic/fake icons.** Embed icons cleanly via base64 data URIs or inline SVG.
2. **Diagrama de Arquitectura Física y Topología de Red (Página dedicada):**
   - *Frontera de Red y Seguridad Perimetral:* Isolation boundaries, Public Internet vs Virtual Network (VNet).
   - *Canal Cifrado:* HTTPS over TLS 1.3 for tarball upload and OCI layer transit.
   - *Aislamiento de Cómputo:* Managed build agents running in dedicated, ephemeral sandboxes.
   - *Plano de Control vs Plano de Datos:* Private Link / Private Endpoints for control commands, and dedicated Regional Data Endpoints for heavy layer pull/push.
   - *Autenticación y Criptografía:* Entra ID Managed Identities, RBAC tokens, AES-256 Microsoft-Managed Keys (MMK) or Customer-Managed Keys (CMK/BYOK).

### 3.4. Code & Asset Dissection Page
- **Exhaustive Script & File Analysis:**
  - Automation scripts (`azdeploy.py`, deploy scripts): Cryptographic hashing for unique DNS naming, platform resolution across OSs, idempotency, environment file generation (`.env`).
  - Containerization files (`Dockerfile`): Base image selection (`python:3.11-slim`), layer caching hygiene (`--no-cache-dir`), decoupled configuration via `ENV`, exposed ports.
  - Microservices & APIs (`app.py`): Endpoint purposes (`/health` probes for orchestrator liveness, `/predict` simulated inference, `/` service discovery), host binding (`0.0.0.0`).

### 3.5. Certification Exam Q&A Bank Page
- **Official AI-200 Exam Skills Matrix (Study Guide Weighting):**
  - Sleek 4-column or 2x2 grid displaying the official exam domain distribution from Microsoft Learn:
    1. *Dominio 1: Desarrollo de soluciones en contenedores en Azure (20% – 25%)* [Highlight if covered in the lab].
    2. *Dominio 2: Desarrollo de soluciones de IA mediante servicios de administración de datos (25% – 30%)*.
    3. *Dominio 3: Conexión y consumo de servicios de Azure (20% – 25%)*.
    4. *Dominio 4: Protección, supervisión y solución de problemas (20% – 25%)*.
- **High-Yield Scenario Questions (AI-200 / AI-102 / AZ-204):**
  - Minimum 5 scenario-based questions matching official Microsoft Learn / PPT knowledge checks.
  - Structure: Scenario -> Options (A, B, C) -> Correct Answer Indicator -> **Justificación Oficial Exhaustiva** explaining why the correct option is architecturally valid and why each distractor is technically incorrect.

### 3.6. Final Page: Glosario Normativo, Diccionario de Siglas y Mapa Curricular
The concluding page of every lab guide MUST contain:
1. **Conceptos Arquitectónicos Centrales:** Grid of cards defining core architectural pillars (e.g., ACR, ACR Tasks & Tarball Context, Digest SHA-256 vs Tag, Replicación Geográfica, Private Link & Data Endpoint, DNS Scope & acr purge).
2. **Diccionario Exhaustivo de Siglas y Acrónimos Técnicos:** Comprehensive 2-column alphabetical reference table explaining all technical acronyms used in the module (e.g., ACA, AKS, ACI, ARM, FQDN, VNet, CI/CD, RBAC, TAR/TGZ, ABAC, CMK/BYOK, MMK, SKU, OCI, CVE, JMESPath, TSV, TLS).
3. **Mapa Curricular y Rutas de Aprendizaje Oficiales (Curso AI-200T00-A):**
  - Complete 9-module learning path roadmap structured into 3 enterprise phases:
    - *Fase 1: Cómputo & Contenedores (Dom. 1):* Módulos 1, 2, 3 (highlight current module with `[★ Este Lab]`).
    - *Fase 2: Datos & Embeddings (Dom. 2):* Módulos 4, 5, 6 (Cosmos DB, PostgreSQL pgvector, Managed Redis).
    - *Fase 3: Integración & DevOps (Dom. 3 y 4):* Módulos 7, 8, 9 (Service Bus, Key Vault, OpenTelemetry/KQL).
  - Footer banner with direct URL to the Microsoft Learn Study Guide.

---

## 4. Strict Physical Page Budgeting & CSS Design System

### A4 Page Constraints
All HTML templates must strictly enforce the following CSS rules:
```css
@page {
  size: A4 portrait;
  margin: 0;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
  color: #1e293b;
  background: #ffffff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.page {
  width: 210mm;
  height: 297mm;
  max-height: 297mm;
  overflow: hidden;
  margin: 0 auto;
  background: #ffffff;
  padding: 7mm 12mm 5mm 12mm;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  page-break-after: always;
  break-after: page;
  position: relative;
}

.page-content {
  display: flex;
  flex-direction: column;
  gap: 4.5px;
}

.page-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #e2e8f0;
  padding-top: 3px;
  font-size: 7.2px;
  color: #94a3b8;
  font-weight: 600;
  letter-spacing: 0.3px;
}
```

### Color Palette & Token System:
- **Primary Azure Blue:** `#0078d4` (headers, title dividers, key highlights).
- **Secondary Slate:** `#1e293b` (headings, body titles).
- **Muted Text:** `#64748b` (subtitles, secondary notes).
- **Paper Background:** `#ffffff`.
- **Card Background:** `#f8fafc` with border `#e2e8f0` and border-radius `4px` or `5px`.
- **Terminal Box:** `#0f172a` background, `#f8fafc` text, `#38bdf8` commands, `#94a3b8` comments, `#fbbf24` flags, `#a5b4fc` values.
- **Accents:**
  - Green / Verified: `#16a34a` (borders `#86efac`, backgrounds `#f0fdf4`).
  - Warning / Caveats: `#d97706` (borders `#fde68a`, backgrounds `#fffbeb`).
  - Purple / Governance / OCI: `#7c3aed` (borders `#ddd6fe`, backgrounds `#f5f3ff`).
  - Cyan / Info: `#0284c7` (borders `#bfdbfe`, backgrounds `#eff6ff`).

### Layout Hygiene Checklist:
1. **Exact Page Budget:** Determine total pages $N$ before authoring. Every page must display `PÁGINA X DE N`.
2. **Zero Overflow / Zero Clipping:** Elements must never cross the 297mm vertical threshold. Adjust typography size (`7.5px` to `8.5px` for cards) and padding (`3px` to `5px`) to fit cleanly.
3. **No Phantom Pages:** Never let trailing empty elements or large margins create an extra blank page.

---

## 5. Compilation, Verification & Quality Assurance Pipeline

### 5.1. Compilation Tool
Use the standardized compilation harness script:
```bash
./.agents/skills/azure-pdf-publisher/scripts/compile-pdf.sh "PDFs/<N>/<N>. <Topic Name>.html"
```

The script:
1. Calls Google Chrome Headless with `--print-to-pdf`.
2. Validates the generated PDF page count against the budget.
3. Generates high-fidelity `.verify_page_*.png` thumbnails via native Swift/PDFKit.

### 5.2. Mandatory Inspection Gate
Before completing any task:
1. Inspect the generated thumbnail images (`.verify_page_1.png`, `.verify_page_*.png`) using `view_file`.
2. Verify:
   - Zero vertical clipping on all cards and tables.
   - Header badges and titles properly aligned.
   - Clean footer formatting (`PÁGINA X DE N`).
   - SVG vector diagrams render sharply with official icons.
3. Once verified, clean up temporary thumbnails:
   ```bash
   rm -f "PDFs/<N>/.verify_page_*.png"
   ```
