# =============================================================================
# [EN] User Configuration - Change the values of these variables as needed.
# [ES] Configuración de Usuario - Modifique los valores de estas variables según sea necesario.
# =============================================================================

# [EN] Resource Group name
# [ES] Nombre del Grupo de Recursos
rg = "<your-resource-group-name>"

# [EN] Azure region for resources
# [ES] Región de Azure para los recursos
location = "<your-azure-region>"

# =============================================================================
# [EN] AUTOMATION ENGINE - Core Python logic and Azure CLI wrapper.
# [ES] MOTOR DE AUTOMATIZACIÓN - Lógica interna de Python y llamadas a Azure CLI.
# =============================================================================

# [EN] Used to generate cryptographic hashes (SHA-1)
# [ES] Módulo para generar hashes criptográficos (SHA-1)
import hashlib

# [EN] Access OS environment and working directory
# [ES] Acceso a variables de entorno y directorio del SO
import os

# [EN] High-level file/path operations (which)
# [ES] Operaciones de rutas y ejecutables en PATH (which)
import shutil

# [EN] Spawns external system processes (Azure CLI)
# [ES] Ejecución de subprocesos externos del sistema (Azure CLI)
import subprocess

# [EN] System parameters and interpreter exit
# [ES] Parámetros del intérprete y control de salida (sys.exit)
import sys

# [EN] Modern object-oriented filesystem paths
# [ES] Manejo orientado a objetos de rutas de archivos
from pathlib import Path

# -----------------------------------------------------------------------------
# [EN] Environment Tuning
# [ES] Ajuste del Entorno de Ejecución
# -----------------------------------------------------------------------------
# [EN] Set environment variable so Azure CLI only outputs errors, hiding deprecation notices.
# [ES] Configura la variable de entorno para que Azure CLI solo imprima errores, ocultando avisos de preview.
os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")

# [EN] Global dictionary acting as an in-memory cache to store resolved executable paths.
# [ES] Diccionario global en memoria para guardar las rutas de binarios ya resueltos y no buscar dos veces.
_EXE_CACHE: dict[str, str] = {}


def _resolve_exe(name: str) -> str:
    """
    [EN] Locate an executable on PATH (handles az.cmd on Windows).
    [ES] Localiza un ejecutable en el PATH del sistema (soporta az.cmd en Windows).
    """
    # [EN] 1. Check if the path was already resolved previously in the cache dictionary.
    # [ES] 1. Revisa si la ruta del comando ya fue resuelta antes en el diccionario de caché.
    cached = _EXE_CACHE.get(name)
    if cached:
        return cached

    # [EN] 2. shutil.which() looks for the executable in the system PATH (equivalent to 'which' in Linux/macOS).
    # [ES] 2. shutil.which() busca el archivo ejecutable en el PATH (equivalente a 'which' en Linux o 'where' en Windows).
    resolved = shutil.which(name)

    # [EN] 3. If not found, print a descriptive error and stop the program with exit code 1.
    # [ES] 3. Si no existe en el sistema, imprime un error claro y detiene el script con código de error 1.
    if not resolved:
        print(f"Error: '{name}' not found on PATH. Install it and retry.")
        sys.exit(1)

    # [EN] 4. Store the resolved path in the cache and return it.
    # [ES] 4. Almacena la ruta absoluta en la caché para futuras llamadas y la retorna.
    _EXE_CACHE[name] = resolved
    return resolved


def run_quiet(description: str, argv: list[str]) -> bool:
    """
    [EN] Run a command, print an error on failure, return success as bool.
    [ES] Ejecuta un comando en silencio, imprime el error si falla y retorna el resultado como booleano.
    """
    # [EN] Replace command name with resolved absolute path, unpacking remaining args with '*'.
    # [ES] Reemplaza el comando inicial por su ruta absoluta y desempaqueta los argumentos restantes con '*'.
    argv = [_resolve_exe(argv[0]), *argv[1:]]

    # [EN] subprocess.run executes the command as a child process.
    #      capture_output=True: silences console by capturing stdout and stderr.
    #      text=True: decodes byte output into Python strings automatically.
    #      check=False: prevents raising an unhandled Python exception on failure.
    # [ES] subprocess.run ejecuta el comando en un subproceso del sistema operativo.
    #      capture_output=True: silencia la pantalla capturando la salida estándar y de errores.
    #      text=True: decodifica automáticamente los bytes de salida a texto (strings de Python).
    #      check=False: evita que Python lance una excepción abrupta si el comando falla.
    result = subprocess.run(argv, capture_output=True, text=True, check=False)

    # [EN] Exit code 0 means success. Any non-zero code represents an error.
    # [ES] En sistemas operativos, el código 0 indica éxito. Cualquier valor diferente es error.
    if result.returncode != 0:
        print(f"Error: {description} failed (exit code {result.returncode}).")
        # [EN] Combine and strip stdout/stderr to display the root cause of the error.
        # [ES] Concatena y limpia los mensajes de salida y error para mostrar la causa raíz al usuario.
        combined = (result.stdout or "") + (result.stderr or "")
        if combined.strip():
            print(combined.rstrip())
        return False
    return True


def az_query(argv: list[str]) -> str:
    """
    [EN] Run an `az ... -o tsv` probe and return stripped stdout (or empty).
    [ES] Ejecuta una consulta `az ... -o tsv` y retorna la salida estándar limpia (o cadena vacía).
    """
    argv = [_resolve_exe(argv[0]), *argv[1:]]
    result = subprocess.run(argv, capture_output=True, text=True, check=False)

    # [EN] If the CLI call failed, return an empty string to indicate failure or absence.
    # [ES] Si la llamada a la CLI falló, retorna una cadena vacía para indicar ausencia o fallo.
    if result.returncode != 0:
        return ""

    # [EN] .strip() removes leading and trailing whitespace and newline characters (\n, \r).
    # [ES] .strip() elimina espacios en blanco y saltos de línea sobrantes al inicio y final.
    return (result.stdout or "").strip()


def require_az_login() -> str:
    """
    [EN] Return the signed-in user's object id, or exit if not logged in.
    [ES] Retorna el Object ID del usuario autenticado en Azure CLI, o finaliza con error si no hay sesión.
    """
    # [EN] Queries Microsoft Entra ID (Azure AD) for the currently logged-in user object ID.
    # [ES] Consulta a Microsoft Entra ID (Azure AD) el identificador único (Object ID) del usuario conectado.
    user_object_id = az_query(
        ["az", "ad", "signed-in-user", "show", "--query", "id", "-o", "tsv"]
    )

    # [EN] If user_object_id is empty, the user has not executed 'az login'.
    # [ES] Si la cadena está vacía, significa que el usuario no tiene una sesión activa iniciada.
    if not user_object_id:
        print("Error: Not authenticated with Azure. Please run: az login")
        sys.exit(1)
    return user_object_id


def write_env_files(env_vars: dict[str, str], directory: str = ".") -> None:
    """
    [EN] Write .env (bash) and .env.ps1 (PowerShell) side by side.
         Writes UTF-8 without BOM and LF line endings so both bash `source` and
         PowerShell dot-source read them correctly on every supported shell.
    [ES] Escribe los archivos .env (Bash) y .env.ps1 (PowerShell) en paralelo.
         Genera codificación UTF-8 sin BOM y saltos LF para compatibilidad universal
         con `source` en Linux/macOS y dot-sourcing en PowerShell.
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


def _derived_names(user_object_id: str) -> str:
    """
    [EN] Derive a globally unique alphanumeric ACR name from user's Azure AD Object ID (SHA-1 hash).
    [ES] Deriva un nombre de ACR alfanumérico globalmente único usando el hash SHA-1 del Object ID de Azure AD.
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
    return f"acr{user_hash}"


def print_banner(acr_name: str) -> None:
    """
    [EN] Print configuration banner to the terminal before execution.
    [ES] Imprime el banner de configuración en la terminal antes de iniciar el despliegue.
    """
    print("=====================================================================")
    print("    Azure Container Registry Exercise - Deployment Script")
    print("=====================================================================")
    print(f"Resource Group: {rg}")
    print(f"Location: {location}")
    print(f"ACR Name: {acr_name}")
    print("=====================================================================")
    print()


def create_resource_group() -> bool:
    """
    [EN] Verify if Resource Group exists; create it if absent (idempotent operation).
    [ES] Verifica si el Grupo de Recursos existe; lo crea si no existe (operación idempotente).
    """
    print(f"Creating resource group '{rg}'...")

    # [EN] Idempotency: probe Azure first to check if the group already exists.
    # [ES] Idempotencia: comprueba en Azure si el grupo de recursos ya existe para no duplicar trabajo.
    exists = az_query(["az", "group", "exists", "--name", rg])
    if exists == "true":
        print(f"Resource group already exists: {rg}")
    else:
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
    return True


def create_acr(acr_name: str) -> bool:
    """
    [EN] Provision Azure Container Registry using the cost-effective Basic SKU.
    [ES] Aprovisiona el Azure Container Registry utilizando el SKU Basic optimizado para costos.
    """
    print(f"Creating Azure Container Registry '{acr_name}'...")

    # [EN] Execute 'az acr create --resource-group <rg> --name <acr_name> --sku Basic'.
    # [ES] Ejecuta la creación del registro OCI privado bajo el SKU básico de menor costo.
    if not run_quiet(
        "Create Azure Container Registry",
        [
            "az", "acr", "create",
            "--resource-group", rg,
            "--name", acr_name,
            "--sku", "Basic",
        ],
    ):
        return False
    print(f"ACR created: {acr_name}")
    print(f"  Login server: {acr_name}.azurecr.io")
    return True


def _preflight() -> None:
    """
    [EN] Preflight checks: ensure api/Dockerfile exists and anchor cwd to the script folder.
    [ES] Comprobaciones previas: asegura que api/Dockerfile exista y fija el cwd en la carpeta del script.
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
    [EN] Main deployment orchestrator:
         1. Preflight validation
         2. Authenticate & retrieve Azure identity
         3. Derive unique registry name
         4. Idempotently create Resource Group
         5. Aprovision ACR (Basic SKU)
         6. Export .env and .env.ps1 configuration files
    [ES] Orquestador principal de despliegue:
         1. Validación previa de archivos requeridos
         2. Autenticación y obtención de identidad en Azure
         3. Derivación de nombre único para el registro
         4. Creación idempotente del Grupo de Recursos
         5. Aprovisionamiento de ACR (SKU Basic)
         6. Exportación de archivos de variables .env y .env.ps1
    """
    # [EN] Step 1: Preflight check
    # [ES] Paso 1: Verificación de entorno
    _preflight()

    # [EN] Step 2: Ensure authenticated session
    # [ES] Paso 2: Validar sesión autenticada
    user_object_id = require_az_login()

    # [EN] Step 3: Compute unique DNS-compliant name
    # [ES] Paso 3: Calcular nombre único para DNS global
    acr_name = _derived_names(user_object_id)

    # [EN] Step 4: Display banner
    # [ES] Paso 4: Mostrar resumen de configuración
    print_banner(acr_name)

    # [EN] Step 5: Provision Resource Group
    # [ES] Paso 5: Aprovisionar Grupo de Recursos
    if not create_resource_group():
        sys.exit(1)
    print()

    # [EN] Step 6: Provision Azure Container Registry
    # [ES] Paso 6: Aprovisionar Azure Container Registry
    if not create_acr(acr_name):
        sys.exit(1)
    print()

    # [EN] Step 7: Export environment variables (.env / .env.ps1)
    # [ES] Paso 7: Exportar variables de entorno (.env / .env.ps1)
    write_env_files({
        "RESOURCE_GROUP": rg,
        "ACR_NAME": acr_name,
        "LOCATION": location,
    })

    print("=====================================================================")
    print("  Deployment Complete!")
    print("=====================================================================")
    print()
    print("Environment variables have been saved to: .env and .env.ps1")
    print()
    print(f"  RESOURCE_GROUP={rg}")
    print(f"  ACR_NAME={acr_name}")
    print(f"  LOCATION={location}")
    print()
    print("=====================================================================")


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
