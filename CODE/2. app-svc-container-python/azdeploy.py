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

# [EN] Pricing tier / compute SKU for App Service Plan.
#      Available tiers for custom Linux containers:
#      - Basic (B1, B2, B3):
#          Development / testing. Dedicated virtual machine, manual scale (1-3 instances),
#          custom domain and SSL support. No auto-scale, no deployment slots, no VNet integration.
#          B1 spec: 1 vCPU, 1.75 GB RAM (most economical dedicated tier).
#      - Standard (S1, S2, S3):
#          General production workloads. Auto-scale (up to 10 instances), 5 deployment slots,
#          daily backups, 99.95% SLA, and virtual network (VNet) integration.
#          S1 spec: 1 vCPU, 1.75 GB RAM.
#      - Premium v3 (P0v3, P1v3, P2v3, P3v3):
#          High-performance production & enterprise AI workloads. Faster Hyper-V CPUs,
#          higher memory-to-vCPU ratio, auto-scale (up to 30 instances), 20 deployment slots,
#          VNet integration, and Zone Redundancy.
#          P0v3 spec: 1 vCPU, 4.0 GB RAM (recommended entry-level tier for this lab).
#      - Isolated v2 (I1v2, I2v2, I3v2, etc.):
#          Mission-critical workloads requiring strict regulatory compliance.
#          Runs inside a dedicated Azure App Service Environment (ASE v3) with full network isolation,
#          private hypervisors, and scaling up to 100 instances.
#      * Note: Free (F1) and Shared (D1) tiers run on multi-tenant shared infrastructure
#              and DO NOT support custom Linux containers.
# [ES] Nivel de precios / SKU de cómputo para el App Service Plan.
#      Niveles disponibles para contenedores Linux personalizados:
#      - Basic (B1, B2, B3):
#          Desarrollo y pruebas. Máquinas virtuales dedicadas, escalado manual (1-3 instancias),
#          soporte de dominio personalizado y SSL. Sin auto-escalado ni slots ni integración VNet.
#          Especificación B1: 1 vCPU, 1.75 GB RAM (el más económico en nivel dedicado).
#      - Standard (S1, S2, S3):
#          Cargas de producción general. Escalado automático (hasta 10 instancias), 5 slots de
#          despliegue, copias de seguridad diarias, SLA 99.95% e integración con red virtual (VNet).
#          Especificación S1: 1 vCPU, 1.75 GB RAM.
#      - Premium v3 (P0v3, P1v3, P2v3, P3v3):
#          Alto rendimiento para producción empresarial y servicios de IA. Procesadores más rápidos,
#          mayor proporción memoria/vCPU, auto-escalado (hasta 30 instancias), 20 slots de despliegue,
#          integración VNet y redundancia de zona.
#          Especificación P0v3: 1 vCPU, 4.0 GB RAM (nivel recomendado por defecto para este laboratorio).
#      - Isolated v2 (I1v2, I2v2, I3v2, etc.):
#          Cargas críticas bajo estricto cumplimiento regulatorio.
#          Se ejecuta en un App Service Environment dedicado (ASE v3) con aislamiento total de red,
#          hipervisores privados y escalado hasta 100 instancias.
#      * Nota: Los niveles Free (F1) y Shared (D1) corren en infraestructura compartida multi-tenant
#              y NO admiten contenedores Linux personalizados.
sku = "P0v3"

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

    # [EN] 2. Search executable across system PATH directories (equivalent to 'which' in Linux/macOS or 'where' in Windows)
    # [ES] 2. Busca el archivo ejecutable en los directorios del PATH del sistema (equivalente a 'which' en Linux/macOS)
    resolved = shutil.which(name)

    # [EN] 3. If not found, display descriptive error and abort with exit code 1
    # [ES] 3. Si no existe en el sistema, imprime error descriptivo y aborta con código 1
    if not resolved:
        print(f"Error: '{name}' not found on PATH. Install it and retry.")
        sys.exit(1)

    # [EN] 4. Store resolved executable path in cache dictionary and return it
    # [ES] 4. Almacena la ruta resuelta en la caché para llamadas subsecuentes y la retorna
    _EXE_CACHE[name] = resolved
    return resolved


def run_quiet(description: str, argv: list[str]) -> bool:
    """
    [EN] Run a command, capture output, print error on failure, and return success bool.
    [ES] Ejecuta un comando, captura la salida, imprime error si falla y retorna booleano de éxito.
    """
    # [EN] Replace binary name with its resolved absolute executable path and unpack arguments with '*'
    # [ES] Reemplaza el comando inicial por su ruta absoluta resuelta y desempaqueta argumentos con '*'
    argv = [_resolve_exe(argv[0]), *argv[1:]]

    # [EN] subprocess.run executes command as child process:
    #      capture_output=True: silences terminal output, capturing stdout and stderr into memory.
    #      text=True: decodes byte streams automatically into Python string objects.
    #      check=False: prevents raising unhandled CalledProcessError exceptions on non-zero exit codes.
    # [ES] subprocess.run ejecuta el comando en un subproceso del sistema:
    #      capture_output=True: silencia la consola capturando stdout y stderr en memoria.
    #      text=True: decodifica automáticamente los bytes de salida a strings de Python.
    #      check=False: evita que Python lance excepciones abruptas ante códigos de salida no cero.
    result = subprocess.run(argv, capture_output=True, text=True, check=False)

    # [EN] Exit code 0 means success. Any non-zero code represents an error.
    # [ES] En sistemas operativos, el código 0 indica éxito. Cualquier valor diferente es error.
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        # [EN] Combine and strip stdout/stderr to display the root cause of the error
        # [ES] Concatena y limpia los mensajes de salida y error para mostrar la causa raíz al usuario
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
    # [EN] Replace command name with resolved absolute path.
    # [ES] Reemplaza el nombre del comando por su ruta absoluta resuelta.
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)

    # [EN] If the CLI call failed, return an empty string to indicate failure or absence.
    # [ES] Si la llamada a la CLI falló, retorna una cadena vacía para indicar ausencia o fallo.
    if result.returncode != 0:
        return ""

    # [EN] .strip() removes leading and trailing whitespace and newline characters (\n, \r).
    # [ES] .strip() elimina espacios en blanco y saltos de línea sobrantes al inicio y final.
    return (result.stdout or "").strip()


def clear_screen() -> None:
    """
    [EN] Clear terminal display across bash, zsh, PowerShell, cmd, and Git Bash.
    [ES] Limpia la pantalla de la terminal en bash, zsh, PowerShell, cmd y Git Bash.
    """
    # [EN] Detect operating system: 'cls' on Windows (NT), 'clear' on POSIX systems (Linux, macOS)
    # [ES] Detecta el sistema operativo: 'cls' en Windows (NT), 'clear' en POSIX (Linux, macOS)
    cmd = "cls" if os.name == "nt" else "clear"
    if os.system(cmd) != 0:
        # [EN] Fallback ANSI escape sequences: \x1b[2J clears display, \x1b[3J clears buffer, \x1b[H resets cursor
        # [ES] Secuencia de escape ANSI de respaldo: \x1b[2J limpia pantalla, \x1b[3J búfer, \x1b[H reposiciona cursor
        sys.stdout.write("\x1b[2J\x1b[3J\x1b[H")
        sys.stdout.flush()


def pause(prompt: str = "Press Enter to continue...") -> None:
    """
    [EN] Block execution until user presses Enter (handles EOF safely).
    [ES] Pausa la ejecución hasta presionar Enter (gestiona fin de archivo EOF).
    """
    try:
        # [EN] Wait for user keystroke in terminal input
        # [ES] Espera la pulsación de tecla del usuario en la consola
        input(prompt)
    except EOFError:
        # [EN] Handle EOF gracefully (when script is piped or executed in automated environments)
        # [ES] Captura fin de archivo EOF con gracia (redirecciones o entornos de ejecución desatendidos)
        print()


def require_az_login() -> str:
    """
    [EN] Verify Azure CLI session; return signed-in user's Object ID or exit with error.
    [ES] Verifica la sesión de Azure CLI; retorna el Object ID del usuario o finaliza con error.
    """
    # [EN] Query Microsoft Entra ID (Azure AD) for the currently logged-in user unique Object ID
    # [ES] Consulta a Microsoft Entra ID (Azure AD) el identificador único (Object ID) del usuario conectado
    user_object_id = az_query(
        ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"]
    )

    # [EN] If user_object_id is empty, user is not authenticated: display error and abort
    # [ES] Si la cadena está vacía, el usuario no tiene una sesión activa: muestra error y aborta
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
    # [EN] Path() represents a filesystem path in an OS-independent way.
    # [ES] Path() abstrae rutas de disco de forma multiplataforma (Windows/Linux/macOS).
    target_dir = Path(directory)

    # [EN] mkdir(parents=True, exist_ok=True) creates folder tree safely without failing if it already exists.
    # [ES] mkdir(parents=True, exist_ok=True) crea directorios padres si no existen y no falla si ya existen.
    target_dir.mkdir(parents=True, exist_ok=True)

    # [EN] Helper: escape special characters for Bash double-quoted strings.
    # [ES] Función auxiliar: escapa caracteres reservados en cadenas entre comillas dobles de Bash.
    def bash_escape(value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("$", "\\$")
            .replace("`", "\\`")
        )

    # [EN] Helper: escape special characters for PowerShell strings (using backticks).
    # [ES] Función auxiliar: escapa caracteres para PowerShell (utilizando acentos graves `).
    def ps_escape(value: str) -> str:
        return (
            value.replace("`", "``")
            .replace('"', '`"')
            .replace("$", "`$")
        )

    # [EN] List comprehensions to format export lines for Bash and environment variables for PowerShell.
    # [ES] Comprensión de listas para formatear comandos 'export' (Bash) y '$env:' (PowerShell).
    bash_lines = [f'export {k}="{bash_escape(v)}"\n' for k, v in env_vars.items()]
    ps_lines = [f'$env:{k} = "{ps_escape(v)}"\n' for k, v in env_vars.items()]

    # [EN] 'with open(...) as f' context manager automatically closes the file even if exceptions occur.
    #      newline="\n": guarantees UNIX LF line endings across all platforms.
    # [ES] El bloque 'with open(...) as f' asegura el cierre automático del archivo ante cualquier error.
    #      newline="\n": garantiza saltos de línea LF (Unix) válidos en cualquier sistema operativo.
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
    # [EN] 1. .encode("utf-8") converts string to raw bytes required by hashlib.
    #      2. hashlib.sha1() calculates a 160-bit cryptographic hash.
    #      3. .hexdigest() converts the hash into a 40-character hexadecimal string.
    #      4. [:8] slices the first 8 characters to produce a short unique alphanumeric string.
    # [ES] 1. .encode("utf-8") convierte el texto a bytes, requerido por las funciones hash.
    #      2. hashlib.sha1() calcula el hash criptográfico SHA-1 de 160 bits.
    #      3. .hexdigest() convierte el resumen a una cadena hexadecimal legible.
    #      4. [:8] toma los primeros 8 caracteres para generar un identificador único y corto.
    user_hash = hashlib.sha1(user_object_id.encode("utf-8")).hexdigest()[:8]

    # [EN] Return deterministic unique names for ACR, App Service Plan, and Web App
    # [ES] Retorna nombres únicos y deterministas para ACR, App Service Plan y Web App
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
    # [EN] 1. Clear terminal to present a clean menu state
    # [ES] 1. Limpia la terminal para presentar un estado limpio del menú
    clear_screen()

    # [EN] 2. Display configuration banner with target resource identifiers
    # [ES] 2. Muestra banner de configuración con los identificadores de recursos objetivo
    print("=====================================================================")
    print("    App Service Container Exercise - Deployment Script")
    print("=====================================================================")
    print(f"Resource Group: {rg}")
    print(f"Location: {location}")
    print(f"SKU: {sku}")
    print(f"ACR Name: {acr_name}")
    print(f"App Service Plan: {app_plan}")
    print("=====================================================================")
    # [EN] 3. Display available deployment options
    # [ES] 3. Muestra las opciones de despliegue disponibles
    print("1. Create Azure Container Registry and build container image")
    print("2. Create App Service Plan")
    print("3. Check deployment status")
    print("4. Exit")
    print("=====================================================================")


def create_resource_group() -> bool:
    """
    [EN] Verify if Resource Group exists; create it if absent (idempotent operation).
    [ES] Verifica si el Grupo de Recursos existe; lo crea si no existe (operación idempotente).
    """
    print(f"Checking/creating resource group '{rg}'...")

    # [EN] Idempotency: probe Azure first to check if the group already exists.
    # [ES] Idempotencia: comprueba en Azure si el grupo de recursos ya existe para no duplicar trabajo.
    exists = az_query(["az", "group", "exists", "--name", rg])
    if exists == "false":
        # [EN] Execute 'az group create --name <rg> --location <location>'.
        # [ES] Ejecuta la creación del grupo de recursos en la región seleccionada.
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
        # [EN] Resource group already exists; skip redundant creation
        # [ES] El grupo de recursos ya existe; se omite la creación redundante
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

    # [EN] 1. Idempotency probe: check if ACR already exists before attempting creation
    # [ES] 1. Verificación de idempotencia: comprueba si el ACR ya existe antes de crearlo
    existing = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "name", "-o", "tsv"]
    )
    if not existing:
        # [EN] Create ACR with admin-enabled=false to enforce Zero-Trust Managed Identity authentication.
        #      Uses cost-effective Basic SKU for lab and development environments.
        # [ES] Crea ACR con admin-enabled=false para forzar autenticación Zero-Trust con Managed Identity.
        #      Utiliza el SKU Basic optimizado para costos de laboratorios y desarrollo.
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
        # [EN] Registry already exists; skip creation
        # [ES] El registro ya existe; omite la creación
        print(f"ACR already exists: {acr_name}")
    print(f"  Login server: {acr_name}.azurecr.io")

    print()
    print("Building and pushing container image to ACR...")
    print("This may take a few minutes...")

    # [EN] 2. Serverless build via ACR Tasks: compresses api/ directory as tarball and builds remotely.
    #      Eliminates local Docker daemon requirement and uploads container image directly into ACR.
    # [ES] 2. Compilación serverless vía ACR Tasks: empaqueta api/ como tarball y compila en la nube.
    #      Elimina la necesidad de Docker local y sube la imagen empaquetada directamente a ACR.
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
    [EN] Provision dedicated Linux App Service Plan for custom containers,
         then write environment variables to .env and .env.ps1 files.
    [ES] Aprovisiona el App Service Plan dedicado Linux para contenedores personalizados,
         y exporta las variables de entorno a los archivos .env y .env.ps1.
    """
    print(f"Creating App Service Plan '{app_plan}'...")

    # [EN] 1. Check if App Service Plan already exists in target resource group
    # [ES] 1. Comprueba si el App Service Plan ya existe en el grupo de recursos destino
    existing = az_query(
        ["az", "appservice", "plan", "show", "--resource-group", rg,
         "--name", app_plan, "--query", "name", "-o", "tsv"]
    )
    if not existing:
        # [EN] Execute 'az appservice plan create':
        #      --is-linux: mandatory for hosting Linux containers in Azure App Service.
        #      --sku: compute tier configured by user (e.g., B1, P0v3).
        # [ES] Ejecuta 'az appservice plan create':
        #      --is-linux: obligatorio para hospedar contenedores Linux en Azure App Service.
        #      --sku: nivel de cómputo configurado por el usuario (ej. B1, P0v3).
        if not run_quiet(
            "Create App Service Plan",
            [
                "az", "appservice", "plan", "create",
                "--resource-group", rg,
                "--name", app_plan,
                "--location", location,
                "--sku", sku,
                "--is-linux",
            ],
        ):
            return False
        print(f"App Service Plan created: {app_plan}")
        print(f"  SKU: {sku}")
    else:
        # [EN] Plan already exists; reuse existing compute plan
        # [ES] El plan ya existe; se reutiliza el plan de cómputo existente
        print(f"App Service Plan already exists: {app_plan}")

    # [EN] 2. Save resolved variables for student CLI exercises (.env and .env.ps1)
    # [ES] 2. Guarda las variables resueltas para las prácticas de consola del estudiante (.env y .env.ps1)
    write_env_files({
        "RESOURCE_GROUP": rg,
        "ACR_NAME": acr_name,
        "APP_PLAN": app_plan,
        "APP_NAME": app_name,
        "LOCATION": location,
        "SKU": sku,
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
    # [EN] Query ACR provisioning state ('Succeeded' indicates registry is ready for push/pull)
    # [ES] Consulta el estado de aprovisionamiento del ACR ('Succeeded' indica listo para push/pull)
    acr_status = az_query(
        ["az", "acr", "show", "--resource-group", rg, "--name", acr_name,
         "--query", "provisioningState", "-o", "tsv"]
    )
    if acr_status:
        print(f"  Status: {acr_status}")
        if acr_status == "Succeeded":
            print("  ACR is ready")
            # [EN] Verify if container image exists inside the registry catalog
            # [ES] Verifica si la imagen de contenedor existe en el catálogo del registro
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
    # [EN] Probe App Service Plan provisioning status
    # [ES] Consulta el estado de aprovisionamiento del App Service Plan
    plan_status = az_query(
        ["az", "appservice", "plan", "show", "--resource-group", rg,
         "--name", app_plan, "--query", "provisioningState", "-o", "tsv"]
    )
    if plan_status:
        print(f"  Status: {plan_status}")
        # [EN] Query pricing tier and SKU size assigned to the plan (e.g., P0v3)
        # [ES] Consulta el nivel de precios y tamaño SKU asignado al plan (ej. P0v3)
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
    # [EN] Query runtime state of the Web App (e.g., 'Running' or empty if not yet deployed)
    # [ES] Consulta el estado de ejecución de la Web App (ej. 'Running' o vacío si aún no se crea)
    app_state = az_query(
        ["az", "webapp", "show", "--resource-group", rg, "--name", app_name,
         "--query", "state", "-o", "tsv"]
    )
    if app_state:
        print(f"  State: {app_state}")
        print(f"  URL: https://{app_name}.azurewebsites.net")

        # [EN] Check if System-Assigned Managed Identity is configured for AcrPull RBAC
        # [ES] Verifica si la Identidad Administrada Asignada por el Sistema está configurada para AcrPull
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
    # [EN] 4. Print current environment variable assignments
    # [ES] 4. Imprime las variables de entorno activas guardadas en disco
    print("=====================================================================")
    print("Environment Variables (.env and .env.ps1 files):")
    print(f"  RESOURCE_GROUP={rg}")
    print(f"  ACR_NAME={acr_name}")
    print(f"  APP_PLAN={app_plan}")
    print(f"  APP_NAME={app_name}")
    print(f"  LOCATION={location}")
    print(f"  SKU={sku}")
    print("=====================================================================")
    return True


def _preflight() -> None:
    """
    [EN] Preflight checks: ensure api/Dockerfile exists and anchor cwd to script folder.
    [ES] Comprobaciones previas: asegura existencia de api/Dockerfile y fija cwd en la carpeta del script.
    """
    # [EN] __file__ is the current script path. .resolve() resolves symlinks. .parent gets folder path.
    # [ES] __file__ es la ruta del script actual. .resolve() resuelve enlaces. .parent obtiene su carpeta.
    script_dir = Path(__file__).resolve().parent

    # [EN] Path / operator joins path segments cleanly across all operating systems.
    # [ES] El operador '/' de Path concatena carpetas de forma segura según el sistema operativo.
    dockerfile = script_dir / "api" / "Dockerfile"

    # [EN] .is_file() checks whether the target file actually exists on the filesystem.
    # [ES] .is_file() verifica si el archivo Dockerfile existe físicamente en el disco.
    if not dockerfile.is_file():
        print("Error: 'api/Dockerfile' is missing next to azdeploy.py. "
              "Make sure you kept the exercise folder intact.")
        sys.exit(1)

    # [EN] os.chdir() changes the current working directory (cwd) of the Python process.
    # [ES] os.chdir() cambia el directorio de trabajo activo del proceso hacia la carpeta del script.
    os.chdir(script_dir)


def main() -> None:
    """
    [EN] Main interactive entrypoint: orchestrates preflight, login verification,
         name derivation, and presents options menu to user.
    [ES] Punto de entrada interactivo principal: orquestación de preflight, verificación de login,
         derivación de nombres y despliegue del menú de opciones al usuario.
    """
    # [EN] Step 1: Preflight validation
    # [ES] Paso 1: Verificación de entorno
    _preflight()

    # [EN] Step 2: Validate authenticated Azure CLI session
    # [ES] Paso 2: Validar sesión autenticada en Azure CLI
    user_object_id = require_az_login()

    # [EN] Step 3: Compute unique DNS-compliant resource names
    # [ES] Paso 3: Calcular nombres únicos de recursos compatibles con DNS
    acr_name, app_plan, app_name = _derived_names(user_object_id)

    # [EN] Step 4: Interactive menu loop for deployment operations
    # [ES] Paso 4: Bucle interactivo de menú para operaciones de despliegue
    while True:
        show_menu(acr_name, app_plan)
        choice = input("Please select an option (1-4): ").strip()

        if choice in {"1", "2", "3", "4"}:
            clear_screen()

        # [EN] Option 1: Provision ACR and build container image via ACR Tasks
        # [ES] Opción 1: Aprovisionar ACR y compilar imagen de contenedor vía ACR Tasks
        if choice == "1":
            print()
            if create_resource_group():
                print()
                create_acr_and_build_image(acr_name)
            print()
            pause()
        # [EN] Option 2: Provision Linux App Service Plan and export environment files
        # [ES] Opción 2: Aprovisionar App Service Plan Linux y exportar archivos de entorno
        elif choice == "2":
            print()
            if create_resource_group():
                print()
                create_app_service_plan(acr_name, app_plan, app_name)
            print()
            pause()
        # [EN] Option 3: Check provisioning status of all resources and Managed Identity
        # [ES] Opción 3: Verificar estado de aprovisionamiento de recursos e Identidad Administrada
        elif choice == "3":
            print()
            check_deployment_status(acr_name, app_plan, app_name)
            print()
            pause()
        # [EN] Option 4: Clean exit
        # [ES] Opción 4: Salida limpia
        elif choice == "4":
            print("Exiting...")
            clear_screen()
            sys.exit(0)
        else:
            print("Invalid option. Please select 1-4.")
            pause()


# [EN] Standard Python idiom: executes main() only when script is run directly, not when imported.
# [ES] Idioma estándar de Python: ejecuta main() solo cuando el script se corre directamente, no al importarse.
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # [EN] Handles Ctrl+C cleanly without showing an ugly Python traceback.
        # [ES] Captura Ctrl+C de forma limpia sin imprimir trazas de error (traceback) en la terminal.
        print()
        sys.exit(130)
