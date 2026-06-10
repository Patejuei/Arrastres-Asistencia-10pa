import flet as ft
from src.database.auth_service import auth_service
from src.config.supabase_client import is_configured, get_config_error
from src.components.dialogs import show_snackbar

def create_login_view(page: ft.Page, on_login_success) -> ft.Container:
    """
    Retorna el contenedor de la vista de inicio de sesión.
    on_login_success es un callback ejecutado cuando el inicio de sesión es exitoso.
    """
    # Inputs
    username_input = ft.TextField(
        label="Nombre de Usuario (N° Registro o Email)",
        hint_text="ej: 100 o admin@bombasuiza.cl",
        prefix_icon=ft.Icons.PERSON_ROUNDED,
        border_color="#D1D5DB",
        focused_border_color="#D81E05",
        text_size=14,
        height=50,
        autofocus=True
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        hint_text="••••••••",
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        password=True,
        can_reveal_password=True,
        border_color="#D1D5DB",
        focused_border_color="#D81E05",
        text_size=14,
        height=50
    )
    
    error_text = ft.Text(
        value="",
        color="#FF4D4D",
        size=13,
        weight=ft.FontWeight.W_500,
        visible=False
    )
    
    login_button = ft.ElevatedButton(
        "Iniciar Sesión", # type: ignore
        style=ft.ButtonStyle(
            bgcolor="#D81E05",
            color="#FFFFFF",
            padding=ft.Padding.symmetric(vertical=15, horizontal=30),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        height=46,
        expand=True
    )

    progress_bar = ft.ProgressBar(color="#D81E05", visible=False)

    def handle_login(e):
        # Desactivar controles durante la llamada
        username = username_input.value
        password = password_input.value
        
        if not username or not password:
            error_text.value = "Ingresá tu usuario y contraseña."
            error_text.visible = True
            page.update()
            return
            
        error_text.visible = False
        progress_bar.visible = True
        username_input.disabled = True
        password_input.disabled = True
        login_button.disabled = True
        page.update()
        
        # Intentar login
        success, msg = auth_service.login(username, password)
        
        progress_bar.visible = False
        username_input.disabled = False
        password_input.disabled = False
        login_button.disabled = False
        
        if success:
            show_snackbar(page, "¡Bienvenido, camarada!")
            on_login_success()
        else:
            error_text.value = msg
            error_text.visible = True
            page.update()

    login_button.on_click = handle_login
    
    # Soporte para presionar 'Enter' en los campos y loguear
    def on_submit(e):
        handle_login(e)
    username_input.on_submit = on_submit
    password_input.on_submit = on_submit

    # Si Supabase NO está configurado, mostramos una alerta
    if not is_configured():
        config_err = get_config_error()
        no_config_controls: list[ft.Control] = [
            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#FFAA00", size=64),
            ft.Text("Base de Datos No Configurada", size=20, weight=ft.FontWeight.BOLD, color="#18181B"),
            ft.Container(
                content=ft.Text(
                    f"Por favor, configurá las credenciales de Supabase en el archivo .env de la raíz del proyecto para continuar.\n\nDetalle:\n{config_err}",
                    color="#52525B",
                    size=14,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=15,
                bgcolor="#FFFBEB",
                border=ft.Border.all(1, "#FEF3C7"),
                border_radius=8
            ),
            ft.TextButton(
                "Reintentar Conexión", # type: ignore
                icon=ft.Icons.REFRESH_ROUNDED,
                icon_color="#D81E05",
                style=ft.ButtonStyle(color="#D81E05"),
                on_click=lambda e: page.window.destroy()  # O cerrar para que recargue al abrir de nuevo
            )
        ]

        content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=no_config_controls,
            spacing=10
        )
    else:
        # Layout normal de login
        login_controls: list[ft.Control] = [
            # Escudo/Icono
            ft.Container(
                content=ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, color="#D81E05", size=50),
                bgcolor="#FEF2F2",
                padding=15,
                border_radius=50,
            ),
            
            # Título institucional
            ft.Text("Décima Compañía", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
            ft.Text("Bomba Suiza", size=16, color="#D81E05", weight=ft.FontWeight.W_600),
            ft.Text("Sistema de Registro de Asistencias", size=13, color="#71717A"),
            
            error_text,
            progress_bar,
            ft.Container(height=5),
            
            username_input,
            ft.Container(height=10),
            password_input,
            ft.Container(height=20),
            
            ft.Row(controls=[login_button]),
        ]

        content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=login_controls,
            spacing=0
        )

    # Tarjeta de Login
    card = ft.Container(
        content=content,
        width=400,
        bgcolor="#FFFFFF",
        padding=40,
        border_radius=16,
        border=ft.Border.all(1, "#E4E4E7"),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=25,
            color="#0000000D",
            offset=ft.Offset(0, 8)
        )
    )

    # Fondo degradado de la página entera
    root_controls: list[ft.Control] = [card]

    return ft.Container(
        content=ft.Column(
            controls=root_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.Alignment(-1.0, -1.0),
            end=ft.alignment.Alignment(1.0, 1.0),
            colors=["#F5F6F8", "#E5E7EB"]
        ),
        expand=True
    )
