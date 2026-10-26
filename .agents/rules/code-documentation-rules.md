# Mandatory Code Documentation & Bilingual Commenting Standard

This document establishes the official engineering protocol and stylistic guidelines for documenting, commenting, and structuring source code in the Azure AI-200 curriculum workspace.

Every script (`azdeploy.py`), application microservice (`main.py`, `app.py`), container specification (`Dockerfile`), and configuration file (`requirements.txt`, `.env`) MUST strictly adhere to this standard, matching the reference implementations in `CODE/1. acr-tasks-python` and `CODE/2. app-svc-container-python`.

---

## 1. Core Principles & Architectural Rationale

Code in this repository is designed for production clarity, architectural education, and certification mastery. It must never appear as bare, uncommented code. Every code file must fulfill three objectives:
1. **Dual Language Accessibility (`[EN]` / `[ES]`):** Every comment, docstring, and explanatory section must provide an English line immediately followed by its Spanish translation/equivalent.
2. **Architectural Didacticism ("Why", not just "What"):** Comments must not merely narrate language syntax (`x = x + 1`); they must explain the cloud, operating system, security, or container design rationale behind the code (e.g. Twelve-Factor methodology, layer caching, signal handling, zero-trust secrets).
3. **Clean Visual Hierarchy:** Consistent divider bars and section tags ensure code is rapidly scannable in IDEs, terminal viewers, and documentation previews.

---

## 2. Visual Delimiter Standards

Code files must use standard 80-character boundary banners:

### A. Major Section Delimiter (`80` characters width)
Used to separate conceptual domains (e.g. Module Header, Imports, Twelve-Factor Config, Route Handlers, Automation Engine, Main Execution Entrypoint):
```python
# =============================================================================
# [EN] Twelve-Factor Configuration - Decouple configuration from source code
#      Settings are ingested from OS environment variables (Container Apps / App Service).
# [ES] Configuración Twelve-Factor - Desacopla la configuración del código fuente
#      Los parámetros se ingieren desde variables de entorno del sistema operativo.
# =============================================================================
```

### B. Subsection / Function Delimiter (`80` characters width)
Used directly above route handlers, utility functions, or logical sub-blocks:
```python
# -----------------------------------------------------------------------------
# [EN] Health Check Endpoint (Liveness / Readiness Probes)
#      Used by orchestrators (Azure Container Apps, Kubernetes, Envoy)
#      to monitor container liveness and route traffic only to healthy replicas.
# [ES] Endpoint de Comprobación de Salud (Health Probe)
#      Utilizado por orquestadores (Azure Container Apps, Kubernetes, Envoy)
#      para verificar disponibilidad y dirigir tráfico únicamente a instancias sanas.
# -----------------------------------------------------------------------------
```

---

## 3. Bilingual Tagging Rules (`[EN]` and `[ES]`)

1. **Tag Format:** The tags `[EN]` and `[ES]` must always be enclosed in square brackets in capital letters, followed by a single space.
2. **Order of Languages:** The English block `[EN]` ALWAYS precedes the Spanish block `[ES]`.
3. **Indentation Parity:** When inside a function, class, or conditional block, the indentation of `[EN]` and `[ES]` must match the current scope level.
4. **Multi-line Explanations:** For multi-line comments, align subsequent lines with a 5-space indentation under the tag text:
```python
# [EN] Persistent storage directory path.
#      In Azure Container Apps, the default filesystem is ephemeral (/tmp).
# [ES] Ruta del directorio de almacenamiento persistente.
#      En Azure Container Apps, el sistema de archivos es efímero por defecto (/tmp).
```

---

## 4. Python Function & Route Docstring Format

Every Python function and endpoint handler MUST contain a bilingual triple-quoted docstring:

```python
def ensure_storage_directory() -> bool:
    """
    [EN] Ensure the persistent storage path exists on the mounted filesystem.
    [ES] Asegura que la ruta de almacenamiento persistente exista en el sistema de archivos montado.
    """
```

For endpoints that accept payloads or return structured data:
```python
@app.route("/process", methods=["POST"])
def process_document():
    """
    [EN] Ingest and analyze a document, returning AI extraction results.
         Accepts JSON or multipart/form-data payloads; enforces size limits.
    [ES] Ingiere y analiza un documento, retornando resultados de extracción de IA.
         Acepta cargas útiles JSON o multipart/form-data; valida límites de tamaño.
    """
```

---

## 5. Step-by-Step Numbered Inline Comments

Complex internal algorithms, CLI automation pipelines, or request processing pipelines must use numbered step markers:

```python
# [EN] 1. Generate unique document identifier and UTC timestamp
# [ES] 1. Genera identificador único para el documento y marca de tiempo UTC
doc_id = str(uuid.uuid4())
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# [EN] 2. Extract document content based on incoming Content-Type
# [ES] 2. Extrae el contenido del documento según el encabezado Content-Type recibido
if request.is_json:
    ...
```

---

## 6. Dockerfile Commenting Standard

Every container instruction (`FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `CMD`) MUST be preceded by a Major Section Delimiter explaining the container engineering step and architectural rationale:

```dockerfile
# =============================================================================
# [EN] Step 1: Base image - Lightweight Debian-based Python runtime
#      Optimized for production: reduces image footprint and attack surface.
# [ES] Paso 1: Imagen base - Entorno Python ligero basado en Debian
#      Optimizado para producción: reduce huella de disco y superficie de ataque.
# =============================================================================
FROM python:3.12-slim

# =============================================================================
# [EN] Step 2: Working directory - Isolates application files inside container
# [ES] Paso 2: Directorio de trabajo - Aísla los archivos de la app dentro del contenedor
# =============================================================================
WORKDIR /app
```

Key Dockerfile explanations that must always be present:
- **`--no-cache-dir`:** Explain why pip download cache is suppressed (minimizes layer size).
- **Split `COPY requirements.txt .` vs `COPY . .`:** Explain Docker build layer caching and cache invalidation.
- **`EXPOSE <port>`:** Clarify that this is documentation metadata for orchestrator routing.
- **`CMD` in exec form / shell wrapper:** Explain why Gunicorn or Python is executed and how `SIGTERM` signals are handled.

---

## 7. Dependencies & Config Files (`requirements.txt`)

Even configuration and dependency manifests must include bilingual headers explaining the role of each library:

```text
# =============================================================================
# [EN] Production Dependencies for Azure Container Apps API
# [ES] Dependencias de Producción para la API en Azure Container Apps
# =============================================================================

# [EN] Lightweight WSGI web framework for REST API routing
# [ES] Framework web WSGI ligero para enrutamiento de APIs REST
flask==3.0.0

# [EN] Production WSGI HTTP server with multi-worker concurrency
# [ES] Servidor HTTP WSGI para producción con concurrencia multi-worker
gunicorn==22.0.0
```

---

## 8. Azure CLI Deployment Scripts (`azdeploy.py`)

Deployment orchestrators must strictly separate:
1. **User Configuration Block:** Top of file with clear editable variable markers (`rg`, `location`, `sku`, etc.).
2. **Immutable Automation Engine Boundary:** Explicit `# DON'T CHANGE ANYTHING BELOW THIS LINE.` barrier.
3. **Utility Logic:** Explaining why `_resolve_exe` caches binary paths (`az` vs `az.cmd` in Windows).
4. **Cryptographic Uniqueness:** Explaining why `hashlib.sha1` is used to generate globally unique DNS prefixes for Azure Container Registry and Container Apps environments.
5. **Idempotent Resource Management:** Explaining `az_query` checks before creation (`az group exists`, `az acr show`, `az containerapp env show`) to prevent race conditions or destructive overwrites.
