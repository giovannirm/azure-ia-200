---
name: azure-pdf-publisher
description: >-
  Standardized protocol to author, format, compile, and visually verify enterprise A4 lab guides and technical documentation PDFs in Azure AI-200.
---

# Azure PDF Publisher & Lab Documentation Protocol

Use this skill whenever authoring, updating, or compiling technical PDFs or lab guides for Azure AI-200 (**Microsoft Certified: Azure AI Cloud Developer Associate**). Every guide must follow the gold standard established in `PDFs/1/1. Azure CLI y ACR Tasks.html`.

---

## 1. Curriculum Enumeration & Directory Structure

All documents MUST be organized according to the course lesson enumeration:
- **Target Folder:** `PDFs/<N>/` where `<N>` is the lesson number (e.g., `1`, `2`, `3`).
- **File Names:** `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`.
- **Cross-Workspace Alignment:**
  - `PDFs/<N>/<N>. <Topic Name>.html`
  - `OBSIDIAN/LESSON <N>/`
  - `videos/<N>. <Topic>.webloc` / `videos/<N>. <Topic>.url`
  - `CODE/<N>. <Project-Name>/`
  - `PPTs/AI-200 PARTE <X>.pptx` (Module `<N>`)

### Authoring Step 0 (Pre-flight):
1. Identify the module index `<N>` from the user request or the curriculum structure (`PDFs/`, `OBSIDIAN/`, `videos/`).
2. Verify that directory `PDFs/<N>/` exists. If not, create it: `mkdir -p "PDFs/<N>"`.
3. Never write HTML or PDF files directly to the root of `PDFs/`.

---

## 2. Mandatory Structural Components of Every Lab Guide

Every technical PDF guide MUST include the following 8 structural pillars:

### Pillar 1: Official Microsoft Learn Alignment (Page 1)
- Include the official **Alineación Curricular Oficial Microsoft Learn** banner:
  - Official Course: `Curso AI-200T00-A: Desarrollo de soluciones en la nube de IA en Azure` (5 días / 120 hrs).
  - Certification: `Microsoft Certified: Azure AI Cloud Developer Associate (Examen AI-200)`.
  - Specific Exam Domain & Weight (e.g., `Dominio 1: Desarrollo de soluciones en contenedores en Azure (20% – 25%)`).
  - Clickable link to official [Guía de Estudio Oficial AI-200 (Study Guide)](https://learn.microsoft.com/es-es/credentials/certifications/resources/study-guides/ai-200).

### Pillar 2: Universal Prerequisites & Critical Notices (Page 1)
- Decouple from ephemeral lab virtual machines (`Admin` / `Pa55w.rd`).
- Specify universal prerequisites: Azure CLI 2.50+, Python 3.10+, RBAC permissions (`Contributor`, `AcrPush`), active subscription (Pay-As-You-Go), zero local Docker daemon.
- Highlight operational caveats: DNS global uniqueness, subscription tier limits, CLI latency, PowerShell (`` ` ``) vs Bash (`\`) line continuation.

### Pillar 3: Didactic CLI Command Anatomy & Parameter Table (Page 1)
- Explain the hierarchy pattern: `az <service> <subgroup> <action> [--parameters]`.
- Provide an exhaustive reference table explaining all flags used (`--resource-group`, `--name`, `--registry`, `--image`, `--output`, `--query`, `--no-wait`, etc.) with technical purposes and practical examples.

### Pillar 4: Dual Verification Flow (CLI + Azure Portal GUI Walkthrough)
- For every practical phase, provide:
  1. Automated Azure CLI commands with output formats (`table`, `json`, `tsv`).
  2. Step-by-step Azure Portal GUI walkthrough (Navigation bar -> Resource blade -> Menu settings -> Verification tabs).

### Pillar 5: Dual Architecture Blueprints with Official Azure Icons
Every guide must contain two dedicated architecture pages:
1. **Diagrama de Arquitectura Lógica (Página dedicada):**
   - Real-world business problem statement and workflow description.
   - Draw.io style canvas layout with logical tiers (Estación de Desarrollo, Cómputo Serverless, Registro OCI, Consumidores Downstream, Gobernanza & Seguridad).
   - **MANDATORY:** Use official Azure vector SVG icons (downloaded or embedded via base64/inline SVG). **Never invent or draw fake icons.**
2. **Diagrama de Arquitectura Física y Topología de Red (Página dedicada):**
   - Network boundaries (Public Internet vs Virtual Network VNet).
   - Encryption in transit (HTTPS / TLS 1.3) and at rest (AES-256 MMK or CMK/BYOK).
   - Private Link, Private Endpoints, and Regional Data Endpoints.
   - Microsoft Entra ID Managed Identities and RBAC authorization tokens.

### Pillar 6: Exhaustive Source Code & Infrastructure Dissection
- Line-by-line breakdown of all lab files (`azdeploy.py`, `Dockerfile`, `app.py`).
- Detail architectural rationale: SHA-1 hashing for DNS uniqueness, slim base images, `--no-cache-dir`, `/health` probes for orchestrators, environment decoupling.

### Pillar 7: Certification Exam Q&A Bank & Skills Weighting Matrix
- **Matriz de Distribución de Habilidades Evaluadas (Study Guide Weighting):**
  - Table or 4-box card detailing the 4 official AI-200 Exam Domains (Containers 20-25%, AI Data 25-30%, Services Connection 20-25%, Security/Monitoring 20-25%), highlighting the current lab's domain.
- **Official Exam-Grade Questions (5+ scenario questions):**
  - Scenario description -> Multiple choice options (A, B, C) -> Marked correct key -> **Justificación Oficial Exhaustiva** explaining why the answer is correct and why distractors fail.

### Pillar 8: Technical Glossary, Acronym Dictionary & 9-Module Roadmap (Final Page)
The final page must strictly contain three distinct sections:
1. **1. Conceptos Arquitectónicos Centrales:** Grid of definition cards for key technical concepts (ACR, ACR Tasks, Tarball Context, Digest SHA-256 vs Tag, Replicación Geográfica, Private Link & Data Endpoint, DNS Scope, etc.).
2. **2. Diccionario de Siglas y Acrónimos Técnicos:** Comprehensive 2-column alphabetical reference table of all acronyms (ACA, AKS, ACI, ARM, FQDN, VNet, CI/CD, RBAC, TAR/TGZ, ABAC, CMK/BYOK, MMK, SKU, OCI, CVE, JMESPath, TSV, TLS).
3. **3. Mapa Curricular y Rutas de Aprendizaje Oficiales (Curso AI-200T00-A):**
   - 3-column roadmap detailing the 9 official Microsoft Learn modules across 3 phases (Cómputo & Contenedores, Datos & Embeddings, Integración & DevOps), highlighting the current module with `[★ Este Lab]`.
   - Footer banner with direct link to Microsoft Learn AI-200 Study Guide.

---

## 3. Strict Page Budgeting & CSS Rules

All HTML guides must enforce these physical A4 constraints:
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

- Every page must feature the standard footer: `PÁGINA X DE N`.
- Zero vertical overflow: Ensure all content strictly fits within 297mm without spilling over.

---

## 4. Automated Compilation & Verification Gate

Run the bundled compilation script:
```bash
./.agents/skills/azure-pdf-publisher/scripts/compile-pdf.sh "PDFs/<N>/<N>. <Topic Name>.html"
```

The script:
1. Calls headless Google Chrome with `--print-to-pdf` outputting directly into `PDFs/<N>/<N>. <Topic Name>.pdf`.
2. Validates the generated page count against the budget.
3. Uses native Swift/PDFKit to render `.verify_page_*.png` thumbnails in `PDFs/<N>/`.
4. Inspect thumbnails with `view_file` to verify text alignment, padding, and zero clipping.
5. Clean up temporary thumbnails once verified: `rm -f "PDFs/<N>/.verify_page_*.png"`.
