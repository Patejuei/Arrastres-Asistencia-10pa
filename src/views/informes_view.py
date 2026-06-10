import flet as ft
import datetime
from flet.controls.margin import Margin
from flet.controls.border import Border
from flet.controls.padding import Padding
from src.database.db_service import db_service
from src.components.dialogs import show_snackbar
from src.utils.excel_generator import (
    generate_arrastre_excel,
    generate_resumen_bombero_excel,
    generate_listado_bomberos_excel,
    generate_listado_licencias_excel
)

def create_informes_view(page: ft.Page) -> ft.Container:
    """Retorna el componente contenedor de la vista de Informes."""
    
    # Estado local
    bomberos_activos = []
    selected_report_type = "arrastre" # arrastre, resumen, bomberos, licencias

    # Componentes del formulario
    report_dropdown = ft.Dropdown(
        label="Seleccionar Tipo de Informe",
        options=[
            ft.dropdown.Option("arrastre", "Arrastre de Asistencia (General)"),
            ft.dropdown.Option("resumen", "Resumen de Asistencia (Individual)"),
            ft.dropdown.Option("bomberos", "Listado de Bomberos Registrados"),
            ft.dropdown.Option("licencias", "Listado de Licencias Registradas"),
        ],
        value="arrastre",
        width=400,
        on_select=lambda e: handle_report_type_change()
    )

    # --- CAMPOS ARRASTRE DE ASISTENCIA ---
    fecha_inicio_input = ft.TextField(
        label="Fecha Inicio (DD-MM-YYYY)",
        value=(datetime.date.today() - datetime.timedelta(days=30)).strftime("%d-%m-%Y"),
        expand=True
    )
    
    fecha_fin_input = ft.TextField(
        label="Fecha Fin (DD-MM-YYYY)",
        value=datetime.date.today().strftime("%d-%m-%Y"),
        expand=True
    )

    # DatePickers
    def handle_inicio_change(e):
        if picker_inicio.value:
            fecha_inicio_input.value = picker_inicio.value.strftime("%d-%m-%Y")
            fecha_inicio_input.update()

    def handle_fin_change(e):
        if picker_fin.value:
            fecha_fin_input.value = picker_fin.value.strftime("%d-%m-%Y")
            fecha_fin_input.update()

    picker_inicio = ft.DatePicker(on_change=handle_inicio_change)
    picker_fin = ft.DatePicker(on_change=handle_fin_change)
    page.overlay.extend([picker_inicio, picker_fin])

    def open_picker_inicio(e):
        picker_inicio.open = True
        page.update()

    def open_picker_fin(e):
        picker_fin.open = True
        page.update()

    btn_inicio = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_inicio)
    btn_fin = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH_ROUNDED, on_click=open_picker_fin)

    arrastre_controls: list[ft.Control] = [
        ft.Text("Definir Rango de Fechas", size=14, weight=ft.FontWeight.BOLD),
        ft.Row(controls=[fecha_inicio_input, btn_inicio]),
        ft.Row(controls=[fecha_fin_input, btn_fin]),
    ]

    arrastre_container = ft.Container(
        content=ft.Column(
            controls=arrastre_controls,
            spacing=10
        ),
        margin=Margin.only(bottom=15)
    )

    # --- CAMPOS RESUMEN DE ASISTENCIA ---
    bombero_dropdown = ft.Dropdown(
        label="Seleccionar Bombero",
        options=[],
        width=400
    )

    resumen_controls: list[ft.Control] = [
        ft.Text("Seleccionar el Personal", size=14, weight=ft.FontWeight.BOLD),
        bombero_dropdown,
    ]

    resumen_container = ft.Container(
        content=ft.Column(
            controls=resumen_controls,
            spacing=10
        ),
        margin=Margin.only(bottom=15),
        visible=False
    )

    # Info panel del reporte seleccionado
    info_text = ft.Text(
        "Este informe genera un documento de Excel consolidando todos los actos de servicio clasificados como 'Efectiva' sucedidos dentro del rango de fechas del personal de alta en la Cía. (descontando periodos de baja).",
        size=13,
        color="#52525B"
    )

    info_card = ft.Container(
        content=info_text,
        padding=15,
        bgcolor="#F4F4F5",
        border_radius=8,
        border=Border.all(width=1, color="#E4E4E7"),
        width=400,
        margin=Margin.only(bottom=20)
    )

    # ==========================================
    # FILE PICKER LOGIC (GUARDADO LOCAL)
    # ==========================================
    file_picker = ft.FilePicker()

    def reset_btn_state():
        generate_btn.disabled = False
        generate_btn.text = "Generar Informe en Excel" # type: ignore
        generate_btn.update()

    async def trigger_export(e):
        # Determinar el nombre de archivo sugerido según el reporte
        report_type = report_dropdown.value
        sugerido = "informe.xlsx"
        
        if report_type == "arrastre":
            sugerido = f"Arrastre_Asistencia_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        elif report_type == "resumen":
            if not bombero_dropdown.value:
                show_snackbar(page, "Seleccioná un bombero primero.", is_error=True)
                return
            sugerido = f"Resumen_Asistencia_{bombero_dropdown.value}_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        elif report_type == "bomberos":
            sugerido = f"Listado_Bomberos_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
        elif report_type == "licencias":
            sugerido = f"Listado_Licencias_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
            
        file_path = await file_picker.save_file(
            file_name=sugerido,
            allowed_extensions=["xlsx"]
        )

        if not file_path:
            return

        # Asegurarnos de que termine en .xlsx
        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"
            
        # Mostrar loading state
        generate_btn.disabled = True
        generate_btn.text = "Generando..." # type: ignore
        generate_btn.update()
        
        try:
            success = False
            msg = ""
            if report_type == "arrastre":
                # Validar fechas
                try:
                    f_ini_dt = datetime.datetime.strptime(fecha_inicio_input.value.strip(), "%d-%m-%Y").date()
                    f_fin_dt = datetime.datetime.strptime(fecha_fin_input.value.strip(), "%d-%m-%Y").date()
                    if f_ini_dt > f_fin_dt:
                        show_snackbar(page, "La fecha de inicio no puede ser posterior a la fecha fin.", is_error=True)
                        reset_btn_state()
                        return
                except ValueError:
                    show_snackbar(page, "Formato de fechas inválido. Usar DD-MM-YYYY.", is_error=True)
                    reset_btn_state()
                    return
                
                success, msg = generate_arrastre_excel(file_path, f_ini_dt.isoformat(), f_fin_dt.isoformat())
                
            elif report_type == "resumen":
                if not bombero_dropdown.value:
                    show_snackbar(page, "Falta seleccionar un bombero.", is_error=True)
                    reset_btn_state()
                    return
                success, msg = generate_resumen_bombero_excel(file_path, bombero_dropdown.value)
                
            elif report_type == "bomberos":
                success, msg = generate_listado_bomberos_excel(file_path)
                
            elif report_type == "licencias":
                success, msg = generate_listado_licencias_excel(file_path)
                
            if success:
                show_snackbar(page, f"¡Informe generado con éxito!\nGuardado en: {file_path}")
            else:
                show_snackbar(page, f"Error: {msg}", is_error=True)
        except Exception as ex:
            show_snackbar(page, f"Excepción al generar Excel: {ex}", is_error=True)
            
        reset_btn_state()


    generate_btn = ft.ElevatedButton(
        "Generar Informe en Excel", # type: ignore
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        style=ft.ButtonStyle(
            bgcolor="#D81E05",
            color="#FFFFFF",
            padding=Padding.symmetric(vertical=15, horizontal=25),
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=trigger_export,
        width=400,
        height=48
    )

    form_controls: list[ft.Control] = [
        report_dropdown,
        ft.Divider(color="#E4E4E7"),
        arrastre_container,
        resumen_container,
        info_card,
        generate_btn
    ]

    # Contenedor del formulario
    form_card = ft.Container(
        content=ft.Column(
            controls=form_controls,
            spacing=10,
            tight=True
        ),
        padding=30,
        border_radius=12,
        border=Border.all(width=1, color="#E4E4E7"),
        bgcolor="#FFFFFF",
        width=460
    )

    header_controls: list[ft.Control] = [
        ft.Text("Módulo de Informes", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
        ft.Text("Generar y descargar reportes oficiales en formato Excel (.xlsx)", size=13, color="#71717A")
    ]

    root_column_controls: list[ft.Control] = [
        # Header
        ft.Column(
            controls=header_controls,
            spacing=4
        ),
        ft.Container(height=15),
        form_card
    ]

    root_container = ft.Container(
        content=ft.Column(
            controls=root_column_controls,
            spacing=10,
            expand=True
        ),
        padding=30,
        expand=True
    )

    def handle_report_type_change():
        report_type = report_dropdown.value
        
        # Controlar visibilidad de contenedores
        arrastre_container.visible = (report_type == "arrastre")
        resumen_container.visible = (report_type == "resumen")
        
        # Actualizar info card
        if report_type == "arrastre":
            info_text.value = "Este informe genera un documento de Excel consolidando: Bombero, Universo de Efectivas, Total listas efectivas, Total listas abono. Muestra el porcentaje de asistencia de cada bombero en base a sus periodos de alta."
        elif report_type == "resumen":
            info_text.value = "Genera un libro de Excel de un bombero seleccionado. La primera hoja contiene su ficha personal con estadísticas totales. Las hojas siguientes corresponden a cada año del historial detallando los actos asistidos."
        elif report_type == "bomberos":
            info_text.value = "Genera una planilla con la nómina de todos los bomberos registrados en el sistema, mostrando Registro General, Nombre completo, RUT y Estado actual."
        elif report_type == "licencias":
            info_text.value = "Genera un listado de todas las licencias médicas y permisos históricos ingresados en el sistema, indicando bombero, motivo, rango de fechas y estado de aprobación."
            
        arrastre_container.update()
        resumen_container.update()
        info_card.update()

    def load_data():
        nonlocal bomberos_activos
        try:
            # Obtener bomberos para el selector de resumen
            bomberos_activos = db_service.get_bomberos()
            
            # Cargar dropdown de bomberos
            bombero_dropdown.options = [
                ft.dropdown.Option(b["registro_general"], f"{b['registro_general']} - {b['apellido_paterno']} {b['nombres']}")
                for b in bomberos_activos
            ]
            if bomberos_activos:
                bombero_dropdown.value = bomberos_activos[0]["registro_general"]
                
            bombero_dropdown.update()
        except Exception as ex:
            show_snackbar(page, f"Error al cargar bomberos para el selector: {ex}", is_error=True)

    def on_init(e):
        load_data()
        
    root_container.on_mount = on_init # type: ignore
    root_container.load_data = load_data # type: ignore
    
    return root_container
