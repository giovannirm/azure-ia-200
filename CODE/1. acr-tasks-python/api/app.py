# =============================================================================
# [EN] Framework and OS module imports
# [ES] Importación del framework Flask y módulo de sistema operativo
# =============================================================================
from flask import Flask, jsonify
import os

# [EN] Create the Flask application instance
# [ES] Crear la instancia principal de la aplicación Flask
app = Flask(__name__)


# -----------------------------------------------------------------------------
# [EN] Health Check Endpoint
#      Used by container orchestrators (like Kubernetes or Azure Container Apps)
#      to perform liveness and readiness probes.
# [ES] Endpoint de Comprobación de Salud
#      Utilizado por orquestadores (Kubernetes, Azure Container Apps) para
#      sondeos de estado (liveness y readiness probes).
# -----------------------------------------------------------------------------
@app.route('/health')
def health():
    """
    [EN] Health check endpoint for container orchestrators.
    [ES] Endpoint de verificación de disponibilidad y salud del servicio.
    """
    return jsonify({
        "status": "healthy",
        # [EN] Read version from env var, defaulting to 1.0.0
        # [ES] Lee la versión desde la variable de entorno, por defecto 1.0.0
        "version": os.getenv("APP_VERSION", "1.0.0")
    })


# -----------------------------------------------------------------------------
# [EN] Prediction Endpoint
#      Simulates an ML inference endpoint - in production, this calls a trained model.
# [ES] Endpoint de Predicción
#      Simula la inferencia de un modelo de ML - en producción ejecuta el modelo real.
# -----------------------------------------------------------------------------
@app.route('/predict')
def predict():
    """
    [EN] Simulated machine learning inference endpoint.
    [ES] Endpoint simulado de inferencia para Machine Learning.
    """
    return jsonify({
        "prediction": "sample-result",
        "confidence": 0.95,
        # [EN] Model version read dynamically from runtime environment
        # [ES] Versión del modelo leída dinámicamente desde el entorno en tiempo de ejecución
        "model_version": os.getenv("MODEL_VERSION", "v1")
    })


# -----------------------------------------------------------------------------
# [EN] Root Endpoint
#      Provides API metadata and catalogs available route endpoints.
# [ES] Endpoint Raíz
#      Proporciona metadatos del servicio y cataloga las rutas disponibles.
# -----------------------------------------------------------------------------
@app.route('/')
def root():
    """
    [EN] Root introspective endpoint with API metadata and route listing.
    [ES] Endpoint raíz introspectivo con metadatos de la API y lista de rutas.
    """
    return jsonify({
        "name": "Inference API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        # [EN] List of exposed endpoints
        # [ES] Lista de endpoints expuestos
        "endpoints": ["/health", "/predict"]
    })


# -----------------------------------------------------------------------------
# [EN] Application Entry Point
#      Runs the development server on port 5000.
#      CRITICAL: host='0.0.0.0' binds all interfaces, enabling traffic from outside the container.
# [ES] Punto de Entrada de la Aplicación
#      Inicia el servidor en el puerto 5000.
#      CRÍTICO: host='0.0.0.0' escucha en todas las interfaces para admitir tráfico externo al contenedor.
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # [EN] host='0.0.0.0' allows incoming container network connections
    # [ES] host='0.0.0.0' permite conexiones entrantes a través de la red del contenedor
    app.run(host='0.0.0.0', port=5000)