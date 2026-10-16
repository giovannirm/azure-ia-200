# =============================================================================
# [EN] User Configuration - Change the values of these variables as needed.
# [ES] Configuración de Usuario - Modifique los valores de estas variables según sea necesario.
# =============================================================================

# [EN] Resource Group name where all lab resources will be organized
# [ES] Nombre del Grupo de Recursos donde se organizarán todos los recursos del laboratorio
rg = "<your-resource-group-name>"

# [EN] Azure region for provisioning resources (e.g., eastus2, westeurope)
# [ES] Región de Azure para aprovisionar los recursos (ej. eastus2, westeurope)
location = "<your-azure-region>"

# =============================================================================
# [EN] AUTOMATION ENGINE - Core Python logic and Azure CLI wrapper.
#      Do not modify anything below unless customizing automation behavior.
# [ES] MOTOR DE AUTOMATIZACIÓN - Lógica interna de Python y llamadas a Azure CLI.
#      No modifique nada debajo de esta línea salvo para personalizar la automatización.
# =============================================================================

# [EN] Cryptographic hashing library used for deterministic naming
# [ES] Biblioteca de hashing criptográfico para derivación determinista de nombres
import hashlib

# [EN] Operating system interface for environment variables and process control
# [ES] Interfaz del sistema operativo para variables de entorno y control de procesos
import os

# [EN] File operations utility to resolve binary paths on PATH
# [ES] Utilidades de archivos para resolución de binarios en el PATH del sistema
import shutil

# [EN] Subprocess execution library to invoke Azure CLI commands
# [ES] Biblioteca de subprocesos para ejecutar comandos de Azure CLI
import subprocess

# [EN] System-specific parameters and exit handler functions
# [ES] Parámetros específicos del sistema y funciones de terminación de proceso
import sys

# [EN] Object-oriented filesystem path manipulation
# [ES] Manipulación orientada a objetos de rutas en el sistema de archivos
from pathlib import Path

# [EN] Target container image repository tag for the document processing microservice
# [ES] Etiqueta del repositorio de la imagen de contenedor para el microservicio de procesamiento
CONTAINER_IMAGE = "docprocessor:v1"

# -----------------------------------------------------------------------------
# [EN] Environment Tuning
# [ES] Ajuste del Entorno de Ejecución
# -----------------------------------------------------------------------------
# [EN] Suppress Azure CLI preview and deprecation warnings from subprocess output
# [ES] Suprime advertencias de preview y deprecación de Azure CLI en la salida de subprocesos
os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")

# [EN] In-memory cache dictionary to avoid repeated PATH lookups for executables
# [ES] Diccionario de caché en memoria para evitar búsquedas redundantes en el PATH
_EXE_CACHE: dict[str, str] = {}


def _resolve_exe(name: str) -> str:
    """
    [EN] Locate an executable on PATH (handles az.cmd on Windows).
    [ES] Localiza un ejecutable en el PATH del sistema (soporta az.cmd en Windows).
    """
    # [EN] 1. Check in-memory cache to return early if already resolved
    # [ES] 1. Revisa la caché en memoria para retornar temprano si ya fue resuelto
    cached = _EXE_CACHE.get(name)
    if cached:
        return cached

    # [EN] 2. Search executable across system PATH directories
    # [ES] 2. Busca el archivo ejecutable en los directorios del PATH del sistema
    resolved = shutil.which(name)
    if not resolved:
        print(f"Error: '{name}' not found on PATH. Install it and retry.")
        sys.exit(1)

    # [EN] 3. Store in cache dictionary and return resolved path
    # [ES] 3. Almacena en la caché y retorna la ruta resuelta
    _EXE_CACHE[name] = resolved
    return resolved


def run_quiet(description: str, argv: list[str]) -> bool:
    """
    [EN] Run a command, capture output, print error on failure, and return success bool.
    [ES] Ejecuta un comando, captura la salida, imprime error si falla y retorna booleano de éxito.
    """
    # [EN] Replace binary name with its resolved absolute executable path
    # [ES] Reemplaza el nombre del comando con su ruta absoluta resuelta
    argv = [_resolve_exe(argv[0]), *argv[1:]]

    # [EN] Execute child process with captured stdout/stderr to keep terminal clean
    # [ES] Ejecuta el subproceso capturando stdout y stderr para mantener limpia la consola
    result = subprocess.run(argv, capture_output=True, text=True, check=False)

    # [EN] Non-zero return code indicates command execution failure
    # [ES] Un código de retorno distinto de cero indica falla en la ejecución
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        combined = (result.stdout or "") + (result.stderr or "")
        if combined.strip():
            print(combined.rstrip())
        return False
    return True


def az_query(argv: list[str]) -> str:
    """
    [EN] Run an `az ... -o tsv` probe and return stripped stdout string (or empty on error).
    [ES] Ejecuta una consulta `az ... -o tsv` y retorna stdout limpio (o cadena vacía ante error).
    """
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def clear_screen() -> None:
    """
    [EN] Clear terminal display across bash, zsh, PowerShell, cmd, and Git Bash.
    [ES] Limpia la pantalla de la terminal en bash, zsh, PowerShell, cmd y Git Bash.
    """
    cmd = "cls" if os.name == "nt" else "clear"
    if os.system(cmd) != 0:
        # [EN] Fallback ANSI escape sequences for screen clearing
        # [ES] Secuencia de escape ANSI alternativa para limpiar pantalla
        sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
        sys.stdout.flush()


def pause(prompt: str = "Press Enter to continue...") -> None:
    """
    [EN] Block execution until user presses Enter (handles EOF safely).
    [ES] Pausa la ejecución hasta presionar Enter (gestiona fin de archivo EOF).
    """
    try:
        input(prompt)
    except EOFError:
        print()


def require_az_login() -> str:
    """
    [EN] Verify Azure CLI session; return signed-in user's Object ID or exit with error.
    [ES] Verifica la sesión de Azure CLI; retorna el Object ID del usuario o finaliza con error.
    """
    # [EN] Query Microsoft Entra ID for the logged-in user's unique directory Object ID
    # [ES] Consulta a Microsoft Entra ID el Object ID único del usuario autenticado
    user_object_id = az_query(
        ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"]
    )
    if not user_object_id:
        print("Error: Not authenticated with Azure. Please run: az login")
        sys.exit(1)
    return user_object_id


def write_env_files(env_vars: dict[str, str], directory: str = ".") -> None:
    """
    [EN] Write .env (bash) and .env.ps1 (PowerShell) side by side for cross-shell loading.
         Generates UTF-8 without BOM and UNIX LF endings for universal compatibility.
    [ES] Escribe archivos .env (bash) y .env.ps1 (PowerShell) en paralelo para exportar variables.
         Genera codificación UTF-8 sin BOM y saltos LF para compatibilidad universal.
    """
    target_dir = Path(directory)
    target_dir.mkdir(parents=True, exist_ok=True)

    # [EN] Shell escape helpers for double-quoted values
    # [ES] Funciones de escape para valores entre comillas dobles en cada shell
    def bash_escape(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("$", "\\$")
            .replace("`", "\\`")
        )

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


def _derived_names(user_object_id: str) -> tuple[str, str, str]:
    """
    [EN] Compute unique, collision-free resource names using SHA-1 hash of user Object ID.
         Ensures globally unique DNS for ACR (*.azurecr.io) and App Service (*.azurewebsites.net).
    [ES] Calcula nombres únicos y libres de colisiones usando el hash SHA-1 del Object ID.
         Garantiza DNS global único para ACR (*.azurecr.io) y App Service (*.azurewebsites.net).
    """
    user_hash = hashlib.sha1(user_object_id.encode("utf-8")).hexdigest()[:8]
    return (
        f"acr{user_hash}",
        f"plan-docprocessor-{user_hash}",
        f"app-docprocessor-{user_hash}",
    )


def show_menu(acr_name: str, app_plan: str) -> None:
    """
    [EN] Display interactive terminal menu showing target deployment names and available phases.
    [ES] Muestra el menú interactivo en terminal con los nombres derivados y fases disponibles.
    """
    clear_screen()
    print("=====================================================================")
    print("    App Service Container Exercise - Deployment Script")
    print("=====================================================================")
    print(f"Resource Group: {rg}")
    print(f"Location: {location}")
    print(f"ACR Name: {acr_name}")
    print(f"App Service Plan: {app_plan}")
    print("=====================================================================")
    print("1. Create Azure Container Registry and build container image")
    print("2. Create App Service Plan")
    print("3. Check deployment status")
    print("4. Exit")
    print("=====================================================================")


def create_resource_group() -> bool:
    """
    [EN] Idempotently verify and create target Resource Group in specified region.
    [ES] Verifica y crea de forma idempotente el Grupo de Recursos en la región elegida.
    """
    print(f"Checking/creating resource group '{rg}'...")
    exists = az_query(["az", "group", "exists", "--name", rg])
    if exists == "false":
        if not run_quiet(
            "Create resource group",
            [
                "az", "group", "create",
                "--name", rg,
                "--location", location,
            ],
        ):
            return False
        print(f"Resource group created: {rg}")
    else:
        print(f"Resource group already exists: {rg}")
    return True


def create_acr_and_build_image(acr_name: str) -> bool:
    """
    [EN] Provision private Azure Container Registry (Basic SKU, Admin User disabled)
         and trigger cloud-native serverless container build via ACR Tasks.
    [ES] Aprovisiona el Azure Container Registry privado (SKU Basic, Admin User deshabilitado)
         y dispara la compilación serverless de la imagen de contenedor vía ACR Tasks.
    """
    print(f"Creating Azure Container Registry '{acr_name}'...")
    existing = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "name", "-o", "tsv"]
    )
    if not existing:
        # [EN] Create ACR with admin-enabled=false to enforce Zero-Trust Managed Identity authentication
        # [ES] Crea ACR con admin-enabled=false para forzar autenticación Zero-Trust con Managed Identity
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
    else:
        print(f"ACR already exists: {acr_name}")
    print(f"  Login server: {acr_name}.azurecr.io")

    print()
    print("Building and pushing container image to ACR...")
    print("This may take a few minutes...")

    # [EN] Serverless build via ACR Tasks: compresses api/ directory as tarball and builds remotely
    # [ES] Compilación serverless vía ACR Tasks: empaqueta api/ como tarball y compila en la nube
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


def create_app_service_plan(acr_name: str, app_plan: str, app_name: str) -> bool:
    """
    [EN] Provision dedicated Linux App Service Plan (SKU P0v3) for custom containers,
         then write environment variables to .env and .env.ps1 files.
    [ES] Aprovisiona el App Service Plan dedicado Linux (SKU P0v3) para contenedores personalizados,
         y exporta las variables de entorno a los archivos .env y .env.ps1.
    """
    print(f"Creating App Service Plan '{app_plan}'...")
    existing = az_query(
        ["az", "appservice", "plan", "show", "--resource-group", rg,
         "--name", app_plan, "--query", "name", "-o", "tsv"]
    )
    if not existing:
        # [EN] --is-linux: required for container hosting. --sku P0v3: entry-level dedicated Premium v3
        # [ES] --is-linux: obligatorio para contenedores. --sku P0v3: nivel dedicado de entrada Premium v3
        if not run_quiet(
            "Create App Service Plan",
            [
                "az", "appservice", "plan", "create",
                "--resource-group", rg,
                "--name", app_plan,
                "--location", location,
                "--sku", "P0v3",
                "--is-linux",
            ],
        ):
            return False
        print(f"App Service Plan created: {app_plan}")
        print("  SKU: P0v3 (Premium v3 tier)")
    else:
        print(f"App Service Plan already exists: {app_plan}")

    # [EN] Save resolved variables for student CLI exercises
    # [ES] Guarda las variables resueltas para las prácticas de consola del estudiante
    write_env_files({
        "RESOURCE_GROUP": rg,
        "ACR_NAME": acr_name,
        "APP_PLAN": app_plan,
        "APP_NAME": app_name,
        "LOCATION": location,
    })
    print()
    print("Environment variables saved to: .env and .env.ps1")
    print("Run 'source .env' (Bash) or '. .\\.env.ps1' (PowerShell) to load them.")
    return True


def check_deployment_status(acr_name: str, app_plan: str, app_name: str) -> bool:
    """
    [EN] Diagnostic probe: inspects provisioning status of ACR, container image,
         App Service Plan, Web App state, and Managed Identity configuration.
    [ES] Diagnóstico de despliegue: inspecciona estado de aprovisionamiento de ACR, imagen OCI,
         App Service Plan, estado de la Web App y configuración de Managed Identity.
    """
    print("Checking deployment status...")
    print()

    # [EN] 1. Inspect Azure Container Registry status and image repository
    # [ES] 1. Inspecciona estado del Azure Container Registry y repositorio de imágenes
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
                ["az", "acr", "repository", "show", "--name", acr_name,
                 "--image", CONTAINER_IMAGE, "--query", "name", "-o", "tsv"]
            )
            if image_exists:
                print(f"  Container image: {CONTAINER_IMAGE}")
            else:
                print("  Container image not found")
    else:
        print("  Status: Not created")

    print()
    # [EN] 2. Inspect App Service Plan state and compute SKU
    # [ES] 2. Inspecciona estado y SKU de cómputo del App Service Plan
    print(f"App Service Plan ({app_plan}):")
    plan_status = az_query(
        ["az", "appservice", "plan", "show", "--resource-group", rg,
         "--name", app_plan, "--query", "provisioningState", "-o", "tsv"]
    )
    if plan_status:
        print(f"  Status: {plan_status}")
        plan_sku = az_query(
            ["az", "appservice", "plan", "show", "--resource-group", rg,
              "--name", app_plan, "--query", "sku.name", "-o", "tsv"]
        )
        if plan_sku:
            print(f"  SKU: {plan_sku}")
        if plan_status == "Succeeded":
            print("  App Service Plan is ready")
    else:
        print("  Status: Not created")

    print()
    # [EN] 3. Inspect Web App container state and Managed Identity
    # [ES] 3. Inspecciona estado del contenedor Web App e Identidad Administrada
    print(f"Web App ({app_name}):")
    app_state = az_query(
        ["az", "webapp", "show", "--resource-group", rg, "--name", app_name,
         "--query", "state", "-o", "tsv"]
    )
    if app_state:
        print(f"  State: {app_state}")
        print(f"  URL: https://{app_name}.azurewebsites.net")

        principal_id = az_query(
            ["az", "webapp", "identity", "show", "--resource-group", rg,
             "--name", app_name, "--query", "principalId", "-o", "tsv"]
        )
        if principal_id:
            print("  Managed identity configured")
        else:
            print("  Managed identity: Not configured")
    else:
        print("  Status: Not created (student task)")

    print()
    print("=====================================================================")
    print("Environment Variables (.env and .env.ps1 files):")
    print(f"  RESOURCE_GROUP={rg}")
    print(f"  ACR_NAME={acr_name}")
    print(f"  APP_PLAN={app_plan}")
    print(f"  APP_NAME={app_name}")
    print(f"  LOCATION={location}")
    print("=====================================================================")
    return True


def _preflight() -> None:
    """
    [EN] Preflight checks: ensure api/Dockerfile exists and anchor cwd to script folder.
    [ES] Comprobaciones previas: asegura existencia de api/Dockerfile y fija cwd en la carpeta del script.
    """
    script_dir = Path(__file__).resolve().parent
    dockerfile = script_dir / "api" / "Dockerfile"
    if not dockerfile.is_file():
        print("Error: 'api/Dockerfile' is missing next to azdeploy.py. "
              "Make sure you kept the exercise folder intact.")
        sys.exit(1)
    os.chdir(script_dir)


def main() -> None:
    """
    [EN] Main interactive entrypoint: orchestrates preflight, login verification,
         name derivation, and presents options menu to user.
    [ES] Punto de entrada interactivo principal: orquestación de preflight, verificación de login,
         derivación de nombres y despliegue del menú de opciones al usuario.
    """
    _preflight()
    user_object_id = require_az_login()
    acr_name, app_plan, app_name = _derived_names(user_object_id)

    while True:
        show_menu(acr_name, app_plan)
        choice = input("Please select an option (1-4): ").strip()

        if choice in {"1", "2", "3", "4"}:
            clear_screen()

        if choice == "1":
            print()
            if create_resource_group():
                print()
                create_acr_and_build_image(acr_name)
            print()
            pause()
        elif choice == "2":
            print()
            if create_resource_group():
                print()
                create_app_service_plan(acr_name, app_plan, app_name)
            print()
            pause()
        elif choice == "3":
            print()
            check_deployment_status(acr_name, app_plan, app_name)
            print()
            pause()
        elif choice == "4":
            print("Exiting...")
            clear_screen()
            sys.exit(0)
        else:
            print("Invalid option. Please select 1-4.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
