# =============================================================================
# [EN] Step 1: Base image - Lightweight Debian-based Python runtime
# [ES] Paso 1: Imagen base - Entorno Python ligero basado en Debian (reduce tamaño y superficie de ataque)
# =============================================================================
FROM python:3.11-slim

# =============================================================================
# [EN] Step 2: Working directory - Isolates application files from system root
# [ES] Paso 2: Directorio de trabajo - Aísla los archivos de la app de la raíz del sistema
# =============================================================================
WORKDIR /app

# =============================================================================
# [EN] Step 3: Install dependencies without caching tarballs to minimize layer size
# [ES] Paso 3: Instalar dependencias sin guardar caché temporal para optimizar tamaño de capa
# =============================================================================
RUN pip install --no-cache-dir flask

# =============================================================================
# [EN] Step 4: Copy source code - Placed after pip install to leverage layer caching
# [ES] Paso 4: Copiar código fuente - Colocado tras dependencias para aprovechar caché de capas
# =============================================================================
COPY app.py .

# =============================================================================
# [EN] Step 5: Default environment variables (Twelve-Factor App configuration)
# [ES] Paso 5: Variables de entorno predeterminadas (desacopla configuración de código)
# =============================================================================
ENV APP_VERSION=1.0.0
ENV MODEL_VERSION=v1

# =============================================================================
# [EN] Step 6: Expose application port (informational metadata for orchestrators)
# [ES] Paso 6: Exponer puerto de la app (metadato informativo para orquestadores)
# =============================================================================
EXPOSE 5000

# =============================================================================
# [EN] Step 7: Launch application in exec form (allows graceful SIGTERM handling)
# [ES] Paso 7: Iniciar aplicación en formato exec (permite apagado limpio mediante SIGTERM)
# =============================================================================
CMD ["python", "app.py"]