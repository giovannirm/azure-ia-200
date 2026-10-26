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

# =============================================================================
# [EN] Step 3: Layer caching for dependencies
#      Copy requirements.txt separately so dependency layers are cached across builds.
# [ES] Paso 3: Caché de capas para dependencias
#      Copia requirements.txt por separado para cachear dependencias si el código cambia.
# =============================================================================
COPY requirements.txt .

# =============================================================================
# [EN] Step 4: Install Python packages without cache tarballs
#      --no-cache-dir eliminates pip download artifacts, minimizing layer size.
# [ES] Paso 4: Instalar paquetes de Python sin archivos de caché temporal
#      --no-cache-dir elimina artefactos descargados por pip, optimizando el tamaño final.
# =============================================================================
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# [EN] Step 5: Copy application source code
#      Placed after dependency installation to maximize Docker layer cache hits.
# [ES] Paso 5: Copiar código fuente de la aplicación
#      Ubicado tras la instalación de paquetes para acelerar compilaciones incrementales.
# =============================================================================
COPY main.py .

# =============================================================================
# [EN] Step 6: Twelve-Factor Configuration & Port Metadata
#      PORT=8000 matches Azure Container Apps target port convention.
#      EXPOSE is informational metadata for container orchestrators and ingress proxies.
# [ES] Paso 6: Configuración Twelve-Factor y Metadatos de Puerto
#      PORT=8000 coincide con la convención de puerto de destino de Azure Container Apps.
#      EXPOSE es metadato informativo para orquestadores de contenedores y proxies de entrada.
# =============================================================================
ENV PORT=8000
EXPOSE 8000

# =============================================================================
# [EN] Step 7: Production WSGI server (Gunicorn) with shell expansion
#      Launches Gunicorn listening on 0.0.0.0 with 2 worker processes.
#      --access-logfile -: Streams HTTP access logs directly to stdout (captured by Log Analytics).
# [ES] Paso 7: Servidor WSGI de producción (Gunicorn) con expansión de shell
#      Inicia Gunicorn escuchando en 0.0.0.0 con 2 procesos de trabajo (workers).
#      --access-logfile -: Envía logs de acceso HTTP directamente a stdout (capturados por Log Analytics).
# =============================================================================
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile - main:app"]
