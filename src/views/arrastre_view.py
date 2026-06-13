import flet as ft
import datetime
from flet.controls.border import Border
from src.database.db_service import db_service
from src.components.dialogs import show_snackbar, show_confirm_dialog
from src.utils.validators import clean_rut
from src.config.claves import CLAVES_DESPACHO, CLAVES_DEFINITIVAS

MESES = [
    ("Enero", 1), ("Febrero", 2), ("Marzo", 3), ("Abril", 4),
    ("Mayo", 5), ("Junio", 6), ("Julio", 7), ("Agosto", 8),
    ("Septiembre", 9), ("Octubre", 10), ("Noviembre", 11), ("Diciembre", 12)
]

def create_arrastre_view(page: ft.Page) -> ft.Container:
    """Retorna el componente contenedor de la vista de Arrastre (Actos de Servicio)."""
    
    # Estado local de la vista
    actos_data = []
    bomberos_activos = []
    
    # Controles de filtros
    mes_filter = ft.Dropdown(
        label="Mes",
        hint_text="Filtrar por mes",
        options=[ft.dropdown.Option("", "Todos")] + [ft.dropdown.Option(str(v), k) for k, v in MESES],
        width=130,
        on_select=lambda e: filter_actos()
    )
    
    # Filtro por año
    anio_filter = ft.Dropdown(
        label="Año",
        options=[ft.dropdown.Option(str(y), str(y)) for y in range(datetime.date.today().year - 5, datetime.date.today().year + 2)],
        value=str(datetime.date.today().year),
        width=100,
        on_select=lambda e: filter_actos()
    )
    
    clave_filter = ft.Dropdown(
        label="Clave de Acto",
        hint_text="Filtrar por tipo de acto",
        options=[ft.dropdown.Option("", "Todas")] + [ft.dropdown.Option(code, desc) for code, desc in CLAVES_DESPACHO.items()],
        width=180,
        on_select=lambda e: filter_actos()
    )
    
    search_input = ft.TextField(
        label="Buscar",
        hint_text="Buscar por fecha, dirección o correlativo...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        width=250,
        on_change=lambda e: filter_actos()
    )
    
    actos_table = ft.DataTable(
        columns=[
            ft.DataColumn(label= ft.Text("Corr. Cía")),
            ft.DataColumn(label= ft.Text("Corr. Gral.")),
            ft.DataColumn(label= ft.Text("Fecha")),
            ft.DataColumn(label= ft.Text("Clave")),
            ft.DataColumn(label= ft.Text("Dirección")),
            ft.DataColumn(label= ft.Text("Esquina")),
            ft.DataColumn(label= ft.Text("Tipo")),
            ft.DataColumn(label= ft.Text("Asistencia")),
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
                    controls=[actos_table],
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
    # Contenedor raíz
    header_row_controls: list[ft.Control] = [
        ft.Column(
            controls=[
                ft.Text("Registro de Arrastre", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
                ft.Text("Gestionar actos de servicio y asistencias correspondientes", size=13, color="#71717A")
            ],
            spacing=4
        ),
        ft.ElevatedButton(
            "Nuevo Acto de Servicio", # type: ignore
            icon=ft.Icons.ADD_ROUNDED,
            style=ft.ButtonStyle(
                bgcolor="#D81E05",
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=lambda e: open_acto_modal()
        )
    ]

    header_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=header_row_controls
    )

    filters_row_controls: list[ft.Control] = [
        search_input,
        anio_filter,
        mes_filter,
        clave_filter,
        ft.IconButton(
            icon=ft.Icons.CLEAR_ALL_ROUNDED,
            tooltip="Limpiar Filtros",
            icon_color="#71717A",
            on_click=lambda e: reset_filters()
        )
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

    def load_actos():
        nonlocal actos_data, bomberos_activos
        loading_bar.visible = True
        root_container.update()
        
        try:
            # Obtener bomberos activos para los dropdowns
            bomberos_activos = db_service.get_bomberos_activos()
            
            # Obtener los filtros activos
            mes_val = int(mes_filter.value) if mes_filter.value else None
            anio_val = int(anio_filter.value) if anio_filter.value else None
            clave_val = clave_filter.value if clave_filter.value else None
            query_val = search_input.value if search_input.value else None
            
            # Obtener actos
            actos_data = db_service.get_actos(mes=mes_val, anio=anio_val, clave=clave_val, query=query_val)
            
            # Renderizar filas
            actos_table.rows.clear()
            for acto in actos_data:
                fecha_str = datetime.datetime.strptime(acto["fecha"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                corr_gen = str(acto["corr_general"] or "-")
                
                # Fila con datos
                actos_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(acto["corr_cia"]), weight=ft.FontWeight.BOLD)),
                            ft.DataCell(ft.Text(corr_gen)),
                            ft.DataCell(ft.Text(fecha_str)),
                            ft.DataCell(ft.Text(acto["clave"])),
                            ft.DataCell(ft.Text(acto["direccion"], max_lines=1)),
                            ft.DataCell(ft.Text(acto.get("esquina") or "-", max_lines=1)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(acto["tipo"], color="#FFFFFF", size=10, weight=ft.FontWeight.W_500),
                                    bgcolor="#10B981" if acto["tipo"] == "Efectiva" else "#3B82F6",
                                    padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                                    border_radius=4
                                )
                            ),
                            ft.DataCell(ft.Text(f"{acto['total_asistencia']} bomberos")),
                            ft.DataCell(
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_ROUNDED,
                                            icon_color="#3B82F6",
                                            icon_size=18,
                                            tooltip="Ver / Editar detalles y asistencia",
                                            on_click=self_make_edit_handler(acto["id"])
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_ROUNDED,
                                            icon_color="#FF4D4D",
                                            icon_size=18,
                                            tooltip="Eliminar Acto",
                                            on_click=self_make_delete_handler(acto["id"], acto["corr_cia"])
                                        )
                                    ],
                                    spacing=0
                                )
                            )
                        ]
                    )
                )
        except Exception as ex:
            show_snackbar(page, f"Error al cargar actos: {ex}", is_error=True)
            
        loading_bar.visible = False
        root_container.update()

    def filter_actos():
        load_actos()

    def reset_filters():
        search_input.value = ""
        mes_filter.value = ""
        anio_filter.value = str(datetime.date.today().year)
        clave_filter.value = ""
        load_actos()

    def self_make_edit_handler(acto_id):
        return lambda e: open_acto_modal(acto_id)

    def self_make_delete_handler(acto_id, corr_cia):
        def delete_action(e):
            success, msg = db_service.delete_acto(acto_id)
            if success:
                show_snackbar(page, "Acto de servicio eliminado con éxito.")
                load_actos()
            else:
                show_snackbar(page, msg, is_error=True)
        return lambda e: show_confirm_dialog(
            page,
            title="Eliminar Acto de Servicio",
            content_text=f"¿Estás seguro de que querés eliminar el Acto N° {corr_cia}? Esto borrará también el registro de asistencias asociado de manera permanente.",
            on_confirm=delete_action
        )

    # ==========================================
    # MODAL DE FORMULARIO COMPLETO (CRUD)
    # ==========================================
    def open_acto_modal(acto_id=None):
        is_edit = acto_id is not None
        
        # 1. Inputs del acto de servicio
        corr_cia_input = ft.TextField(label="Correlativo Compañía", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        corr_gen_input = ft.TextField(label="Correlativo General (Opcional)", keyboard_type=ft.KeyboardType.NUMBER, expand=True)
        
        fecha_input = ft.TextField(
            label="Fecha (DD-MM-YYYY)",
            value=datetime.date.today().strftime("%d-%m-%Y"),
            hint_text="DD-MM-YYYY",
            expand=True
        )
        
        # Selector de Fecha Nativo de Flet
        def handle_date_change(e):
            if date_picker.value:
                fecha_input.value = date_picker.value.strftime("%d-%m-%Y")
                fecha_input.update()
                
        date_picker = ft.DatePicker(
            first_date=datetime.date(2000, 1, 1),
            last_date=datetime.date(2100, 1, 1),
            on_change=handle_date_change
        )
        page.overlay.append(date_picker)
        
        def open_date_picker(e):
            date_picker.open = True
            page.update()

        date_btn = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
            icon_color="#D81E05",
            tooltip="Seleccionar Fecha",
            on_click=open_date_picker
        )
        
        # Selector de claves de 2 niveles
        def handle_categoria_change(e):
            selected_cat = clave_categoria_dropdown.value
            if selected_cat and selected_cat in CLAVES_DEFINITIVAS:
                clave_definitiva_dropdown.options = [
                    ft.dropdown.Option(code, desc) for code, desc in CLAVES_DEFINITIVAS[selected_cat]
                ]
                if CLAVES_DEFINITIVAS[selected_cat]:
                    clave_definitiva_dropdown.value = CLAVES_DEFINITIVAS[selected_cat][0][0]
            else:
                clave_definitiva_dropdown.options = []
                clave_definitiva_dropdown.value = None
            clave_definitiva_dropdown.update()

        clave_categoria_dropdown = ft.Dropdown(
            label="Categoría de Clave",
            options=[ft.dropdown.Option(code, desc) for code, desc in CLAVES_DESPACHO.items()],
            on_select=handle_categoria_change,
            expand=True
        )

        clave_definitiva_dropdown = ft.Dropdown(
            label="Clave Definitiva (Acto)",
            options=[],
            expand=True
        )
        
        direccion_input = ft.TextField(label="Dirección del Acto", expand=True)
        esquina_input = ft.TextField(label="Esquina (Opcional)", expand=True)
        
        tipo_dropdown = ft.Dropdown(
            label="Tipo de Acto",
            options=[
                ft.dropdown.Option("Efectiva", "Efectiva (Para arrastre obligatorio)"),
                ft.dropdown.Option("Abono", "Abono (Lista de abono/justificada)")
            ],
            value="Efectiva",
            expand=True
        )

        cant_listas_input = ft.TextField(
            label="Cantidad Máxima de Listas",
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True
        )
        
        # Dropdowns de oficiales
        bomberos_options = [ft.dropdown.Option(b["registro_general"], f"{b['registro_general']} - {b['apellido_paterno']} {b['nombres']}") for b in bomberos_activos]
        
        a_cargo_dropdown = ft.Dropdown(label="Oficial a Cargo Cía", options=bomberos_options, expand=True)
        tomo_lista_dropdown = ft.Dropdown(label="Oficial que Tomó Lista", options=bomberos_options, expand=True)

        # 2. Contenedor de Asistencias del Personal
        # Mapeamos bomberos activos a filas de asistencia en memoria
        # Estructura: reg_bombero -> { "checkbox": Checkbox, "listas": TextField }
        asistencia_controls = {}
        
        def toggle_all_asistencias(e):
            val = e.control.value
            for reg, ctrls in asistencia_controls.items():
                chk = ctrls["checkbox"]
                txt = ctrls["listas"]
                chk.value = val
                if val:
                    txt.disabled = False
                    txt.value = cant_listas_input.value or "1"
                else:
                    txt.disabled = True
                    txt.value = "0"
                chk.update()
                txt.update()

        check_all_cb = ft.Checkbox(label="Marcar a todos como asistidos", on_change=toggle_all_asistencias)
        
        asistencia_list_view = ft.Column(spacing=4, scroll=ft.ScrollMode.AUTO, expand=True)
        
        def toggle_listas_input(e, reg):
            chk = e.control
            txt = asistencia_controls[reg]["listas"]
            if chk.value:
                txt.disabled = False
                txt.value = cant_listas_input.value or "1"
            else:
                txt.disabled = True
                txt.value = "0"
            txt.update()

        # Inicializar lista de asistencia
        def build_asistencias_list_ui(current_asis_map=None):
            asistencia_list_view.controls.clear()
            asistencia_controls.clear()
            
            for b in bomberos_activos:
                reg = b["registro_general"]
                nombre = f"{b['apellido_paterno']} {b['apellido_materno']}, {b['nombres']}"
                
                # Obtener asistencia previa si estamos editando
                has_assisted = False
                cant_listas = 0
                if current_asis_map and reg in current_asis_map:
                    cant_listas = current_asis_map[reg]
                    has_assisted = cant_listas > 0
                    
                cb = ft.Checkbox(
                    value=has_assisted, 
                    fill_color="#D81E05",
                    on_change=lambda e, r=reg: toggle_listas_input(e, r)
                )
                
                txt = ft.TextField(
                    value=str(cant_listas),
                    width=60,
                    height=36,
                    content_padding=ft.Padding.symmetric(vertical=4, horizontal=8),
                    text_align=ft.TextAlign.CENTER,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    disabled=not has_assisted,
                    text_size=12
                )
                
                asistencia_controls[reg] = {
                    "checkbox": cb,
                    "listas": txt
                }
                
                asistencia_list_view.controls.append(
                    ft.Container(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Container(
                                            content=ft.Text(reg, color="#71717A", size=11, weight=ft.FontWeight.BOLD),
                                            bgcolor="#F4F4F5",
                                            padding=ft.Padding.symmetric(vertical=2, horizontal=6),
                                            border_radius=4
                                        ),
                                        ft.Text(nombre, size=13, weight=ft.FontWeight.W_500)
                                    ],
                                    spacing=10
                                ),
                                ft.Row(
                                    controls=[
                                        cb,
                                        ft.Text("Listas:", size=11, color="#71717A"),
                                        txt
                                    ],
                                    spacing=6
                                )
                            ]
                        ),
                        padding=ft.Padding.symmetric(vertical=6, horizontal=12),
                        border_radius=6,
                        bgcolor="#FFFFFF",
                        border=Border.all(width=1, color="#E4E4E7")
                    )
                )

        # 3. Cargar datos previos si es edición
        current_acto = None
        if is_edit:
            current_acto = db_service.get_acto_detalles(acto_id)
            if current_acto:
                corr_cia_input.value = str(current_acto["corr_cia"])
                corr_gen_input.value = str(current_acto["corr_general"] or "")
                fecha_input.value = datetime.datetime.strptime(current_acto["fecha"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                direccion_input.value = current_acto["direccion"]
                esquina_input.value = current_acto.get("esquina") or ""
                tipo_dropdown.value = current_acto["tipo"]
                a_cargo_dropdown.value = current_acto.get("a_cargo_cia")
                tomo_lista_dropdown.value = current_acto.get("tomo_lista")
                cant_listas_input.value = str(current_acto.get("cantidad_listas", 1))
                
                # Cargar claves de 2 niveles
                definitive_clave = current_acto["clave"]
                cat_parts = definitive_clave.split("-")
                if len(cat_parts) >= 3:
                    cat_code = "-".join(cat_parts[:-1])
                else:
                    cat_code = definitive_clave
                
                clave_categoria_dropdown.value = cat_code
                if cat_code in CLAVES_DEFINITIVAS:
                    clave_definitiva_dropdown.options = [
                        ft.dropdown.Option(code, desc) for code, desc in CLAVES_DEFINITIVAS[cat_code]
                    ]
                clave_definitiva_dropdown.value = definitive_clave
                
                # Crear un mapa de reg_bombero -> cantidad_listas
                prev_asis = {asis["reg_bombero"]: asis["cantidad_listas"] for asis in current_acto.get("asistencias", [])}
                build_asistencias_list_ui(prev_asis)
        else:
            build_asistencias_list_ui()

        # Modal
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Acto de Servicio" if is_edit else "Crear Nuevo Acto de Servicio", weight=ft.FontWeight.BOLD, size=18),
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def handle_save(e):
            # Validaciones básicas
            if not corr_cia_input.value:
                show_snackbar(page, "Falta el Correlativo de Compañía.", is_error=True)
                return
            if not fecha_input.value:
                show_snackbar(page, "Falta la Fecha del Acto.", is_error=True)
                return
            if not clave_definitiva_dropdown.value:
                show_snackbar(page, "Falta seleccionar la Clave Definitiva del Acto.", is_error=True)
                return
            if not direccion_input.value:
                show_snackbar(page, "Falta la Dirección.", is_error=True)
                return
            if not cant_listas_input.value:
                show_snackbar(page, "Falta la Cantidad Máxima de Listas.", is_error=True)
                return
            try:
                max_listas = int(cant_listas_input.value)
                if max_listas < 1:
                    show_snackbar(page, "La cantidad de listas del acto debe ser al menos 1.", is_error=True)
                    return
            except ValueError:
                show_snackbar(page, "La cantidad de listas debe ser un número entero válido.", is_error=True)
                return
            if not a_cargo_dropdown.value:
                show_snackbar(page, "Falta ingresar quién estuvo A Cargo de la Cía.", is_error=True)
                return
            if not tomo_lista_dropdown.value:
                show_snackbar(page, "Falta ingresar quién Tomó Lista.", is_error=True)
                return

            # Parsear fecha
            try:
                fecha_dt = datetime.datetime.strptime(fecha_input.value.strip(), "%d-%m-%Y").date()
                fecha_db_str = fecha_dt.isoformat()
            except ValueError:
                show_snackbar(page, "Formato de fecha inválido. Usar DD-MM-YYYY.", is_error=True)
                return

            # Construir objeto acto
            acto_data = {
                "corr_cia": int(corr_cia_input.value),
                "corr_general": int(corr_gen_input.value) if corr_gen_input.value else None,
                "fecha": fecha_db_str,
                "clave": clave_definitiva_dropdown.value,
                "direccion": direccion_input.value,
                "esquina": esquina_input.value.strip() if esquina_input.value else None,
                "tipo": tipo_dropdown.value,
                "a_cargo_cia": a_cargo_dropdown.value,
                "tomo_lista": tomo_lista_dropdown.value,
                "cantidad_listas": max_listas
            }
            
            # Construir lista de asistencia
            asistencias_list = []
            for reg, ctrls in asistencia_controls.items():
                cb = ctrls["checkbox"]
                txt = ctrls["listas"]
                if cb.value:
                    try:
                        listas = int(txt.value or 0)
                        if listas < 1 or listas > max_listas:
                            show_snackbar(
                                page, 
                                f"Las listas de {reg} deben estar entre 1 y {max_listas}.", 
                                is_error=True
                            )
                            return
                    except ValueError:
                        show_snackbar(
                            page, 
                            f"Las listas de {reg} deben ser un número válido.", 
                            is_error=True
                        )
                        return
                else:
                    listas = 0
                asistencias_list.append({
                    "reg_bombero": reg,
                    "cantidad_listas": listas
                })

            if is_edit:
                assert acto_id is not None
                success, msg = db_service.update_acto_completo(acto_id, acto_data, asistencias_list)
            else:
                success, msg = db_service.create_acto_completo(acto_data, asistencias_list)
                
            if success:
                show_snackbar(page, "Guardado correctamente.")
                dialog.open = False
                page.update()
                load_actos()
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

        # Pestañas del formulario (Datos vs Asistencia)
        datos_controls: list[ft.Control] = [
            ft.Row(controls=[corr_cia_input, corr_gen_input]),
            ft.Row(controls=[fecha_input, date_btn]),
            ft.Row(controls=[clave_categoria_dropdown, clave_definitiva_dropdown]),
            ft.Row(controls=[direccion_input, esquina_input]),
            ft.Row(controls=[tipo_dropdown, cant_listas_input]),
            ft.Row(controls=[a_cargo_dropdown]),
            ft.Row(controls=[tomo_lista_dropdown]),
        ]

        form_datos = ft.Container(
            content=ft.Column(
                controls=datos_controls,
                spacing=12,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=10
        )

        asistencia_panel_controls: list[ft.Control] = [
            check_all_cb,
            ft.Divider(color="#E4E4E7"),
            ft.Container(content=asistencia_list_view, height=300, expand=True)
        ]

        form_asistencias = ft.Container(
            content=ft.Column(
                controls=asistencia_panel_controls,
                spacing=5,
                expand=True
            ),
            padding=10,
            expand=True
        )

        tabs_form = ft.Tabs(
            length=2,
            selected_index=0,
            expand=True,
            height=400,
            width=500,
            content=ft.Column(
                expand=True,
                controls=[ # type: ignore
                    ft.TabBar(
                        tabs=[ # type: ignore
                            ft.Tab(label="Detalles del Acto", icon=ft.Icons.DESCRIPTION_ROUNDED),
                            ft.Tab(label= "Asistencia Personal", icon=ft.Icons.CHECKLIST_ROUNDED),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[ # type: ignore
                            form_datos,
                            form_asistencias,
                        ]
                    )
                ]
            )
        )

        dialog.content = tabs_form
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Cargar datos al renderizar inicialmente
    def on_init(e):
        load_actos()
        
    root_container.on_mount = on_init # type: ignore
    root_container.load_data = load_actos # type: ignore
    
    return root_container
