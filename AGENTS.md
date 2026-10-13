# Azure AI-200 Workspace Guidelines & PDF Harness

This repository hosts official course materials, labs, source code, and technical documentation for the Azure AI-200 curriculum.

## Mandatory PDF & Lab Guide Architecture Rules
When generating, updating, or formatting HTML and PDF guides in this workspace:
1. **Curriculum Enumeration & Directory Structure:** All guides MUST be organized inside `PDFs/<N>/<N>. <Topic Name>.html` and `PDFs/<N>/<N>. <Topic Name>.pdf`, where `<N>` matches the curriculum lesson index (`OBSIDIAN/LESSON <N>/`, `videos/<N>. <Topic>.mp4`, `CODE/<N>. <Project>/`, PPTs). Never save documents directly into root `PDFs/`.
2. **Universal Execution Context:** Never include ephemeral lab VM credentials (`Admin`, `Pa55w.rd`) or VM UI navigation. Use general prerequisites (Azure CLI, Python, RBAC) and emphasize cloud-native workflows (e.g. serverless builds with zero local Docker daemon).
3. **Command Anatomy & Explanations:** Provide detailed breakdowns of all Azure CLI commands (`az <service> <subgroup> <action>`), explaining flags (`--resource-group`, `--name`, `--registry`, `--image`, `--output`, `--query`), and noting PowerShell (`` ` ``) vs Bash (`\`) syntax.
4. **Exhaustive Code Dissection:** Analyze all project scripts (`azdeploy.py`, `Dockerfile`, `app.py`) line by line, explaining architectural decisions (SHA-1 hashing for global DNS uniqueness, slim base images, `--no-cache-dir`, `/health` probes).
5. **Certification Exam Q&A Bank:** Include official exam-style questions (AI-200 / AI-102 / AZ-204) with detailed rationales for correct answers and distractors.
6. **Physical Page Budgeting:** Adhere strictly to A4 layout constraints (`.page { width: 210mm; height: 297mm; max-height: 297mm; overflow: hidden; }`) with `PÁGINA X DE N` footers and zero clipping.
7. **Verification Gate:** Compile with Google Chrome headless and verify page count and layout using the harness script:
   `./.agents/skills/azure-pdf-publisher/scripts/compile-pdf.sh "PDFs/<N>/<N>. <Topic Name>.html"`

