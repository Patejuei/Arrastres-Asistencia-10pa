import flet as ft
import datetime
from src.database.db_service import db_service
from src.components.dialogs import show_snackbar, show_confirm_dialog

def create_licencias_view(page: ft.Page) -> ft.Container:
    """Retorna el componente contenedor de la vista de Licencias."""
    
    # Estado local
    licencias_data = []
    bomberos_activos = []

    # Buscador
    search_input = ft.TextField(
        label="Buscar Bombero",
        hint_text="Buscar por nombre o registro...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        width=300,
        on_change=lambda e: filter_licencias()
    )

    licencias_table = ft.DataTable(
        columns=[
            # Cabecera
            ft.DataColumn(label= ft.Text("Reg. Bombero")),
            ft.DataColumn(label= ft.Text("Nombre Bombero")),
            ft.DataColumn(label= ft.Text("Desde")),
            ft.DataColumn(label= ft.Text("Hasta")),
            ft.DataColumn(label= ft.Text("Duración")),
            ft.DataColumn(label= ft.Text("Motivo")),
            ft.DataColumn(label= ft.Text("Estado")),
            ft.DataColumn(label= ft.Text("Acciones")),
        ],
        rows=[],
        heading_row_color="#F8FAFC",
        divider_thickness=1,
    )

    table_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[licencias_table],
                    scroll=ft.ScrollMode.AUTO,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        border_radius=8,
        border=ft.Border.all(width=1, color="#E4E4E7"),
        bgcolor="#FFFFFF",
        expand=True
    )

    loading_bar = ft.ProgressBar(color="#D81E05", visible=False)

    # Contenedor raíz
    header_row_controls: list[ft.Control] = [
        ft.Column(
            controls=[
                ft.Text("Gestión de Licencias", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
                ft.Text("Administrar justificativos y licencias de inasistencia autorizadas", size=13, color="#71717A")
            ],
            spacing=4
        ),
        ft.ElevatedButton(
            "Registrar Licencia", # type: ignore
            icon=ft.Icons.ADD_ROUNDED,
            style=ft.ButtonStyle(
                bgcolor="#D81E05",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: open_licencia_modal()
        )
    ]

    header_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=header_row_controls
    )

    filters_row_controls: list[ft.Control] = [
        search_input,
    ]

    filters_row = ft.Row(
        controls=filters_row_controls,
        spacing=10,
        alignment=ft.MainAxisAlignment.START
    )

    column_controls: list[ft.Control] = [
        header_row,
        ft.Container(height=10),
        filters_row,
        loading_bar,
        ft.Container(height=5),
        table_container
    ]

    root_container = ft.Container(
        content=ft.Column(
            controls=column_controls,
            spacing=10,
            expand=True
        ),
        padding=30,
        expand=True
    )

    def load_licencias():
        nonlocal licencias_data, bomberos_activos
        loading_bar.visible = True
        root_container.update()
        
        try:
            # Cargar bomberos para los dropdowns del formulario
            bomberos_activos = db_service.get_bomberos()
            # Cargar licencias
            licencias_data = db_service.get_licencias()
            
            filter_licencias()
            
        except Exception as ex:
            show_snackbar(page, f"Error al cargar datos: {ex}", is_error=True)
            
        loading_bar.visible = False
        root_container.update()

    def filter_licencias():
        q = search_input.value.lower().strip() if search_input.value else ""
        
        licencias_table.rows.clear()
        
        for lic in licencias_data:
            reg = lic["reg_bombero"]
            b_info = lic.get("bomberos") or {}
            nombres = b_info.get("nombres", "").lower()
            ap_paterno = b_info.get("apellido_paterno", "").lower()
            ap_materno = b_info.get("apellido_materno", "").lower()
            nombre_completo = f"{nombres} {ap_paterno} {ap_materno}"
            
            # Aplicar filtro de búsqueda
            if q and (q not in reg.lower() and q not in nombre_completo):
                continue
                
            f_desde_dt = datetime.datetime.strptime(lic["fecha_desde"][:10], "%Y-%m-%d").date()
            f_hasta_dt = datetime.datetime.strptime(lic["fecha_hasta"][:10], "%Y-%m-%d").date()
            
            dias_duracion = (f_hasta_dt - f_desde_dt).days + 1
            
            aprobada = lic.get("aprobado", False)
            estado_lbl = "Aprobada" if aprobada else "Pendiente"
            estado_color = "#10B981" if aprobada else "#F59E0B"
            
            licencias_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(reg, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(f"{b_info.get('apellido_paterno', '')}, {b_info.get('nombres', '')}")),
                        ft.DataCell(ft.Text(f_desde_dt.strftime("%d-%m-%Y"))),
                        ft.DataCell(ft.Text(f_hasta_dt.strftime("%d-%m-%Y"))),
                        ft.DataCell(ft.Text(f"{dias_duracion} día(s)")),
                        ft.DataCell(ft.Text(lic["motivo"], max_lines=1)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(estado_lbl, color="#FFFFFF", size=10, weight=ft.FontWeight.W_500),
                                bgcolor=estado_color,
                                padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_ROUNDED,
                                        icon_color="#3B82F6",
                                        icon_size=18,
                                        tooltip="Editar Licencia",
                                        on_click=self_make_edit_handler(lic)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_ROUNDED,
                                        icon_color="#FF4D4D",
                                        icon_size=18,
                                        tooltip="Eliminar Licencia",
                                        on_click=self_make_delete_handler(lic["id"], reg)
                                    )
                                ],
                                spacing=0
                            )
                        )
                    ]
                )
            )
        licencias_table.update()

    def self_make_edit_handler(licencia):
        return lambda e: open_licencia_modal(licencia)

    def self_make_delete_handler(lic_id, reg_bombero):
        def delete_action(e):
            success, msg = db_service.delete_licencia(lic_id)
            if success:
                show_snackbar(page, "Licencia eliminada con éxito.")
                load_licencias()
            else:
                show_snackbar(page, msg, is_error=True)
        return lambda e: show_confirm_dialog(
            page,
            title="Eliminar Licencia",
            content_text=f"¿Estás seguro de que querés eliminar esta licencia del bombero Reg. {reg_bombero}? Esto podría alterar el cálculo de inactividad de su Dashboard.",
            on_confirm=delete_action
        )

    # ==========================================
    # MODAL REGISTRAR/EDITAR LICENCIA
    # ==========================================
    def open_licencia_modal(licencia_previa=None):
        is_edit = licencia_previa is not None
        
        # Inputs
        bombero_dropdown = ft.Dropdown(
            label="Bombero",
            options=[ft.dropdown.Option(b["registro_general"], f"{b['registro_general']} - {b['apellido_paterno']} {b['nombres']}") for b in bomberos_activos],
            expand=True,
            disabled=is_edit # No permitir cambiar de bombero al editar
        )
        
        fecha_desde_input = ft.TextField(
            label="Desde (DD-MM-YYYY)",
            value=datetime.date.today().strftime("%d-%m-%Y"),
            expand=True
        )
        
        fecha_hasta_input = ft.TextField(
            label="Hasta (DD-MM-YYYY)",
            value=datetime.date.today().strftime("%d-%m-%Y"),
            expand=True
        )
        
        # Selectores nativos
        def handle_desde_change(e):
            if date_picker_desde.value:
                fecha_desde_input.value = date_picker_desde.value.strftime("%d-%m-%Y")
                fecha_desde_input.update()
                
        def handle_hasta_change(e):
            if date_picker_hasta.value:
                fecha_hasta_input.value = date_picker_hasta.value.strftime("%d-%m-%Y")
                fecha_hasta_input.update()

        date_picker_desde = ft.DatePicker(on_change=handle_desde_change)
        date_picker_hasta = ft.DatePicker(on_change=handle_hasta_change)
        
        page.overlay.extend([date_picker_desde, date_picker_hasta])

        def open_picker_desde(e):
            date_picker_desde.open = True
            page.update()

        def open_picker_hasta(e):
            date_picker_hasta.open = True
            page.update()

        desde_btn = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_desde)
        hasta_btn = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_hasta)

        motivo_input = ft.TextField(label="Motivo / Justificación", hint_text="ej: Licencia Médica, Viaje laboral...", expand=True)
        aprobado_checkbox = ft.Checkbox(label="Licencia Aprobada (Descuenta inactividad)", value=True, fill_color="#D81E05")

        # Cargar datos previos si es edición
        if is_edit:
            bombero_dropdown.value = licencia_previa["reg_bombero"]
            fecha_desde_input.value = datetime.datetime.strptime(licencia_previa["fecha_desde"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
            fecha_hasta_input.value = datetime.datetime.strptime(licencia_previa["fecha_hasta"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
            motivo_input.value = licencia_previa["motivo"]
            aprobado_checkbox.value = licencia_previa["aprobado"]

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Licencia" if is_edit else "Registrar Nueva Licencia", weight=ft.FontWeight.BOLD, size=18),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def handle_save(e):
            if not bombero_dropdown.value:
                show_snackbar(page, "Falta seleccionar al bombero.", is_error=True)
                return
            if not fecha_desde_input.value or not fecha_hasta_input.value:
                show_snackbar(page, "Falta ingresar el rango de fechas.", is_error=True)
                return
            if not motivo_input.value:
                show_snackbar(page, "Falta ingresar el motivo.", is_error=True)
                return

            try:
                desde_dt = datetime.datetime.strptime(fecha_desde_input.value.strip(), "%d-%m-%Y").date()
                hasta_dt = datetime.datetime.strptime(fecha_hasta_input.value.strip(), "%d-%m-%Y").date()
                
                if desde_dt > hasta_dt:
                    show_snackbar(page, "La fecha 'Desde' no puede ser posterior a la fecha 'Hasta'.", is_error=True)
                    return
            except ValueError:
                show_snackbar(page, "Formato de fechas inválido. Usar DD-MM-YYYY.", is_error=True)
                return

            lic_data = {
                "reg_bombero": bombero_dropdown.value,
                "fecha_desde": desde_dt.isoformat(),
                "fecha_hasta": hasta_dt.isoformat(),
                "motivo": motivo_input.value.strip(),
                "aprobado": aprobado_checkbox.value
            }

            if is_edit:
                assert licencia_previa is not None
                success, msg = db_service.update_licencia(licencia_previa["id"], lic_data)
            else:
                success, msg = db_service.create_licencia(lic_data)
                
            if success:
                show_snackbar(page, "Licencia guardada correctamente.")
                dialog.open = False
                page.update()
                load_licencias()
            else:
                show_snackbar(page, msg, is_error=True)

        def handle_close(e):
            dialog.open = False
            page.update()

        actions_list: list[ft.Control] = [
            ft.TextButton("Cancelar", on_click=handle_close, style=ft.ButtonStyle(color="#71717A")), # type: ignore
            ft.ElevatedButton("Guardar", on_click=handle_save, style=ft.ButtonStyle(bgcolor="#D81E05", color="#FFFFFF")) # type: ignore
        ]
        dialog.actions = actions_list

        dialog_controls: list[ft.Control] = [
            ft.Row(controls=[bombero_dropdown]),
            ft.Row(controls=[fecha_desde_input, desde_btn]),
            ft.Row(controls=[fecha_hasta_input, hasta_btn]),
            ft.Row(controls=[motivo_input]),
            ft.Row(controls=[aprobado_checkbox]),
        ]

        dialog.content = ft.Container(
            content=ft.Column(
                controls=dialog_controls,
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                tight=True
            ),
            width=400,
            padding=10
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Cargar al iniciar
    def on_init(e):
        load_licencias()
        
    root_container.on_mount = on_init # type: ignore
    root_container.load_data = load_licencias # type: ignore
    
    return root_container
