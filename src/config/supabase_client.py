import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno del archivo .env
# Si estamos ejecutándonos desde AppData (empaquetados por Flet), buscamos el .env al lado del ejecutable .exe
if "AppData" in os.path.abspath(__file__):
    executable_dir = os.path.dirname(sys.executable)
    dotenv_path = os.path.join(executable_dir, ".env")
    load_dotenv(dotenv_path)
else:
    # En desarrollo local
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_client: Client = None
_config_error = None

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        _config_error = "Las variables SUPABASE_URL o SUPABASE_KEY no están configuradas en el archivo .env"
    else:
        # Remover espacios en blanco accidentales que a veces copia el usuario
        url = SUPABASE_URL.strip()
        key = SUPABASE_KEY.strip()
        if not url or not key or url.startswith("https://tu-proyecto"):
            _config_error = "Las credenciales de Supabase en el archivo .env parecen no haber sido configuradas correctamente."
        else:
            _client = create_client(url, key)
except Exception as e:
    _config_error = f"Error al inicializar el cliente de Supabase: {str(e)}"

def get_supabase_client() -> Client:
    """Retorna la instancia del cliente Supabase si está disponible."""
    if _config_error:
        raise ValueError(_config_error)
    return _client

def is_configured() -> bool:
    """Verifica si el cliente de Supabase fue configurado con éxito."""
    return _client is not None

def get_config_error() -> str:
    """Retorna el mensaje de error de configuración si existe."""
    return _config_error or ""
