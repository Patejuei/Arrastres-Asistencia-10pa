import flet as ft
import locale

from src.database.auth_service import auth_service
from src.config.supabase_client import is_configured
from src.views.login_view import create_login_view
from src.views.dashboard_view import create_dashboard_view
from src.views.arrastre_view import create_arrastre_view
from src.views.licencias_view import create_licencias_view
from src.views.bomberos_view import create_bomberos_view
from src.views.informes_view import create_informes_view
from src.components.sidebar import Sidebar

# Intentar configurar el locale para fechas en español (opcional)
try:
    locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
except Exception:
    try:
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except Exception:
        pass # Usar local del sistema por defecto si falla

async def main(page: ft.Page):
    page.title = "Bomba Suiza - Control de Asistencia"
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 650
    await page.window.center()
    
    # Modo claro por defecto
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Configuración de tema premium
    page.theme = ft.Theme(
        color_scheme_seed="#D81E05",  # Semilla de color basada en el Rojo Suizo
        color_scheme=ft.ColorScheme(
            primary="#D81E05",
            on_primary="#FFFFFF",
            secondary="#1E1E24",
            on_secondary="#FFFFFF",
            error="#FF4D4D",
            surface="#FFFFFF",
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )

    # Contenedor principal para SPA (Single Page Application)
    content_area = ft.Container(expand=True)
    sidebar_instance = None

    def navigate_to(route_name: str):
        """Maneja la navegación interna actualizando el contenedor principal."""
        # Si no está autenticado y no vamos al login, forzar login
        if not auth_service.is_authenticated() and route_name != "/login":
            show_login_screen()
            return

        if route_name == "/login":
            show_login_screen()
            return

        # Si no está configurado Supabase, redirigir al login (que mostrará el error de config)
        if not is_configured():
            show_login_screen()
            return

        # Actualizar vista del content_area según la ruta elegida
        if route_name == "/dashboard":
            content_area.content = create_dashboard_view(page)
        elif route_name == "/arrastre":
            content_area.content = create_arrastre_view(page)
        elif route_name == "/licencias":
            content_area.content = create_licencias_view(page)
        elif route_name == "/bomberos":
            content_area.content = create_bomberos_view(page)
        elif route_name == "/informes":
            content_area.content = create_informes_view(page)

        # Sincronizar el estado seleccionado del Sidebar
        if sidebar_instance:
            sidebar_instance.set_active_route(route_name)

        page.update()

        # Cargar datos después de montar
        if hasattr(content_area.content, "load_data"):
            try:
                load_fn = getattr(content_area.content, "load_data")
                if load_fn:
                    load_fn()
            except Exception as ex:
                print(f"Error cargando datos para la vista {route_name}: {ex}")

    def show_login_screen():
        """Renderiza la pantalla de login a tamaño completo."""
        page.clean()
        # El callback al loguearse con éxito nos manda al dashboard
        login_view = create_login_view(page, on_login_success=lambda: show_app_layout())
        page.add(login_view)
        page.update()

    def show_app_layout():
        """Renderiza el layout principal de la aplicación con Sidebar y área de contenido SPA."""
        nonlocal sidebar_instance
        page.clean()  # Limpiar la pantalla del login

        # Crear el Sidebar con el callback de navegación
        sidebar_instance = Sidebar(
            current_route="/dashboard",
            on_navigation=navigate_to
        )

        # Estructura principal de la app (Sidebar a la izquierda, Contenido a la derecha)
        main_layout = ft.Row(
            controls=[
                sidebar_instance,
                ft.VerticalDivider(width=1, color="#E4E4E7"),
                content_area
            ],
            spacing=0,
            expand=True
        )

        # Cargar la vista por defecto (Dashboard)
        content_area.content = create_dashboard_view(page)
        
        page.add(
            ft.SafeArea(
                content=main_layout,
                expand=True
            )
        )
        page.update()

        # Cargar datos para la vista por defecto (Dashboard)
        if hasattr(content_area.content, "load_data"):
            try:
                load_fn = getattr(content_area.content, "load_data")
                if load_fn:
                    load_fn()
            except Exception as ex:
                print(f"Error cargando datos para la vista inicial: {ex}")

    # --- FLUJO INICIAL ---
    # Verificar si ya existe una sesión guardada de Supabase Auth
    if is_configured() and auth_service.is_authenticated():
        show_app_layout()
    else:
        show_login_screen()

# Para ejecutar el archivo directamente
if __name__ == "__main__":
    ft.run(main)
