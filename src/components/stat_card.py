import flet as ft
from typing import Any
from flet.controls.border import Border

class StatCard(ft.Container):
    """
    Tarjeta de estadística estilizada para el Dashboard.
    Muestra un título, un valor destacado, un ícono y un color de acento.
    """
    def __init__(
        self,
        title: str,
        value: str,
        icon: Any,
        color: str = "#D81E05",  # Rojo por defecto
        subtitle: str | None = None,
        alert_mode: bool = False,
        alert_color: str | None = None
    ):
        # Configurar colores según el modo de alerta y severidad
        if alert_mode and alert_color:
            c_upper = alert_color.upper()
            if c_upper == "#FF4D4D":  # Alerta Roja
                border_color = "#EF4444"  # Rojo Tailwind
                bg_color = "#FEF2F2"      # Rojo pastel muy suave
                text_icon_color = "#DC2626"
            elif c_upper == "#FFAA00":  # Alerta Amarilla
                border_color = "#F59E0B"  # Amarillo/Ámbar Tailwind
                bg_color = "#FFFBEB"      # Amarillo pastel muy suave
                text_icon_color = "#D97706"
            else:
                border_color = alert_color
                bg_color = f"{alert_color}1A"  # ~10% de opacidad
                text_icon_color = alert_color
        else:
            border_color = "#E4E4E7"
            bg_color = "#FFFFFF"
            text_icon_color = color
        
        content_column = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=14, color="#71717A", weight=ft.FontWeight.W_500),
                        ft.Icon(icon, color=text_icon_color, size=24),
                    ]
                ),
                ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color="#18181B"),
            ],
            spacing=8,
            tight=True
        )
        
        if subtitle:
            content_column.controls.append(
                ft.Text(subtitle, size=11, color="#71717A")
            )
            
        super().__init__(
            content=content_column,
            padding=20,
            border_radius=12,
            bgcolor=bg_color,
            border=Border.all(width=1, color=border_color),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#00000008",
                offset=ft.Offset(0, 4)
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            expand=True
        )
        
        # Efecto hover interactivo
        self.on_hover = self._handle_hover
        self.base_border_color = border_color
        self.hover_color = text_icon_color

    def _handle_hover(self, e):
        # Resaltar borde en hover
        if e.data == "true":
            self.border = Border.all(width=1.5, color=self.hover_color)
            self.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color="#0000000F",
                offset=ft.Offset(0, 6)
            )
        else:
            self.border = Border.all(width=1, color=self.base_border_color)
            self.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color="#00000008",
                offset=ft.Offset(0, 4)
            )
        self.update()
