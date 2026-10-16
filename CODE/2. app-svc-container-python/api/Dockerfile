# =============================================================================
# [EN] Step 1: Base image - Lightweight Debian-based Python runtime
#      Optimized for production containers: reduces image footprint and attack surface.
# [ES] Paso 1: Imagen base - Entorno Python ligero basado en Debian
#      Optimizado para contenedores en producción: reduce huella de disco y superficie de ataque.
# =============================================================================
FROM python:3.11-slim

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
# [EN] Step 6: Create default storage directory for local testing
#      In Azure App Service, /home will be mounted over CIFS/SMB if persistent storage is enabled.
# [ES] Paso 6: Crear directorio de almacenamiento predeterminado para pruebas locales
#      En Azure App Service, /home se montará vía CIFS/SMB al activar almacenamiento persistente.
# =============================================================================
RUN mkdir -p /home/processed

# =============================================================================
# [EN] Step 7: Expose container port (informational metadata for App Service routing)
# [ES] Paso 7: Exponer puerto del contenedor (metadato informativo para App Service)
# =============================================================================
EXPOSE 80

# =============================================================================
# [EN] Step 8: Production WSGI server (Gunicorn) in exec form
#      Exec form (JSON array) ensures Gunicorn receives SIGTERM signals directly for graceful shutdown.
#      --bind 0.0.0.0:80: Listens on all interfaces on port 80.
#      --workers 2: 2 concurrent worker processes for CPU concurrency.
#      --access-logfile -: Streams HTTP access logs directly to stdout (captured by App Service Log Stream).
# [ES] Paso 8: Servidor WSGI de producción (Gunicorn) en formato exec
#      Formato exec (array JSON) asegura que Gunicorn reciba señales SIGTERM para apagado controlado.
#      --bind 0.0.0.0:80: Escucha en todas las interfaces en el puerto 80.
#      --workers 2: 2 procesos de trabajo concurrentes para atender peticiones.
#      --access-logfile -: Emite registros de acceso a stdout (capturados por App Service Log Stream).
# =============================================================================
CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "2", "--access-logfile", "-", "main:app"]
