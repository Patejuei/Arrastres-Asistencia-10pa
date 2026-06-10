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
        # Configurar colores según el modo de alerta
        border_color = alert_color if alert_mode else "#E4E4E7"
        bg_color = f"{alert_color}0A" if alert_mode else "#FFFFFF"  # 0A es opacidad muy baja en hexadecimal
        
        content_column = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=14, color="#71717A", weight=ft.FontWeight.W_500),
                        ft.Icon(icon, color=color if not alert_mode else alert_color, size=24),
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
        self.hover_color = color if not alert_mode else alert_color

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
