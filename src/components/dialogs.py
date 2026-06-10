import flet as ft

def show_snackbar(page: ft.Page, message: str, is_error: bool = False):
    """Muestra un SnackBar rápido en la parte inferior de la pantalla."""
    bg_color = "#FF4D4D" if is_error else "#22C55E"
    
    snack = ft.SnackBar(
        content=ft.Text(message, color="#FFFFFF", weight=ft.FontWeight.W_500),
        bgcolor=bg_color,
        action=ft.SnackBarAction(label="Entendido", text_color="#FFFFFF")
    )
    page.overlay.append(snack)
    snack.open = True
    page.update()

def show_confirm_dialog(
    page: ft.Page,
    title: str,
    content_text: str,
    on_confirm,
    confirm_text: str = "Confirmar",
    confirm_color: str = "#D81E05"
) -> ft.AlertDialog:
    """
    Muestra un diálogo de confirmación genérico (ej. eliminar).
    on_confirm es un callback que se ejecuta al presionar el botón de confirmación.
    """
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.WARNING_ROUNDED, color="#FFAA00", size=28),
                ft.Text(title, weight=ft.FontWeight.BOLD, size=18)
            ],
            spacing=10
        ),
        content=ft.Text(content_text, size=14, color="#52525B"),
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_dialog(e):
        dialog.open = False
        page.update()

    def handle_confirm(e):
        dialog.open = False
        page.update()
        on_confirm(e)

    dialog.actions = [
        ft.TextButton("Cancelar", on_click=close_dialog, style=ft.ButtonStyle(color="#71717A")),
        ft.ElevatedButton(
            confirm_text,
            on_click=handle_confirm,
            style=ft.ButtonStyle(
                bgcolor=confirm_color,
                color="#FFFFFF"
            )
        )
    ]
    
    page.overlay.append(dialog)
    dialog.open = True
    page.update()
    return dialog
