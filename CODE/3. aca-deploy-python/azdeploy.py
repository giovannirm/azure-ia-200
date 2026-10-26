# =============================================================================
# [EN] User Configuration - Change the values of these variables as needed.
# [ES] Configuración de Usuario - Modifique los valores de estas variables según sea necesario.
# =============================================================================

# [EN] Resource Group name where all lab resources will be organized
# [ES] Nombre del Grupo de Recursos donde se organizarán todos los recursos del laboratorio
rg = "<your-resource-group-name>"

# [EN] Azure region for provisioning resources (e.g., eastus, westeurope)
# [ES] Región de Azure para aprovisionar los recursos (ej. eastus, westeurope)
location = "<your-azure-region>"

# =============================================================================
# [EN] AUTOMATION ENGINE - Core Python logic and Azure CLI wrapper.
#      Do not modify anything below unless customizing automation behavior.
# [ES] MOTOR DE AUTOMATIZACIÓN - Lógica interna de Python y llamadas a Azure CLI.
#      No modifique nada debajo de esta línea salvo para personalizar la automatización.
# =============================================================================

# [EN] Module for cryptographic hash generation (SHA-1 for global DNS uniqueness)
# [ES] Módulo para generar hashes criptográficos (SHA-1 para unicidad global de DNS)
import hashlib

# [EN] Access OS environment and working directory
# [ES] Acceso a variables de entorno y directorio del SO
import os

# [EN] High-level file and path operations (which)
# [ES] Operaciones de rutas y ejecutables en PATH (which)
import shutil

# [EN] Spawns external system processes (Azure CLI)
# [ES] Ejecución de subprocesos externos del sistema (Azure CLI)
import subprocess

# [EN] System parameters and interpreter exit control
# [ES] Parámetros del intérprete y control de salida (sys.exit)
import sys

# [EN] Modern object-oriented filesystem paths
# [ES] Manejo orientado a objetos de rutas de archivos
from pathlib import Path

# =============================================================================
# [EN] Application Deployment Parameters & Service Constants
# [ES] Parámetros de Despliegue de la Aplicación y Constantes del Servicio
# =============================================================================

# [EN] Name of the target Azure Container App microservice
# [ES] Nombre del microservicio destino en Azure Container Apps
CONTAINER_APP_NAME = "ai-api"

# [EN] Name and version tag of the container image stored in ACR
# [ES] Nombre y etiqueta de versión de la imagen de contenedor almacenada en ACR
CONTAINER_IMAGE = "ai-api:v1"

# [EN] Target HTTP listener port inside the container (8000 for Gunicorn)
# [ES] Puerto de escucha HTTP de destino dentro del contenedor (8000 para Gunicorn)
TARGET_PORT = "8000"

# [EN] Configured OpenAI / Cognitive AI model name for document processing
# [ES] Nombre del modelo de IA cognitiva / OpenAI configurado para procesamiento
MODEL_NAME = "gpt-5.1"

# [EN] Demo API key for embeddings; injected into ACA as an encrypted secret
# [ES] Clave de API de prueba para embeddings; inyectada en ACA como secreto cifrado
EMBEDDINGS_API_KEY = "demo-key-12345"

# -----------------------------------------------------------------------------
# [EN] Environment Tuning
# [ES] Ajuste del Entorno de Ejecución
# -----------------------------------------------------------------------------
# [EN] Configure Azure CLI to output errors only, suppressing preview and deprecation banners
# [ES] Configura Azure CLI para mostrar solo errores, suprimiendo avisos de preview y deprecación
os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")

# [EN] In-memory cache dictionary to store resolved executable binary paths
# [ES] Diccionario de caché en memoria para almacenar rutas de binarios ya resueltos
_EXE_CACHE: dict[str, str] = {}


# -----------------------------------------------------------------------------
# [EN] Executable Resolver
#      Locates command line tools on PATH, handling platform differences (Windows az.cmd).
# [ES] Resolutor de Ejecutables
#      Localiza herramientas en el PATH del sistema, gestionando diferencias de SO (az.cmd).
# -----------------------------------------------------------------------------
def _resolve_exe(name: str) -> str:
    """
    [EN] Locate an executable on PATH (handles az.cmd on Windows).
    [ES] Localiza un ejecutable en el PATH del sistema (soporta az.cmd en Windows).
    """
    # [EN] 1. Return cached executable path if previously resolved
    # [ES] 1. Retorna la ruta en caché si ya fue resuelta anteriormente
    cached = _EXE_CACHE.get(name)
    if cached:
        return cached

    # [EN] 2. Locate binary in system PATH
    # [ES] 2. Busca el binario ejecutable en el PATH del sistema
    resolved = shutil.which(name)

    # [EN] 3. Terminate execution with error message if tool is missing
    # [ES] 3. Detiene la ejecución con mensaje descriptivo si la herramienta no existe
    if not resolved:
        print(f"Error: '{name}' not found on PATH. Install it and retry.")
        sys.exit(1)

    # [EN] 4. Store resolved absolute path in cache and return
    # [ES] 4. Almacena la ruta absoluta en la caché y la retorna
    _EXE_CACHE[name] = resolved
    return resolved


# -----------------------------------------------------------------------------
# [EN] Silent Subprocess Runner
#      Executes Azure CLI commands suppressing stdout unless an error occurs.
# [ES] Ejecutor Silencioso de Subprocesos
#      Ejecuta comandos de Azure CLI silenciando stdout salvo en caso de error.
# -----------------------------------------------------------------------------
def run_quiet(description: str, argv: list[str]) -> bool:
    """
    [EN] Run a command, print an error on failure, return success as bool.
    [ES] Ejecuta un comando en silencio, imprime el error si falla y retorna el resultado como booleano.
    """
    # [EN] Replace command name with resolved absolute path, unpacking remaining arguments
    # [ES] Reemplaza el comando inicial por su ruta absoluta y desempaqueta los argumentos restantes
    argv = [_resolve_exe(argv[0]), *argv[1:]]

    # [EN] Execute child process capturing stdout and stderr
    # [ES] Ejecuta el subproceso capturando la salida estándar y de errores
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        combined = (result.stdout or "") + (result.stderr or "")
        if combined.strip():
            print(combined.rstrip())
        return False
    return True


# -----------------------------------------------------------------------------
# [EN] Azure CLI Query Helper
#      Runs an az CLI query command and returns the trimmed stdout string.
# [ES] Función de Consulta de Azure CLI
#      Ejecuta una consulta de Azure CLI y retorna la salida de texto recortada.
# -----------------------------------------------------------------------------
def az_query(argv: list[str]) -> str:
    """
    [EN] Run an Azure CLI command and return its trimmed stdout string.
    [ES] Ejecuta un comando de Azure CLI y retorna su salida estándar limpia de espacios.
    """
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


# -----------------------------------------------------------------------------
# [EN] Console Management Helpers
# [ES] Funciones Auxiliares de Gestión de Consola
# -----------------------------------------------------------------------------
def clear_screen() -> None:
    """
    [EN] Clear terminal window across Windows (cls) and Unix (clear / ANSI escape codes).
    [ES] Limpia la pantalla de la terminal en Windows (cls) y Unix (clear / códigos ANSI).
    """
    cmd = "cls" if os.name == "nt" else "clear"
    if os.system(cmd) != 0:
        sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
        sys.stdout.flush()


def pause() -> None:
    """
    [EN] Wait for user acknowledgement before proceeding.
    [ES] Espera la confirmación del usuario antes de continuar.
    """
    try:
        input("Press Enter to continue...")
    except EOFError:
        print()


# -----------------------------------------------------------------------------
# [EN] Environment File Generator
#      Exports configured variables side-by-side for Bash (.env) and PowerShell (.env.ps1).
# [ES] Generador de Archivos de Variables de Entorno
#      Exporta variables de configuración en paralelo para Bash (.env) y PowerShell (.env.ps1).
# -----------------------------------------------------------------------------
def write_env_files(env_vars: dict[str, str], directory: str = ".") -> None:
    """
    [EN] Write .env (bash) and .env.ps1 (PowerShell) side by side with escaped values.
    [ES] Escribe archivos .env (Bash) y .env.ps1 (PowerShell) con caracteres de escape seguros.
    """
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    # [EN] Escape characters for Bash export strings
    # [ES] Escapa caracteres especiales para cadenas de exportación en Bash
    def bash_escape(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("$", "\\$")
            .replace("`", "\\`")
        )

    # [EN] Escape characters for PowerShell $env: variable assignment
    # [ES] Escapa caracteres especiales para asignación de variables $env: en PowerShell
    def ps_escape(value: str) -> str:
        return (
            value.replace("`", "``")
            .replace('"', '`"')
            .replace("$", "`$")
        )

    bash_lines = [f'export {k}="{bash_escape(v)}"\n' for k, v in env_vars.items()]
    ps_lines = [f'$env:{k} = "{ps_escape(v)}"\n' for k, v in env_vars.items()]

    with open(target_dir / ".env", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(bash_lines)
    with open(target_dir / ".env.ps1", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(ps_lines)


# -----------------------------------------------------------------------------
# [EN] Azure Authentication Preflight
#      Ensures the developer is authenticated against Azure via az login.
# [ES] Verificación de Autenticación en Azure
#      Garantiza que el desarrollador esté autenticado en Azure mediante az login.
# -----------------------------------------------------------------------------
def require_az_login() -> str:
    """
    [EN] Verify active Azure CLI login session and retrieve signed-in user object ID.
    [ES] Verifica la sesión activa en Azure CLI y obtiene el ID de objeto del usuario autenticado.
    """
    user_object_id = az_query(
        ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"]
    )
    if not user_object_id:
        print("Error: Not authenticated with Azure. Please run: az login")
        sys.exit(1)
    return user_object_id


# -----------------------------------------------------------------------------
# [EN] Deterministic Name Derivation (Global DNS Uniqueness)
#      Computes an 8-character SHA-1 hash to guarantee unique resource names.
# [ES] Derivación Determinista de Nombres (Unicidad Global de DNS)
#      Calcula un hash SHA-1 de 8 caracteres para garantizar nombres de recursos únicos en Azure.
# -----------------------------------------------------------------------------
def _derived_names(user_object_id: str) -> tuple[str, str]:
    """
    [EN] Derive unique ACR and ACA Environment names using a SHA-1 hash of the user ID.
    [ES] Deriva nombres únicos para ACR y Container Apps Environment usando un hash SHA-1 del ID de usuario.
    """
    # [EN] Generate 8-character lowercase hexadecimal hash
    # [ES] Genera hash hexadecimal en minúsculas de 8 caracteres
    user_hash = hashlib.sha1(user_object_id.encode("utf-8")).hexdigest()[:8]
    return f"acr{user_hash}", f"aca-env-{user_hash}"


# -----------------------------------------------------------------------------
# [EN] Resource Group Provisioning
#      Idempotent check and creation of the target Azure Resource Group.
# [ES] Aprovisionamiento del Grupo de Recursos
#      Verificación idempotente y creación del Grupo de Recursos de Azure.
# -----------------------------------------------------------------------------
def create_resource_group() -> bool:
    """
    [EN] Check if resource group exists; create it if not found.
    [ES] Comprueba si el grupo de recursos existe; lo crea si no se encuentra.
    """
    print(f"Checking/creating resource group '{rg}'...")
    exists = az_query(["az", "group", "exists", "--name", rg])
    if exists == "false":
        if not run_quiet(
            "Create resource group",
            ["az", "group", "create", "--name", rg, "--location", location],
        ):
            return False
        print(f"Resource group created: {rg}")
    else:
        print(f"Resource group already exists: {rg}")
    return True


# -----------------------------------------------------------------------------
# [EN] Azure Container Registry & Serverless Build
#      Provisions ACR (Basic SKU) and executes a cloud-native build using ACR Tasks.
# [ES] Azure Container Registry y Compilación Serverless
#      Aprovisiona ACR (SKU Basic) y ejecuta una compilación serverless usando ACR Tasks.
# -----------------------------------------------------------------------------
def create_acr_and_build_image(acr_name: str) -> bool:
    """
    [EN] Provision Azure Container Registry and build/push container image via ACR Tasks.
    [ES] Aprovisiona Azure Container Registry y compila/sube la imagen mediante ACR Tasks.
    """
    if not create_resource_group():
        return False
    print()
    print(f"Creating Azure Container Registry '{acr_name}'...")

    # [EN] Check if ACR already exists
    # [ES] Verifica si el ACR ya existe
    existing = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "name", "-o", "tsv"]
    )
    if existing:
        print(f"ACR already exists: {acr_name}")
    else:
        # [EN] Provision ACR with admin user disabled (Zero-Trust via Managed Identity)
        # [ES] Aprovisiona ACR con usuario administrador deshabilitado (Zero-Trust vía Managed Identity)
        if not run_quiet(
            "Create Azure Container Registry",
            [
                "az", "acr", "create",
                "--resource-group", rg,
                "--name", acr_name,
                "--sku", "Basic",
                "--admin-enabled", "false",
            ],
        ):
            return False
        print(f"ACR created: {acr_name}")
    print(f"  Login server: {acr_name}.azurecr.io")

    print()
    print("Building and pushing container image to ACR...")
    print("This may take a few minutes...")
    # [EN] Execute serverless build in Azure without requiring local Docker daemon
    # [ES] Ejecuta compilación serverless en Azure sin requerir Docker daemon local
    if not run_quiet(
        "Build and push container image",
        [
            "az", "acr", "build",
            "--resource-group", rg,
            "--registry", acr_name,
            "--image", CONTAINER_IMAGE,
            "--file", "api/Dockerfile",
            "--no-logs",
            "api/",
        ],
    ):
        return False
    print(f"Image built and pushed: {acr_name}.azurecr.io/{CONTAINER_IMAGE}")
    return True


# -----------------------------------------------------------------------------
# [EN] Container Apps Environment Provisioning
#      Creates the shared network boundary and Log Analytics workspace for ACA.
# [ES] Aprovisionamiento del Container Apps Environment
#      Crea la frontera de red compartida y el espacio de trabajo Log Analytics para ACA.
# -----------------------------------------------------------------------------
def create_containerapps_environment(acr_name: str, aca_env: str) -> bool:
    """
    [EN] Provision Container Apps environment and persist environment variables.
    [ES] Aprovisiona el entorno de Container Apps y persiste las variables de entorno.
    """
    if not create_resource_group():
        return False
    print()
    print(f"Creating Container Apps environment '{aca_env}' (if needed)...")
    print("This may take a few minutes...")

    existing = az_query(
        ["az", "containerapp", "env", "show",
         "--name", aca_env, "--resource-group", rg,
         "--query", "name", "-o", "tsv"]
    )
    if existing:
        print(f"Container Apps environment already exists: {aca_env}")
    else:
        # [EN] Create ACA managed Kubernetes environment
        # [ES] Crea el entorno Kubernetes administrado para ACA
        if not run_quiet(
            "Create Container Apps environment",
            [
                "az", "containerapp", "env", "create",
                "--name", aca_env,
                "--resource-group", rg,
                "--location", location,
            ],
        ):
            return False
        print(f"Container Apps environment created: {aca_env}")

    # [EN] Persist all configuration variables to .env and .env.ps1
    # [ES] Persiste todas las variables de configuración en .env y .env.ps1
    write_env_files({
        "RESOURCE_GROUP": rg,
        "ACR_NAME": acr_name,
        "ACR_SERVER": f"{acr_name}.azurecr.io",
        "ACA_ENVIRONMENT": aca_env,
        "CONTAINER_APP_NAME": CONTAINER_APP_NAME,
        "CONTAINER_IMAGE": CONTAINER_IMAGE,
        "TARGET_PORT": TARGET_PORT,
        "MODEL_NAME": MODEL_NAME,
        "EMBEDDINGS_API_KEY": EMBEDDINGS_API_KEY,
        "LOCATION": location,
    })
    print()
    print("Environment variables saved to .env and .env.ps1")
    print("Run 'source .env' (Bash) or '. .\\.env.ps1' (PowerShell) to load them.")
    return True


# -----------------------------------------------------------------------------
# [EN] Deployment Status Inspector
#      Verifies provisioning states for ACA Environment and ACR image repository.
# [ES] Inspector de Estado de Despliegue
#      Verifica los estados de aprovisionamiento de Container Apps y repositorio ACR.
# -----------------------------------------------------------------------------
def check_deployment_status(acr_name: str, aca_env: str) -> bool:
    """
    [EN] Inspect deployment status of ACR and Container Apps Environment.
    [ES] Inspecciona el estado de despliegue del ACR y del Container Apps Environment.
    """
    print("Checking deployment status...")
    print()

    # [EN] Query Container Apps Environment provisioning state
    # [ES] Consulta el estado de aprovisionamiento del Container Apps Environment
    print(f"Container Apps Environment ({aca_env}):")
    env_status = az_query(
        ["az", "containerapp", "env", "show",
         "--resource-group", rg, "--name", aca_env,
         "--query", "properties.provisioningState", "-o", "tsv"]
    )
    if env_status:
        print(f"  Status: {env_status}")
        if env_status == "Succeeded":
            print("  Container Apps environment is ready")
    else:
        print("  Status: Not created")

    print()
    # [EN] Query Azure Container Registry status and image existence
    # [ES] Consulta el estado de Azure Container Registry y la existencia de la imagen
    print(f"Azure Container Registry ({acr_name}):")
    acr_status = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "provisioningState", "-o", "tsv"]
    )
    if acr_status:
        print(f"  Status: {acr_status}")
        if acr_status == "Succeeded":
            print("  ACR is ready")
            image_exists = az_query(
                ["az", "acr", "repository", "show",
                 "--name", acr_name, "--image", CONTAINER_IMAGE,
                 "--query", "name", "-o", "tsv"]
            )
            if image_exists:
                print(f"  Container image: {CONTAINER_IMAGE}")
            else:
                print("  Container image not found")
    else:
        print("  Status: Not created")
    return True


# -----------------------------------------------------------------------------
# [EN] Interactive Terminal Menu
# [ES] Menú Interactivo de Terminal
# -----------------------------------------------------------------------------
def show_menu(acr_name: str, aca_env: str) -> None:
    """
    [EN] Render the interactive command-line deployment menu.
    [ES] Muestra el menú interactivo de despliegue en la línea de comandos.
    """
    clear_screen()
    print("=====================================================================")
    print("    Azure Container Apps Exercise - Deployment Script")
    print("=====================================================================")
    print(f"Resource Group: {rg}")
    print(f"Location: {location}")
    print(f"Container Apps Environment: {aca_env}")
    print(f"ACR Name: {acr_name}")
    print("=====================================================================")
    print("1. Create Azure Container Registry and build container image")
    print("2. Create Container Apps environment")
    print("3. Check deployment status")
    print("4. Exit")
    print("=====================================================================")


# -----------------------------------------------------------------------------
# [EN] Script Directory Preflight Verification
# [ES] Verificación Previa del Directorio de Ejecución
# -----------------------------------------------------------------------------
def _preflight() -> None:
    """
    [EN] Validate that api/Dockerfile exists in the current project structure.
    [ES] Valida que api/Dockerfile exista en la estructura del proyecto actual.
    """
    script_dir = Path(__file__).resolve().parent
    if not (script_dir / "api" / "Dockerfile").is_file():
        print(
            "Error: 'api/Dockerfile' is missing next to azdeploy.py. "
            "Make sure you kept the exercise folder intact."
        )
        sys.exit(1)
    os.chdir(script_dir)


# =============================================================================
# [EN] Main Orchestration Flow
# [ES] Flujo Principal de Orquestación
# =============================================================================
def main() -> None:
    """
    [EN] Main execution loop managing Azure authentication and interactive user options.
    [ES] Bucle principal de ejecución que gestiona la autenticación y opciones interactivas.
    """
    _preflight()
    user_object_id = require_az_login()
    acr_name, aca_env = _derived_names(user_object_id)

    while True:
        show_menu(acr_name, aca_env)
        choice = input("Please select an option (1-4): ").strip()
        if choice in {"1", "2", "3", "4"}:
            clear_screen()

        if choice == "1":
            print()
            create_acr_and_build_image(acr_name)
            print()
            pause()
        elif choice == "2":
            print()
            create_containerapps_environment(acr_name, aca_env)
            print()
            pause()
        elif choice == "3":
            print()
            check_deployment_status(acr_name, aca_env)
            print()
            pause()
        elif choice == "4":
            print("Exiting...")
            clear_screen()
            sys.exit(0)
        else:
            print()
            print("Invalid option. Please select 1-4.")
            print()
            pause()


# =============================================================================
# [EN] Python Interpreter Entrypoint
# [ES] Punto de Entrada del Intérprete Python
# =============================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
