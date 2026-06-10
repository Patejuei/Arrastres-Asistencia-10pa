import flet as ft
from flet.controls.margin import Margin
from flet.controls.padding import Padding
from src.database.auth_service import auth_service

class Sidebar(ft.Container):
    """
    Menú de navegación lateral con diseño moderno y colores institucionales.
    """
    def __init__(self, current_route: str, on_navigation):
        self.current_route = current_route
        self.on_navigation = on_navigation  # Callback: func(route_name: str)
        
        # Obtener información del usuario logueado
        user = auth_service.get_current_user()
        username = "Bombero Décima"
        if user and user.email:
            username = user.email.split("@")[0].upper()

        # Botones de navegación
        self.nav_items = [
            ("Dashboard", ft.Icons.DASHBOARD_ROUNDED, "/dashboard"),
            ("Arrastre", ft.Icons.ASSESSMENT_ROUNDED, "/arrastre"),
            ("Licencias", ft.Icons.CARD_MEMBERSHIP_ROUNDED, "/licencias"),
            ("Bomberos", ft.Icons.PEOPLE_ROUNDED, "/bomberos"),
            ("Informes", ft.Icons.PRINT_ROUNDED, "/informes"),
        ]
        
        self.menu_buttons = []
        self._build_menu()

        # Contenedor del Sidebar
        super().__init__(
            width=260,
            bgcolor="#1E1E24",  # Gris carbón premium
            padding=Padding.all(20),
            content=ft.Column(
                controls=[
                    # Cabecera / Logo
                    ft.Container(
                        margin=Margin.only(bottom=30),
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, color="#D81E05", size=32),
                                        ft.Text("DECIMA CIA.", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    ],
                                    spacing=10
                                ),
                                ft.Text("Bomba Suiza", size=14, color="#D81E05", weight=ft.FontWeight.W_600, margin=Margin.only(left=42)),
                            ],
                            spacing=0
                        )
                    ),
                    
                    # Lista de botones
                    ft.Column(
                        controls=self.menu_buttons,
                        spacing=8,
                        expand=True
                    ),
                    
                    ft.Divider(color="#3F3F46", thickness=1),
                    
                    # Perfil de usuario y Logout
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(username, size=13, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                                    ft.Text("Décima Cía.", size=11, color="#A1A1AA"),
                                ],
                                spacing=2
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT_ROUNDED,
                                icon_color="#A1A1AA",
                                icon_size=20,
                                tooltip="Cerrar Sesión",
                                on_click=self._handle_logout
                            )
                        ]
                    )
                ]
            )
        )

    def _build_menu(self):
        self.menu_buttons.clear()
        for label, icon, route in self.nav_items:
            is_active = self.current_route == route
            
            # Estilos del botón según estado activo
            text_color = "#FFFFFF" if is_active else "#A1A1AA"
            bg_color = "#D81E05" if is_active else "transparent"
            icon_color = "#FFFFFF" if is_active else "#A1A1AA"
            weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL

            # Botón personalizado con contenedor interactivo
            btn = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(icon, color=icon_color, size=20),
                        ft.Text(label, color=text_color, size=14, weight=weight)
                    ],
                    spacing=12
                ),
                padding=Padding.symmetric(vertical=12, horizontal=16),
                border_radius=8,
                bgcolor=bg_color,
                on_click=self._make_navigate_handler(route),
                on_hover=self._make_hover_handler(is_active),
                data=route,  # Guardar la ruta para referencia en hover
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
            )
            self.menu_buttons.append(btn)

    def _make_navigate_handler(self, route):
        return lambda e: self.on_navigation(route)

    def _make_hover_handler(self, is_active):
        """Maneja el hover sobre los botones inactivos del menú."""
        if is_active:
            return None
        return lambda e: self._hover_effect(e)

    def _hover_effect(self, e):
        # Efecto de cambio de color al pasar el mouse por encima del botón inactivo
        container = e.control
        if e.data == "true":
            container.bgcolor = "#2D2D34"
        else:
            container.bgcolor = "transparent"
        container.update()

    def set_active_route(self, route):
        """Actualiza visualmente la opción activa del Sidebar sin recrear todo."""
        self.current_route = route
        self._build_menu()
        self.update()

    def _handle_logout(self, e):
        # Callback para desconectar al usuario
        auth_service.logout()
        # Navegar al login
        self.on_navigation("/login")
