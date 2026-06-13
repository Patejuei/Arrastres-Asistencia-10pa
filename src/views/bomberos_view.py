import flet as ft
import datetime
from src.database.db_service import db_service
from src.components.dialogs import show_snackbar, show_confirm_dialog
from src.utils.validators import format_rut, validate_rut, clean_rut

ESTADOS_BOMBERO = ["Activo", "Renunciado", "Separado", "Expulsado"]

def create_bomberos_view(page: ft.Page) -> ft.Container:
    """Retorna el componente contenedor de la vista de Bomberos."""
    
    # Estado local
    bomberos_data = []

    # Buscador
    search_input = ft.TextField(
        label="Buscar Bombero",
        hint_text="Buscar por nombre, apellido, rut o registro...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        width=300,
        on_change=lambda e: filter_bomberos()
    )

    bomberos_table = ft.DataTable(
        columns=[
            ft.DataColumn(label= ft.Text("Reg. Gral.")),
            ft.DataColumn(label= ft.Text("Nombre")),
            ft.DataColumn(label= ft.Text("Apellidos")),
            ft.DataColumn(label= ft.Text("RUT")),
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
                    controls=[bomberos_table],
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
                ft.Text("Nómina de Personal", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
                ft.Text("Registro general de bomberos de la Cía. y su historial de movimientos", size=13, color="#71717A")
            ],
            spacing=4
        ),
        ft.ElevatedButton(
            "Agregar Bombero", # type: ignore
            icon=ft.Icons.ADD_ROUNDED,
            style=ft.ButtonStyle(
                bgcolor="#D81E05",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: open_bombero_modal()
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

    def load_bomberos():
        nonlocal bomberos_data
        loading_bar.visible = True
        root_container.update()
        
        try:
            bomberos_data = db_service.get_bomberos()
            filter_bomberos()
        except Exception as ex:
            show_snackbar(page, f"Error al cargar bomberos: {ex}", is_error=True)
            
        loading_bar.visible = False
        root_container.update()

    def filter_bomberos():
        q = search_input.value.lower().strip() if search_input.value else ""
        
        bomberos_table.rows.clear()
        for b in bomberos_data:
            reg = b["registro_general"]
            nombres = b["nombres"].lower()
            ap_paterno = b["apellido_paterno"].lower()
            ap_materno = b["apellido_materno"].lower()
            rut = b["rut"].lower()
            estado = b["state"] if "state" in b else b.get("estado", "Activo")
            
            nombre_completo = f"{nombres} {ap_paterno} {ap_materno}"
            
            # Filtro
            if q and (q not in reg.lower() and q not in nombre_completo and q not in rut):
                continue
                
            # Determinar color de badge de estado
            estado_colors = {
                "Activo": "#10B981",
                "Renunciado": "#6B7280",
                "Separado": "#F59E0B",
                "Expulsado": "#EF4444"
            }
            bg_badge = estado_colors.get(estado, "#71717A")
            
            bomberos_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(reg, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(b["nombres"])),
                        ft.DataCell(ft.Text(f"{b['apellido_paterno']} {b['apellido_materno']}")),
                        ft.DataCell(ft.Text(format_rut(b["rut"]))),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(estado, color="#FFFFFF", size=10, weight=ft.FontWeight.W_500),
                                bgcolor=bg_badge,
                                padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.EDIT_ROUNDED,
                                icon_color="#3B82F6",
                                icon_size=18,
                                tooltip="Ficha y Movimientos",
                                on_click=self_make_edit_handler(b)
                            )
                        )
                    ]
                )
            )
        bomberos_table.update()

    def self_make_edit_handler(bombero):
        return lambda e: open_bombero_modal(bombero)

    # ==========================================
    # MODAL FICHA BOMBERO / CRUD / MOVIMIENTOS
    # ==========================================
    def open_bombero_modal(bombero_previo=None):
        is_edit = bombero_previo is not None
        movimientos_list = []
        
        # 1. Inputs Personales
        reg_input = ft.TextField(
            label="Registro General",
            hint_text="ej: 101",
            disabled=is_edit,
            expand=True
        )
        
        nombres_input = ft.TextField(label="Nombres", expand=True)
        paterno_input = ft.TextField(label="Apellido Paterno", expand=True)
        materno_input = ft.TextField(label="Apellido Materno", expand=True)
        
        rut_input = ft.TextField(
            label="RUT",
            hint_text="12345678-9",
            expand=True,
            on_blur=lambda e: format_rut_field()
        )
        
        estado_dropdown = ft.Dropdown(
            label="Estado",
            options=[ft.dropdown.Option(st) for st in ESTADOS_BOMBERO],
            value="Activo",
            expand=True
        )

        # Campo exclusivo para nuevos ingresos: Fecha de Ingreso Inicial
        fecha_ingreso_inicial_input = ft.TextField(
            label="Fecha de Ingreso (DD-MM-YYYY)",
            value=datetime.date.today().strftime("%d-%m-%Y"),
            visible=not is_edit,
            expand=True
        )
        
        def format_rut_field():
            if rut_input.value:
                rut_input.value = format_rut(rut_input.value)
                rut_input.update()

        # 2. Movimientos de Personal (Solo visible al editar)
        movimientos_column = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, expand=True)
        
        def load_movimientos_ui():
            nonlocal movimientos_list
            movimientos_column.controls.clear()
            
            if not is_edit:
                return
                
            assert bombero_previo is not None
            reg = bombero_previo["registro_general"]
            movimientos_list = db_service.get_movimientos_by_bombero(reg)
            
            if not movimientos_list:
                movimientos_column.controls.append(
                    ft.Text("Sin movimientos registrados.", italic=True, size=12, color="#71717A")
                )
            else:
                for m in movimientos_list:
                    f_ing = datetime.datetime.strptime(m["fecha_ingreso"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                    f_sal = datetime.datetime.strptime(m["fecha_salida"][:10], "%Y-%m-%d").strftime("%d-%m-%Y") if m["fecha_salida"] else "Vigente / Actualidad"
                    
                    movimientos_column.controls.append(
                        ft.Container(
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Text(f"Ingreso: {f_ing}", size=12, weight=ft.FontWeight.BOLD),
                                            ft.Text(f"Salida: {f_sal}", size=11, color="#71717A")
                                        ],
                                        spacing=2
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.EDIT_ROUNDED,
                                                icon_color="#3B82F6",
                                                icon_size=16,
                                                on_click=self_make_edit_mov_handler(m)
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.DELETE_ROUNDED,
                                                icon_color="#FF4D4D",
                                                icon_size=16,
                                                on_click=self_make_delete_mov_handler(m["id"])
                                            )
                                        ],
                                        spacing=0
                                    )
                                ]
                            ),
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(width=1, color="#F1F5F9")
                        )
                    )
            try:
                movimientos_column.update()
            except Exception:
                pass

        def self_make_edit_mov_handler(mov):
            return lambda e: open_movimiento_editor_modal(mov)

        def self_make_delete_mov_handler(mov_id):
            def delete_mov_action(e):
                success, msg = db_service.delete_movimiento(mov_id)
                if success:
                    show_snackbar(page, "Movimiento eliminado.")
                    load_movimientos_ui()
                else:
                    show_snackbar(page, msg, is_error=True)
            return lambda e: show_confirm_dialog(
                page,
                title="Eliminar Movimiento",
                content_text="¿Estás seguro de que querés eliminar este período de alta/baja? Afectará el cálculo de su universo de asistencia.",
                on_confirm=delete_mov_action
            )

        # Cargar datos iniciales
        if is_edit:
            reg_input.value = bombero_previo["registro_general"]
            nombres_input.value = bombero_previo["nombres"]
            paterno_input.value = bombero_previo["apellido_paterno"]
            materno_input.value = bombero_previo["apellido_materno"]
            rut_input.value = format_rut(bombero_previo["rut"])
            estado_dropdown.value = bombero_previo.get("estado", "Activo")
            
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ficha del Bombero" if is_edit else "Agregar Nuevo Bombero", weight=ft.FontWeight.BOLD, size=18),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def handle_save(e):
            # Validaciones
            if not reg_input.value or not reg_input.value.strip():
                show_snackbar(page, "Falta el Registro General.", is_error=True)
                return
            if not nombres_input.value or not nombres_input.value.strip():
                show_snackbar(page, "Falta ingresar los nombres.", is_error=True)
                return
            if not paterno_input.value or not paterno_input.value.strip():
                show_snackbar(page, "Falta ingresar el apellido paterno.", is_error=True)
                return
            if not materno_input.value or not materno_input.value.strip():
                show_snackbar(page, "Falta ingresar el apellido materno.", is_error=True)
                return
            
            cleaned_rut_val = clean_rut(rut_input.value)
            if not validate_rut(cleaned_rut_val):
                show_snackbar(page, "El RUT ingresado no es válido.", is_error=True)
                return

            bombero_data = {
                "registro_general": reg_input.value.strip(),
                "nombres": nombres_input.value.strip(),
                "apellido_paterno": paterno_input.value.strip(),
                "apellido_materno": materno_input.value.strip(),
                "rut": cleaned_rut_val,
                "estado": estado_dropdown.value
            }

            if is_edit:
                assert bombero_previo is not None
                success, msg = db_service.update_bombero(bombero_previo["registro_general"], bombero_data)
                if success:
                    show_snackbar(page, "Bombero actualizado correctamente.")
                    dialog.open = False
                    page.update()
                    load_bomberos()
                else:
                    show_snackbar(page, msg, is_error=True)
            else:
                # Creación: Requiere primer movimiento obligatorio
                try:
                    fecha_ing_dt = datetime.datetime.strptime(fecha_ingreso_inicial_input.value.strip(), "%d-%m-%Y").date()
                except ValueError:
                    show_snackbar(page, "Fecha de ingreso inicial inválida. Usar DD-MM-YYYY.", is_error=True)
                    return

                # Guardar en Supabase
                success, msg = db_service.create_bombero(bombero_data)
                if success:
                    # Crear movimiento de ingreso inicial automáticamente
                    db_service.create_movimiento({
                        "reg_bombero": bombero_data["registro_general"],
                        "fecha_ingreso": fecha_ing_dt.isoformat(),
                        "fecha_salida": None
                    })
                    show_snackbar(page, "Bombero y movimiento inicial creados con éxito.")
                    dialog.open = False
                    page.update()
                    load_bomberos()
                else:
                    show_snackbar(page, msg, is_error=True)

        def handle_close(e):
            dialog.open = False
            page.update()

        actions_list: list[ft.Control] = [
            ft.TextButton("Cerrar" if is_edit else "Cancelar", on_click=handle_close, style=ft.ButtonStyle(color="#71717A")), # type: ignore
            ft.ElevatedButton("Guardar Ficha", on_click=handle_save, style=ft.ButtonStyle(bgcolor="#D81E05", color="#FFFFFF")) # type: ignore
        ]
        dialog.actions = actions_list

        # Vistas de pestañas
        personales_controls: list[ft.Control] = [
            ft.Row(controls=[reg_input]),
            ft.Row(controls=[nombres_input]),
            ft.Row(controls=[paterno_input, materno_input]),
            ft.Row(controls=[rut_input]),
            ft.Row(controls=[estado_dropdown]),
            ft.Row(controls=[fecha_ingreso_inicial_input]),
        ]

        ficha_personales = ft.Container(
            content=ft.Column(
                controls=personales_controls,
                spacing=12,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=10
        )

        movimientos_panel_controls: list[ft.Control] = [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Historial de Altas/Bajas", size=14, weight=ft.FontWeight.BOLD),
                    ft.TextButton(
                        "Agregar Movimiento", # type: ignore
                        icon=ft.Icons.ADD_ROUNDED,
                        style=ft.ButtonStyle(color="#D81E05"),
                        on_click=lambda e: open_movimiento_editor_modal()
                    )
                ]
            ),
            ft.Divider(color="#E4E4E7"),
            ft.Container(content=movimientos_column, height=220, expand=True)
        ]

        ficha_movimientos = ft.Container(
            content=ft.Column(
                controls=movimientos_panel_controls,
                spacing=5,
                expand=True
            ),
            padding=10,
            expand=True
        )

        tabs_headers: list[ft.Control] = [ # type: ignore
            ft.Tab(label="Datos Personales", icon=ft.Icons.PERSON_ROUNDED)
        ]
        tabs_contents: list[ft.Control] = [
            ficha_personales
        ]
        if is_edit:
            tabs_headers.append(ft.Tab(label="Periodos de Servicio", icon=ft.Icons.HISTORY_ROUNDED))
            tabs_contents.append(ficha_movimientos)
            # Cargar los movimientos
            load_movimientos_ui()

        tabs_form = ft.Tabs(
            length=len(tabs_headers),
            selected_index=0,
            expand=True,
            height=380,
            width=500,
            content=ft.Column(
                expand=True,
                controls=[ # type: ignore
                    ft.TabBar(tabs=tabs_headers), # type: ignore
                    ft.TabBarView(expand=True, controls=tabs_contents)
                ]
            )
        )

        dialog.content = tabs_form
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

        # ==========================================
        # SUB-MODAL EDITOR DE MOVIMIENTOS
        # ==========================================
        def open_movimiento_editor_modal(movimiento_previo=None):
            is_edit_mov = movimiento_previo is not None
            
            f_ing_input = ft.TextField(
                label="Fecha de Ingreso (DD-MM-YYYY)",
                value=datetime.date.today().strftime("%d-%m-%Y"),
                expand=True
            )
            
            f_sal_input = ft.TextField(
                label="Fecha de Salida (Opcional - DD-MM-YYYY)",
                value="",
                hint_text="Dejar vacío si sigue activo",
                expand=True
            )

            # DatePickers
            def handle_ing_change(e):
                if picker_ing.value:
                    f_ing_input.value = picker_ing.value.strftime("%d-%m-%Y")
                    f_ing_input.update()
            
            def handle_sal_change(e):
                if picker_sal.value:
                    f_sal_input.value = picker_sal.value.strftime("%d-%m-%Y")
                    f_sal_input.update()

            picker_ing = ft.DatePicker(on_change=handle_ing_change)
            picker_sal = ft.DatePicker(on_change=handle_sal_change)
            page.overlay.extend([picker_ing, picker_sal])

            def open_picker_ing(e):
                picker_ing.open = True
                page.update()

            def open_picker_sal(e):
                picker_sal.open = True
                page.update()

            ing_btn = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_ing)
            sal_btn = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_sal)

            if is_edit_mov:
                assert movimiento_previo is not None
                f_ing_input.value = datetime.datetime.strptime(movimiento_previo["fecha_ingreso"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                f_sal_input.value = datetime.datetime.strptime(movimiento_previo["fecha_salida"][:10], "%Y-%m-%d").strftime("%d-%m-%Y") if movimiento_previo["fecha_salida"] else ""

            sub_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar Periodo" if is_edit_mov else "Agregar Período de Servicio", size=16, weight=ft.FontWeight.BOLD),
                actions_alignment=ft.MainAxisAlignment.END,
            )

            def save_movimiento(e):
                if not f_ing_input.value:
                    show_snackbar(page, "Falta la fecha de ingreso.", is_error=True)
                    return

                try:
                    ing_dt = datetime.datetime.strptime(f_ing_input.value.strip(), "%d-%m-%Y").date()
                    sal_dt = None
                    if f_sal_input.value and f_sal_input.value.strip():
                        sal_dt = datetime.datetime.strptime(f_sal_input.value.strip(), "%d-%m-%Y").date()
                        
                        if ing_dt > sal_dt:
                            show_snackbar(page, "La fecha de ingreso no puede ser posterior a la de salida.", is_error=True)
                            return
                except ValueError:
                    show_snackbar(page, "Fechas inválidas. Usar formato DD-MM-YYYY.", is_error=True)
                    return

                assert bombero_previo is not None
                mov_data = {
                    "reg_bombero": bombero_previo["registro_general"],
                    "fecha_ingreso": ing_dt.isoformat(),
                    "fecha_salida": sal_dt.isoformat() if sal_dt else None
                }

                if is_edit_mov:
                    assert movimiento_previo is not None
                    success, msg = db_service.update_movimiento(movimiento_previo["id"], mov_data)
                else:
                    success, msg = db_service.create_movimiento(mov_data)

                if success:
                    show_snackbar(page, "Período guardado correctamente.")
                    sub_dialog.open = False
                    page.update()
                    load_movimientos_ui()
                else:
                    show_snackbar(page, msg, is_error=True)

            def close_sub_dialog(e):
                sub_dialog.open = False
                page.update()

            sub_actions: list[ft.Control] = [
                ft.TextButton("Cancelar", on_click=close_sub_dialog, style=ft.ButtonStyle(color="#71717A")), # type: ignore
                ft.ElevatedButton("Guardar", on_click=save_movimiento, style=ft.ButtonStyle(bgcolor="#D81E05", color="#FFFFFF")) # type: ignore
            ]
            sub_dialog.actions = sub_actions

            sub_controls: list[ft.Control] = [
                ft.Row(controls=[f_ing_input, ing_btn]),
                ft.Row(controls=[f_sal_input, sal_btn]),
            ]

            sub_dialog.content = ft.Container(
                content=ft.Column(
                    controls=sub_controls,
                    spacing=10,
                    tight=True
                ),
                width=350,
                padding=10
            )

            page.overlay.append(sub_dialog)
            sub_dialog.open = True
            page.update()

    # Cargar al iniciar
    def on_init(e):
        load_bomberos()
        
    root_container.on_mount = on_init # type: ignore
    root_container.load_data = load_bomberos # type: ignore
    
    return root_container
