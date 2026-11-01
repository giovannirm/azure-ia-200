# =============================================================================
# [EN] AI Document Processing Mock API - Microservice for Azure Container Apps
#      Demonstrates containerized serverless workloads, Twelve-Factor configuration,
#      health probes, runtime secret ingestion, and Log Analytics streaming.
# [ES] API Simulada de Procesamiento de Documentos - Microservicio para Azure Container Apps
#      Demuestra cargas serverless en contenedores, configuración Twelve-Factor,
#      sondeos de salud, inyección de secretos en runtime y streaming a Log Analytics.
# =============================================================================

# [EN] Standard library imports for JSON serialization, logging, OS access, UUIDs, and UTC time
# [ES] Importaciones de biblioteca estándar para serialización JSON, logging, SO, UUIDs y tiempo UTC
import json
import logging
import os
import uuid
from datetime import datetime, timezone

# [EN] Web framework imports for REST routing, HTTP request handling, and JSON responses
# [ES] Importaciones del framework web para enrutamiento REST, peticiones HTTP y respuestas JSON
from flask import Flask, jsonify, request

# =============================================================================
# [EN] Flask Application Initialization
# [ES] Inicialización de la Aplicación Flask
# =============================================================================
app = Flask(__name__)

# =============================================================================
# [EN] Twelve-Factor Configuration - Decouple configuration from source code
#      Settings are ingested from OS environment variables (Container Apps Configuration).
# [ES] Configuración Twelve-Factor - Desacopla la configuración del código fuente
#      Los parámetros se ingieren desde variables de entorno (Configuración de Container Apps).
# =============================================================================

# [EN] Deployment environment identifier (development, staging, production)
# [ES] Identificador del entorno de despliegue (development, staging, production)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# [EN] Minimum logging threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# [ES] Umbral mínimo de severidad para logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# [EN] Configured AI model identifier (e.g., gpt-5.1) passed via Container Apps environment variable
# [ES] Identificador del modelo de IA configurado (ej. gpt-5.1) inyectado vía variable de entorno en ACA
MODEL_NAME = os.getenv("MODEL_NAME", "not-configured")

# [EN] Secret API key reference. Injected securely in Container Apps via secretref:
#      Eliminates plain-text secret exposure in deployment scripts and ARM templates.
# [ES] Referencia a la clave secreta de API. Inyectada de forma segura en ACA mediante secretref:
#      Elimina la exposición de contraseñas o claves en texto plano en scripts y plantillas ARM.
EMBEDDINGS_API_KEY = os.getenv("EMBEDDINGS_API_KEY")

# [EN] Maximum allowed document payload size in megabytes (enforces payload boundary and DoS protection)
# [ES] Tamaño máximo permitido para el documento en megabytes (protección de perímetro y contra DoS)
MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "10"))

# [EN] Maximum simulated processing execution window in seconds
# [ES] Ventana máxima de ejecución simulada para procesamiento en segundos
PROCESSING_TIMEOUT_SECONDS = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "15"))

# [EN] Ephemeral storage directory path.
#      Azure Container Apps replicas use ephemeral container storage by default (/tmp/processed).
# [ES] Ruta del directorio de almacenamiento efímero.
#      Las réplicas de Azure Container Apps usan almacenamiento efímero por defecto (/tmp/processed).
STORAGE_PATH = os.getenv("STORAGE_PATH", "/tmp/processed")

# =============================================================================
# [EN] Logging Configuration
#      Streams structured logs to stdout/stderr for automated Log Analytics ingestion.
# [ES] Configuración de Logging
#      Envía logs estructurados a stdout/stderr para ingesta automática en Log Analytics.
# =============================================================================
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# [EN] Storage Preflight Helper
#      Verifies that the target storage directory exists; attempts creation if missing.
# [ES] Función Auxiliar de Almacenamiento
#      Verifica la existencia del directorio de almacenamiento; lo crea si no existe.
# -----------------------------------------------------------------------------
def _ensure_storage_directory() -> bool:
    """
    [EN] Ensure the local processing storage directory exists on the ephemeral filesystem.
    [ES] Asegura que el directorio de almacenamiento exista en el sistema de archivos efímero.
    """
    try:
        # [EN] Create directory recursively (exist_ok=True avoids raising error if directory already exists)
        # [ES] Crea el directorio de forma recursiva (exist_ok=True evita error si la carpeta ya existe)
        os.makedirs(STORAGE_PATH, exist_ok=True)
        return True
    except Exception as exc:
        # [EN] Log warning if storage path is inaccessible
        # [ES] Registra advertencia si la ruta es inaccesible
        logger.warning("Could not create storage directory: %s", exc)
        return False


# -----------------------------------------------------------------------------
# [EN] Secret Configuration Verifier
#      Checks whether EMBEDDINGS_API_KEY was successfully populated via secretref:
# [ES] Verificador de Configuración de Secretos
#      Comprueba si EMBEDDINGS_API_KEY fue inyectada exitosamente mediante secretref:
# -----------------------------------------------------------------------------
def _embeddings_key_configured() -> bool:
    """
    [EN] Check if the embeddings API key secret is configured in the environment.
    [ES] Comprueba si el secreto de la clave de embeddings está configurado en el entorno.
    """
    return bool(EMBEDDINGS_API_KEY and EMBEDDINGS_API_KEY.strip())


# =============================================================================
# [EN] API Endpoints & Route Handlers
# [ES] Endpoints de la API y Manejadores de Rutas
# =============================================================================

# -----------------------------------------------------------------------------
# [EN] Root Endpoint - Service Information and Discovery
#      Provides catalog of running version, environment, model, and active configuration.
# [ES] Endpoint Raíz - Información del Servicio y Descubrimiento
#      Proporciona el catálogo de versión activa, entorno, modelo y configuración cargada.
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    """
    [EN] Returns service status, model information, secret presence, and configuration.
    [ES] Retorna estado del servicio, modelo de IA, presencia de secretos y configuración.
    """
    # [EN] Log incoming request for service catalog discovery
    # [ES] Registra la solicitud entrante para descubrimiento del catálogo del servicio
    logger.info("Service info requested")

    # [EN] Return JSON payload with service metadata, model name, and configuration values
    # [ES] Retorna payload JSON con metadatos del servicio, modelo y valores de configuración
    return jsonify(
        {
            "service": "AI Document Processing API",
            "status": "running",
            "version": "1.0.0",
            "environment": ENVIRONMENT,
            "model": {"name": MODEL_NAME},
            "secrets": {"embeddings_api_key_configured": _embeddings_key_configured()},
            "config": {
                "max_document_size_mb": MAX_DOCUMENT_SIZE_MB,
                "processing_timeout_seconds": PROCESSING_TIMEOUT_SECONDS,
                "log_level": LOG_LEVEL,
                "storage_path": STORAGE_PATH,
            },
        }
    )


# -----------------------------------------------------------------------------
# [EN] Health Check Endpoint (Liveness / Readiness Probes)
#      Used by Azure Container Apps Envoy Ingress and container orchestrator
#      to monitor replica health and route traffic only to responsive instances.
# [ES] Endpoint de Comprobación de Salud (Health Probe)
#      Utilizado por el Envoy Ingress de Azure Container Apps y el orquestador
#      para verificar disponibilidad y dirigir tráfico únicamente a instancias sanas.
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """
    [EN] Fast, lightweight liveness probe returning HTTP 200 with healthy status.
    [ES] Sondeo de disponibilidad rápido y ligero que retorna HTTP 200 con estado healthy.
    """
    # [EN] Fast response: return HTTP 200 with healthy status for orchestrator probes
    # [ES] Respuesta rápida: retorna HTTP 200 con estado healthy para sondeos del orquestador
    return jsonify({"status": "healthy"})


# -----------------------------------------------------------------------------
# [EN] Document Processing Endpoint (Core Business Logic)
#      Accepts JSON payloads, multipart file uploads, or raw text streams.
#      Simulates cognitive AI extraction: named entities, key phrases, and sentiment.
#      Saves processed document telemetry to the local ephemeral storage path.
# [ES] Endpoint de Procesamiento de Documentos (Lógica de Negocio Principal)
#      Acepta cargas JSON, subida de archivos multipart o flujos de texto plano.
#      Simula extracción cognitiva con IA: entidades nombradas, frases clave y sentimiento.
#      Guarda la telemetría del documento procesado en el almacenamiento efímero local.
# -----------------------------------------------------------------------------
@app.route("/process", methods=["POST"])
def process_document():
    """
    [EN] Ingest and analyze a document, returning AI extraction results.
         Supports JSON (content, filename) or multipart file uploads.
    [ES] Ingiere y analiza un documento, retornando resultados de extracción mediante IA.
         Soporta JSON (content, filename) o subida de archivos multipart.
    """
    logger.info("Document processing request received")

    # [EN] 1. Generate unique document identifier and UTC ISO timestamp
    # [ES] 1. Genera identificador único para el documento y marca de tiempo ISO en UTC
    doc_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # [EN] 2. Extract document content based on incoming payload format
    # [ES] 2. Extrae el contenido del documento según el formato del payload recibido
    if request.is_json:
        # [EN] Handle application/json payload with JSON body parameters
        # [ES] Procesa payload application/json con parámetros en el cuerpo JSON
        data = request.get_json(silent=True) or {}
        content = data.get("content", "")
        filename = data.get("filename", "document.txt")
    elif request.files:
        # [EN] Handle multipart/form-data payload with uploaded binary/text file
        # [ES] Procesa payload multipart/form-data con archivo binario/texto subido
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file provided"}), 400
        content = file.read().decode("utf-8", errors="ignore")
        filename = file.filename or "document.txt"
    else:
        # [EN] Handle raw text/plain or fallback raw stream payload
        # [ES] Procesa texto plano raw text/plain o flujo de datos sin formato
        content = request.data.decode("utf-8", errors="ignore") or "Sample document"
        filename = "document.txt"

    # [EN] 3. Payload size enforcement: reject payloads exceeding MAX_DOCUMENT_SIZE_MB
    # [ES] 3. Control de tamaño de carga útil: rechaza documentos que superen MAX_DOCUMENT_SIZE_MB
    content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
    if content_size_mb > MAX_DOCUMENT_SIZE_MB:
        logger.warning("Document too large: %.2f MB", content_size_mb)
        return (
            jsonify({"error": f"Document exceeds maximum size of {MAX_DOCUMENT_SIZE_MB} MB"}),
            413,
        )

    logger.info("Processing document: %s (%s chars)", filename, len(content))

    # [EN] 4. Compute metrics and simulate AI cognitive model extraction
    # [ES] 4. Calcula métricas y simula extracción cognitiva mediante modelos de IA
    word_count = len(content.split())
    char_count = len(content)

    # [EN] Simulated named entity recognition (NER)
    # [ES] Simulación de reconocimiento de entidades nombradas (NER)
    mock_entities = [
        {"text": "Azure", "type": "Technology", "confidence": 0.95},
        {"text": "Container Apps", "type": "Service", "confidence": 0.93},
        {"text": "document", "type": "Concept", "confidence": 0.87},
    ]

    # [EN] Simulated key phrase extraction
    # [ES] Simulación de extracción de frases clave
    mock_key_phrases = [
        "document processing",
        "container deployment",
        "secrets and configuration",
        "revision management",
    ]

    # [EN] Simulated sentiment analysis scores
    # [ES] Simulación de puntuaciones de análisis de sentimiento
    mock_sentiment = {
        "overall": "neutral",
        "confidence": 0.78,
        "scores": {"positive": 0.22, "neutral": 0.68, "negative": 0.10},
    }

    # [EN] 5. Build structured analytical response document
    # [ES] 5. Construye el documento de respuesta analítica estructurada
    result = {
        "document_id": doc_id,
        "filename": filename,
        "processed_at": timestamp,
        "environment": ENVIRONMENT,
        "model": {"name": MODEL_NAME},
        "secrets": {"embeddings_api_key_configured": _embeddings_key_configured()},
        "statistics": {
            "character_count": char_count,
            "word_count": word_count,
            "size_bytes": len(content.encode("utf-8")),
        },
        "analysis": {
            "entities": mock_entities,
            "key_phrases": mock_key_phrases,
            "sentiment": mock_sentiment,
        },
        "processing_config": {
            "timeout_seconds": PROCESSING_TIMEOUT_SECONDS,
            "max_size_mb": MAX_DOCUMENT_SIZE_MB,
        },
    }

    # [EN] 6. Persist analytical results to local storage path
    # [ES] 6. Persiste los resultados analíticos en la ruta de almacenamiento local
    storage_available = _ensure_storage_directory()
    if storage_available:
        try:
            result_path = os.path.join(STORAGE_PATH, f"{doc_id}.json")
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            result["storage"] = {"saved": True, "path": result_path}
            logger.info("Result saved to %s", result_path)
        except Exception as exc:
            logger.error("Failed to save result: %s", exc)
            result["storage"] = {"saved": False, "error": str(exc)}
    else:
        result["storage"] = {"saved": False, "reason": "Storage not available"}

    return jsonify(result)


# -----------------------------------------------------------------------------
# [EN] Processed Documents Listing Endpoint
#      Catalogs all JSON documents currently stored in the local container storage.
# [ES] Endpoint de Listado de Documentos Procesados
#      Cataloga todos los documentos JSON almacenados actualmente en el contenedor local.
# -----------------------------------------------------------------------------
@app.route("/documents", methods=["GET"])
def list_documents():
    """
    [EN] List processed documents stored in the container's local filesystem.
    [ES] Lista los documentos procesados almacenados en el sistema de archivos local.
    """
    logger.info("Listing processed documents")

    # [EN] Check storage directory accessibility
    # [ES] Verifica la accesibilidad del directorio de almacenamiento
    if not _ensure_storage_directory():
        return jsonify({"documents": [], "error": "Storage not available"})

    try:
        files = []
        # [EN] Iterate files in storage path and extract metadata
        # [ES] Itera los archivos en la ruta de almacenamiento y extrae metadatos
        for filename in os.listdir(STORAGE_PATH):
            if filename.endswith(".json"):
                filepath = os.path.join(STORAGE_PATH, filename)
                stat = os.stat(filepath)
                files.append(
                    {
                        "document_id": filename.replace(".json", ""),
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                    }
                )
        return jsonify({"documents": files, "count": len(files)})
    except Exception as exc:
        logger.error("Failed to list documents: %s", exc)
        return jsonify({"documents": [], "error": str(exc)})


# -----------------------------------------------------------------------------
# [EN] Document Retrieval by ID Endpoint
#      Fetches and returns a single processed document JSON by its document_id.
# [ES] Endpoint de Recuperación de Documento por ID
#      Obtiene y retorna el JSON de un documento procesado según su document_id.
# -----------------------------------------------------------------------------
@app.route("/documents/<doc_id>", methods=["GET"])
def get_document(doc_id: str):
    """
    [EN] Retrieve a single processed document by its unique identifier.
    [ES] Recupera un documento procesado individual según su identificador único.
    """
    logger.info("Retrieving document: %s", doc_id)

    filepath = os.path.join(STORAGE_PATH, f"{doc_id}.json")
    # [EN] Return HTTP 404 if document file does not exist
    # [ES] Retorna HTTP 404 si el archivo del documento no existe
    if not os.path.exists(filepath):
        return jsonify({"error": "Document not found"}), 404

    try:
        # [EN] Read and return JSON file content
        # [ES] Lee y retorna el contenido del archivo JSON
        with open(filepath, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as exc:
        logger.error("Failed to read document: %s", exc)
        return jsonify({"error": str(exc)}), 500


# -----------------------------------------------------------------------------
# [EN] Application Startup Telemetry
#      Outputs environment variables, model configuration, and secret status to stdout.
# [ES] Telemetría de Inicio de la Aplicación
#      Emite variables de entorno, configuración del modelo y estado de secretos a stdout.
# -----------------------------------------------------------------------------
def _log_startup_summary() -> None:
    """
    [EN] Log active configuration settings and secret status on application boot.
    [ES] Registra en el log los ajustes activos y el estado de secretos al iniciar la app.
    """
    logger.info("Starting AI Document Processing API")
    logger.info("ENVIRONMENT=%s LOG_LEVEL=%s", ENVIRONMENT, LOG_LEVEL)
    logger.info("MODEL_NAME=%s", MODEL_NAME)
    logger.info("EMBEDDINGS_API_KEY configured: %s", _embeddings_key_configured())


# =============================================================================
# [EN] Direct Execution Entrypoint (Development & Local Testing)
#      In production containers, Gunicorn launches main:app directly.
# [ES] Punto de Entrada para Ejecución Directa (Desarrollo y Pruebas Locales)
#      En contenedores de producción, Gunicorn invoca directamente main:app.
# =============================================================================
if __name__ == "__main__":
    _log_startup_summary()
    _ensure_storage_directory()

    # [EN] Read port from environment (defaults to 8000 for Azure Container Apps)
    # [ES] Lee el puerto desde el entorno (por defecto 8000 para Azure Container Apps)
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
