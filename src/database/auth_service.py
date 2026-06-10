from src.config.supabase_client import get_supabase_client, is_configured

class AuthService:
    def __init__(self):
        self._current_user = None

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Intenta iniciar sesión en Supabase.
        Mapea el nombre de usuario a un email del dominio @bombasuiza.cl para usar Supabase Auth.
        Retorna (True, 'Éxito') o (False, 'Mensaje de error').
        """
        if not is_configured():
            return False, "La base de datos no está configurada correctamente en el archivo .env."

        if not username or not password:
            return False, "Nombre de usuario y contraseña son requeridos."

        # Mapear username a email sintético si no tiene formato de email ya
        email = username.strip()
        if "@" not in email:
            # Para aceptar RUT o registro general
            email = f"{email.lower()}@bombasuiza.cl"

        try:
            supabase = get_supabase_client()
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if res.user:
                self._current_user = res.user
                return True, "Inicio de sesión exitoso"
            else:
                return False, "No se pudo obtener información del usuario autenticado."
        except Exception as e:
            # Capturar errores comunes de Supabase Auth
            err_msg = str(e)
            if "Invalid login credentials" in err_msg:
                return False, "Usuario o contraseña incorrectos."
            elif "Email not confirmed" in err_msg:
                return False, "El correo electrónico del usuario no ha sido confirmado en Supabase."
            else:
                return False, f"Error al iniciar sesión: {err_msg}"

    def logout(self) -> bool:
        """Cierra la sesión actual del usuario."""
        if not is_configured():
            self._current_user = None
            return True
            
        try:
            supabase = get_supabase_client()
            supabase.auth.sign_out()
            self._current_user = None
            return True
        except Exception:
            self._current_user = None
            return False

    def get_current_user(self):
        """Retorna los datos del usuario actual si está autenticado."""
        if self._current_user:
            return self._current_user
            
        # Si no está en memoria, intentar buscar la sesión actual en el cliente de Supabase
        if is_configured():
            try:
                supabase = get_supabase_client()
                session = supabase.auth.get_session()
                if session and session.user:
                    self._current_user = session.user
                    return self._current_user
            except Exception:
                pass
        return None

    def is_authenticated(self) -> bool:
        """Verifica si el usuario está autenticado."""
        return self.get_current_user() is not None

# Instancia global del servicio para compartir sesión en toda la app
auth_service = AuthService()
