# =============================================================================
# [EN] Document Processing API - Microservice for Azure App Service
#      Demonstrates containerized workloads, Twelve-Factor configuration,
#      health probes, and Azure persistent storage integration.
# [ES] API de Procesamiento de Documentos - Microservicio para Azure App Service
#      Demuestra cargas de trabajo en contenedores, configuración Twelve-Factor,
#      sondeos de salud (health probes) e integración con almacenamiento persistente de Azure.
# =============================================================================

# [EN] Standard library imports for JSON serialization, logging, OS access, and UUIDs
# [ES] Importaciones de biblioteca estándar para serialización JSON, logging, SO y UUIDs
import json
import logging
import os
import uuid
from datetime import datetime

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
#      Settings are ingested from OS environment variables (App Settings in App Service).
# [ES] Configuración Twelve-Factor - Desacopla la configuración del código fuente
#      Los parámetros se ingieren desde variables de entorno (Application Settings en App Service).
# =============================================================================

# [EN] Deployment environment identifier (development, staging, production)
# [ES] Identificador del entorno de despliegue (development, staging, production)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# [EN] Minimum logging threshold (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# [ES] Umbral mínimo de severidad para logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# [EN] Maximum allowed document payload size in megabytes (enforces DoS protection)
# [ES] Tamaño máximo permitido para el documento en megabytes (protección contra DoS)
MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))

# [EN] Maximum simulated processing execution window in seconds
# [ES] Ventana máxima de ejecución simulada para procesamiento en segundos
PROCESSING_TIMEOUT_SECONDS = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "30"))

# [EN] Persistent storage directory path.
#      In Azure App Service, /home is backed by Azure Storage CIFS/SMB share
#      when WEBSITES_ENABLE_APP_SERVICE_STORAGE=true is configured.
# [ES] Ruta del directorio de almacenamiento persistente.
#      En Azure App Service, /home está respaldado por Azure Storage (CIFS/SMB)
#      cuando WEBSITES_ENABLE_APP_SERVICE_STORAGE=true está configurado.
STORAGE_PATH = os.getenv("STORAGE_PATH", "/home/processed")

# =============================================================================
# [EN] Logging Configuration
#      Streams structured logs to stdout/stderr so Azure Log Stream and Kudu capture them.
# [ES] Configuración de Logging
#      Envía logs estructurados a stdout/stderr para ser capturados por Azure Log Stream y Kudu.
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
def ensure_storage_directory() -> bool:
    """
    [EN] Ensure the persistent storage path exists on the mounted filesystem.
    [ES] Asegura que la ruta de almacenamiento persistente exista en el sistema de archivos montado.
    """
    try:
        os.makedirs(STORAGE_PATH, exist_ok=True)
        return True
    except Exception as e:
        logger.warning(f"Could not create storage directory '{STORAGE_PATH}': {e}")
        return False


# =============================================================================
# [EN] API Endpoints & Route Handlers
# [ES] Endpoints de la API y Manejadores de Rutas
# =============================================================================

# -----------------------------------------------------------------------------
# [EN] Root Endpoint - Service Information and Discovery
#      Provides catalog of running version, environment, and active configuration.
# [ES] Endpoint Raíz - Información del Servicio y Descubrimiento
#      Proporciona el catálogo de versión activa, entorno y configuración cargada.
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    """
    [EN] Returns service status, version, and active runtime configuration.
    [ES] Retorna el estado del servicio, versión y configuración activa en tiempo de ejecución.
    """
    logger.info("Service catalog requested from root endpoint")
    return jsonify(
        {
            "service": "Document Processing API",
            "status": "running",
            "environment": ENVIRONMENT,
            "version": "1.0.0",
            "config": {
                "max_document_size_mb": MAX_DOCUMENT_SIZE_MB,
                "processing_timeout_seconds": PROCESSING_TIMEOUT_SECONDS,
                "log_level": LOG_LEVEL,
                "storage_path": STORAGE_PATH,
            },
        }
    )


# -----------------------------------------------------------------------------
# [EN] Health Check Endpoint
#      Used by Azure App Service Health Check probes and front-end load balancers
#      to monitor container liveness and route traffic only to healthy instances.
# [ES] Endpoint de Comprobación de Salud (Health Probe)
#      Utilizado por los sondeos de App Service y balanceadores de carga front-end
#      para verificar la disponibilidad del contenedor y dirigir tráfico únicamente a instancias sanas.
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """
    [EN] Fast, lightweight liveness probe for Azure App Service routing.
    [ES] Sondeo de disponibilidad rápido y ligero para el enrutamiento de Azure App Service.
    """
    return jsonify({"status": "healthy"})


# -----------------------------------------------------------------------------
# [EN] Document Processing Endpoint (Core Business Logic)
#      Accepts JSON, multipart file uploads, or raw text payloads.
#      Simulates AI extraction: named entities, key phrases, and sentiment.
#      Persists analysis results to persistent /home/processed storage.
# [ES] Endpoint de Procesamiento de Documentos (Lógica de Negocio Principal)
#      Acepta cargas útiles JSON, subida de archivos multipart o texto plano.
#      Simula extracción con IA: entidades nombradas, frases clave y análisis de sentimiento.
#      Persiste los resultados analíticos en el almacenamiento persistente /home/processed.
# -----------------------------------------------------------------------------
@app.route("/process", methods=["POST"])
def process_document():
    """
    [EN] Ingest and analyze a document, returning AI extraction results.
    [ES] Ingiere y analiza un documento, retornando resultados de extracción mediante IA.
    """
    logger.info("Document processing request received")

    # [EN] 1. Generate unique document identifier and UTC timestamp
    # [ES] 1. Genera identificador único para el documento y marca de tiempo UTC
    doc_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # [EN] 2. Extract document content based on incoming Content-Type
    # [ES] 2. Extrae el contenido del documento según el encabezado Content-Type recibido
    if request.is_json:
        data = request.get_json()
        content = data.get("content", "")
        filename = data.get("filename", "document.txt")
    elif request.files:
        file = request.files.get("file")
        if file:
            content = file.read().decode("utf-8", errors="ignore")
            filename = file.filename
        else:
            return jsonify({"error": "No file provided in multipart request"}), 400
    else:
        content = request.data.decode("utf-8", errors="ignore") or "Sample document"
        filename = "document.txt"

    # [EN] 3. Payload size enforcement: reject payloads exceeding MAX_DOCUMENT_SIZE_MB
    # [ES] 3. Control de tamaño de carga útil: rechaza documentos que superen MAX_DOCUMENT_SIZE_MB
    content_size_bytes = len(content.encode("utf-8"))
    content_size_mb = content_size_bytes / (1024 * 1024)
    if content_size_mb > MAX_DOCUMENT_SIZE_MB:
        logger.warning(f"Document rejected: size {content_size_mb:.2f} MB exceeds {MAX_DOCUMENT_SIZE_MB} MB limit")
        return (
            jsonify(
                {
                    "error": f"Document exceeds maximum size of {MAX_DOCUMENT_SIZE_MB} MB"
                }
            ),
            413,
        )

    logger.info(f"Processing document: '{filename}' ({len(content)} characters, {content_size_bytes} bytes)")

    # [EN] 4. Compute metrics and simulate AI cognitive analysis
    # [ES] 4. Calcula métricas y simula análisis cognitivo mediante modelos de IA
    word_count = len(content.split())
    char_count = len(content)

    # [EN] Simulated Named Entity Recognition (NER)
    # [ES] Extracción simulada de Entidades Nombradas (NER)
    mock_entities = [
        {"text": "Azure", "type": "Technology", "confidence": 0.95},
        {"text": "App Service", "type": "Service", "confidence": 0.92},
        {"text": "container", "type": "Concept", "confidence": 0.88},
    ]

    # [EN] Simulated Key Phrase Extraction
    # [ES] Extracción simulada de Frases Clave
    mock_key_phrases = [
        "document processing",
        "cloud deployment",
        "container hosting",
        "managed service",
    ]

    # [EN] Simulated Sentiment Analysis
    # [ES] Análisis simulado de Sentimiento
    mock_sentiment = {
        "overall": "neutral",
        "confidence": 0.78,
        "scores": {"positive": 0.25, "neutral": 0.65, "negative": 0.10},
    }

    # [EN] 5. Assemble structured analytical response payload
    # [ES] 5. Ensambla el payload de respuesta analítica estructurada
    result = {
        "document_id": doc_id,
        "filename": filename,
        "processed_at": timestamp,
        "environment": ENVIRONMENT,
        "statistics": {
            "character_count": char_count,
            "word_count": word_count,
            "size_bytes": content_size_bytes,
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

    # [EN] 6. Save result to persistent storage if directory is writable
    #      Verifies persistence across container restarts when Azure Storage is mounted.
    # [ES] 6. Guarda el resultado en almacenamiento persistente si el directorio es accesible
    #      Garantiza persistencia ante reinicios del contenedor al montar Azure Storage.
    storage_available = ensure_storage_directory()
    if storage_available:
        try:
            result_path = os.path.join(STORAGE_PATH, f"{doc_id}.json")
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            result["storage"] = {"saved": True, "path": result_path}
            logger.info(f"Result successfully persisted to: {result_path}")
        except Exception as e:
            logger.error(f"Failed to persist result to disk: {e}")
            result["storage"] = {"saved": False, "error": str(e)}
    else:
        result["storage"] = {"saved": False, "reason": "Persistent storage unavailable"}

    logger.info(f"Document processing completed successfully: {doc_id}")
    return jsonify(result)


# -----------------------------------------------------------------------------
# [EN] Catalog Query Endpoint - List All Processed Documents
#      Scans persistent storage directory (/home/processed) and returns file metadata.
# [ES] Endpoint de Consulta de Catálogo - Listar Documentos Procesados
#      Examina el directorio persistente (/home/processed) y retorna metadatos de archivos.
# -----------------------------------------------------------------------------
@app.route("/documents", methods=["GET"])
def list_documents():
    """
    [EN] List all processed JSON documents stored on persistent volume.
    [ES] Lista todos los documentos JSON procesados almacenados en el volumen persistente.
    """
    logger.info("Listing processed documents from storage directory")

    if not ensure_storage_directory():
        return jsonify({"documents": [], "error": "Storage directory unavailable"}), 500

    try:
        files = []
        for filename in os.listdir(STORAGE_PATH):
            if filename.endswith(".json"):
                filepath = os.path.join(STORAGE_PATH, filename)
                stat = os.stat(filepath)
                files.append(
                    {
                        "document_id": filename.replace(".json", ""),
                        "size_bytes": stat.st_size,
                        "created_at": datetime.fromtimestamp(
                            stat.st_ctime
                        ).isoformat(),
                    }
                )
        return jsonify({"documents": files, "count": len(files)})
    except Exception as e:
        logger.error(f"Failed to list documents in '{STORAGE_PATH}': {e}")
        return jsonify({"documents": [], "error": str(e)}), 500


# -----------------------------------------------------------------------------
# [EN] Document Retrieval Endpoint - Fetch Single Document by ID
# [ES] Endpoint de Recuperación de Documento - Obtener Documento por ID
# -----------------------------------------------------------------------------
@app.route("/documents/<doc_id>", methods=["GET"])
def get_document(doc_id):
    """
    [EN] Retrieve stored analysis JSON for a specific document ID.
    [ES] Recupera el JSON de análisis almacenado para un ID de documento específico.
    """
    logger.info(f"Retrieving document by ID: {doc_id}")

    filepath = os.path.join(STORAGE_PATH, f"{doc_id}.json")

    # [EN] Guard: verify file exists before attempting read
    # [ES] Validación: verifica existencia del archivo antes de intentar lectura
    if not os.path.exists(filepath):
        logger.warning(f"Document ID '{doc_id}' not found at '{filepath}'")
        return jsonify({"error": f"Document '{doc_id}' not found"}), 404

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        logger.error(f"Failed to read document '{filepath}': {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# [EN] Local Development Entrypoint
#      In production, Gunicorn launches 'main:app' directly via CMD in Dockerfile.
# [ES] Punto de Entrada para Desarrollo Local
#      En producción, Gunicorn invoca 'main:app' directamente mediante CMD en Dockerfile.
# =============================================================================
if __name__ == "__main__":
    logger.info(f"Starting Document Processing API in '{ENVIRONMENT}' mode")
    logger.info(f"Configuration: MAX_SIZE={MAX_DOCUMENT_SIZE_MB}MB, TIMEOUT={PROCESSING_TIMEOUT_SECONDS}s")

    # [EN] Ensure storage directory is prepared prior to accepting traffic
    # [ES] Asegura que el directorio de almacenamiento esté listo antes de recibir tráfico
    ensure_storage_directory()

    # [EN] Bind to port from environment (defaults to 80 for container compatibility)
    # [ES] Enlaza al puerto de la variable de entorno (por defecto 80 para contenedores)
    port = int(os.getenv("PORT", "80"))
    app.run(host="0.0.0.0", port=port)
