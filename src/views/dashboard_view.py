import flet as ft
import datetime
import flet_charts as fch
from src.database.db_service import db_service
from src.components.stat_card import StatCard
from src.utils.date_helpers import get_bomberos_alertas

def create_dashboard_view(page: ft.Page) -> ft.Container:
    """Retorna el componente contenedor de la vista del Dashboard."""
    
    # Contenedores dinámicos
    stats_row = ft.Row(spacing=15)
    charts_and_lics_row = ft.Row(spacing=15)
    alerts_container = ft.Container(expand=True)
    
    main_column_controls: list[ft.Control] = [
        # Header
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Dashboard de Control", size=24, weight=ft.FontWeight.BOLD, color="#18181B"),
                        ft.Text(f"Resumen de asistencia y estados al {datetime.date.today().strftime('%d de %B, %Y')}", size=13, color="#71717A")
                    ],
                    spacing=4
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color="#D81E05",
                    tooltip="Actualizar Datos",
                    on_click=lambda e: load_dashboard_data()
                )
            ]
        ),
        ft.Container(height=10),
        stats_row,
        ft.Container(height=10),
        charts_and_lics_row,
        ft.Container(height=10),
        alerts_container
    ]

    main_column = ft.Column(
        controls=main_column_controls,
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    loading_indicator_controls: list[ft.Control] = [
        ft.ProgressRing(color="#D81E05"),
        ft.Text("Cargando estadísticas del cuartel...", color="#71717A", size=14)
    ]

    loading_indicator = ft.Container(
        content=ft.Column(
            controls=loading_indicator_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment.CENTER,
        expand=True
    )

    # Contenedor raíz
    root_container = ft.Container(
        content=loading_indicator,
        padding=30,
        expand=True
    )

    def load_dashboard_data():
        # Mostrar loading
        root_container.content = loading_indicator
        root_container.update()
        
        try:
            # 1. Consultar estadísticas de la base de datos
            cant_servicios = db_service.get_servicios_ultimo_mes()
            promedio_asis = db_service.get_promedio_asistencia_ultimo_mes()
            llamados_resumen = db_service.get_resumen_llamados_ultimo_mes()
            
            # 2. Calcular alertas de inactividad
            rojas, amarillas = get_bomberos_alertas()
            
            # 3. Obtener licencias activas al día de hoy
            hoy_str = datetime.date.today().isoformat()
            licencias_hoy = db_service.get_licencias_activas_en_fecha(hoy_str)
            
            # --- CONSTRUIR TARJETAS DE ESTADÍSTICAS ---
            stats_controls: list[ft.Control] = [ # type: ignore
                StatCard(
                    title="Servicios (Último Mes)",
                    value=str(cant_servicios),
                    icon=ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED,
                    color="#D81E05"
                ),
                StatCard(
                    title="Promedio Asistencia",
                    value=f"{promedio_asis} bomb.",
                    icon=ft.Icons.FACT_CHECK_ROUNDED,
                    color="#D81E05"
                ),
                StatCard(
                    title="Alertas Rojas (>=90 días)",
                    value=str(len(rojas)),
                    icon=ft.Icons.ERROR_OUTLINE_ROUNDED,
                    color="#FF4D4D",
                    alert_mode=len(rojas) > 0,
                    alert_color="#FF4D4D"
                ),
                StatCard(
                    title="Alertas Amarillas (>=30 días)",
                    value=str(len(amarillas)),
                    icon=ft.Icons.WARNING_AMBER_ROUNDED,
                    color="#FFAA00",
                    alert_mode=len(amarillas) > 0,
                    alert_color="#FFAA00"
                )
            ]
            stats_row.controls = stats_controls
            
            # --- CONSTRUIR GRÁFICO DE LLAMADOS ---
            pie_sections = []
            colors_palette = ["#D81E05", "#1E1E24", "#71717A", "#EF4444", "#F59E0B", "#10B981", "#3B82F6"]
            
            resumen_text_controls = []
            
            if llamados_resumen:
                for idx, (clave, conteo) in enumerate(llamados_resumen.items()):
                    color = colors_palette[idx % len(colors_palette)]
                    pie_sections.append(
                        fch.PieChartSection(
                            value=conteo,
                            title=str(conteo),
                            title_style=ft.TextStyle(size=12, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                            color=color,
                            radius=40
                        )
                    )
                    
                    # Leyenda
                    resumen_text_controls.append(
                        ft.Row(
                            controls=[
                                ft.Container(width=12, height=12, bgcolor=color, border_radius=3),
                                ft.Text(f"{clave}: {conteo} llamado(s)", size=12, color="#3F3F46")
                            ],
                            spacing=8
                        )
                    )
            else:
                # Si no hay llamados
                pie_sections.append(
                    fch.PieChartSection(
                        value=1,
                        title="0",
                        color="#E4E4E7",
                        radius=40
                    )
                )
                resumen_text_controls.append(
                    ft.Text("Sin llamados en los últimos 30 días.", italic=True, size=12, color="#71717A")
                )

            chart_card = ft.Container(
                content=ft.Column(
                    controls=[ # type: ignore
                        ft.Text("Tipos de Llamados (Último Mes)", size=15, weight=ft.FontWeight.BOLD, color="#18181B"),
                        ft.Divider(color="#E4E4E7"),
                        ft.Row(
                            controls=[ # type: ignore
                                ft.Container(
                                    content=fch.PieChart(
                                        sections=pie_sections,
                                        sections_space=2,
                                        center_space_radius=30,
                                        expand=True
                                    ),
                                    width=120,
                                    height=120
                                ),
                                ft.Column(
                                    controls=resumen_text_controls,
                                    spacing=5,
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        )
                    ],
                    spacing=10
                ),
                padding=20,
                border_radius=12,
                border=ft.Border.all(width=1, color="#E4E4E7"),
                bgcolor="#FFFFFF",
                expand=True
            )
            
            # --- CONSTRUIR CONTENEDOR DE LICENCIAS ACTIVAS ---
            lics_list_views = []
            if licencias_hoy:
                for lic in licencias_hoy:
                    b_info = lic.get("bomberos") or {}
                    nombre_b = f"{b_info.get('nombres', '')} {b_info.get('apellido_paterno', '')}"
                    f_hasta_parsed = datetime.datetime.strptime(lic["fecha_hasta"][:10], "%Y-%m-%d").strftime("%d-%m-%Y")
                    
                    lics_list_views.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CARD_MEMBERSHIP_ROUNDED, color="#D81E05", size=18),
                                    ft.Column(
                                        controls=[
                                            ft.Text(nombre_b, size=12, weight=ft.FontWeight.BOLD, color="#18181B"),
                                            ft.Text(f"Hasta: {f_hasta_parsed} | {lic['motivo']}", size=11, color="#71717A")
                                        ],
                                        spacing=2
                                    )
                                ],
                                spacing=10
                            ),
                            padding=8,
                            bgcolor="#F8FAFC",
                            border_radius=6,
                            border=ft.Border.all(width=1, color="#F1F5F9")
                        )
                    )
            else:
                lics_list_views.append(
                    ft.Container(
                        content=ft.Text("No hay licencias activas el día de hoy.", italic=True, size=12, color="#71717A"),
                        padding=15,
                        alignment=ft.alignment.Alignment(0, 0)
                    )
                )

            lics_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Licencias Activas Hoy", size=15, weight=ft.FontWeight.BOLD, color="#18181B"),
                        ft.Divider(color="#E4E4E7"),
                        ft.Column(
                            controls=lics_list_views,
                            spacing=8,
                            scroll=ft.ScrollMode.AUTO,
                            height=120
                        )
                    ],
                    spacing=10
                ),
                padding=20,
                border_radius=12,
                border=ft.Border.all(width=1, color="#E4E4E7"),
                bgcolor="#FFFFFF",
                expand=True
            )
            
            charts_and_lics_row.controls = [chart_card, lics_card]
            
            # --- CONSTRUIR SECCIÓN DE ALERTAS (DETALLE) ---
            def make_alert_tile(b_info, alert_color):
                # Genera una fila para la lista de alertas
                return ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(b_info["registro_general"], weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(b_info["nombre_completo"])),
                        ft.DataCell(ft.Text(b_info["ultima_asistencia"])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(f"{b_info['dias_inactividad']} días", color="#FFFFFF", size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=alert_color,
                                padding=ft.Padding.symmetric(vertical=4, horizontal=8),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Text(f"- {b_info['dias_licencia_descontados']} días" if b_info['dias_licencia_descontados'] > 0 else "Sin licencias")),
                    ]
                )

            rojas_rows = [make_alert_tile(b, "#FF4D4D") for b in rojas]
            amarillas_rows = [make_alert_tile(b, "#FFAA00") for b in amarillas]

            rojas_table = ft.DataTable(
                columns=[
                    ft.DataColumn(label=ft.Text("Reg. Gral.")),
                    ft.DataColumn(label=ft.Text("Bombero")),
                    ft.DataColumn(label=ft.Text("Última Lista")),
                    ft.DataColumn(label=ft.Text("Inactividad")),
                    ft.DataColumn(label=ft.Text("Descuento Licencia")),
                ],
                rows=rojas_rows,
                heading_row_color="#F8FAFC",
                divider_thickness=1,
                expand=True
            )

            amarillas_table = ft.DataTable(
                columns=[
                    ft.DataColumn(label=ft.Text("Reg. Gral.")),
                    ft.DataColumn(label=ft.Text("Bombero")),
                    ft.DataColumn(label=ft.Text("Última Lista")),
                    ft.DataColumn(label=ft.Text("Inactividad")),
                    ft.DataColumn(label=ft.Text("Descuento Licencia")),
                ],
                rows=amarillas_rows,
                heading_row_color="#F8FAFC",
                divider_thickness=1,
                expand=True
            )

            red_tab_controls: list[ft.Control] = [ # type: ignore
                ft.Container(height=5),
                ft.Column(controls=[rojas_table], scroll=ft.ScrollMode.AUTO, expand=True) if rojas_rows else 
                ft.Container(content=ft.Text("No hay bomberos en alerta roja. ¡Excelente!", italic=True, color="#71717A"), padding=30, alignment=ft.alignment.Alignment(0, 0))
            ]

            yellow_tab_controls: list[ft.Control] = [ # type: ignore
                ft.Container(height=5),
                ft.Column(controls=[amarillas_table], scroll=ft.ScrollMode.AUTO, expand=True) if amarillas_rows else
                ft.Container(content=ft.Text("No hay bomberos en alerta amarilla.", italic=True, color="#71717A"), padding=30, alignment=ft.alignment.Alignment(0, 0))
            ]

            # Tabulador de Alertas
            tabs = ft.Tabs(
                length=2,
                selected_index=0,
                animation_duration=300,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.TabBar(
                            tabs=[
                                ft.Tab(label=f"Críticos - Alerta Roja ({len(rojas)})", icon=ft.Icons.DANGEROUS_ROUNDED),
                                ft.Tab(label=f"Advertencias - Alerta Amarilla ({len(amarillas)})", icon=ft.Icons.WARNING_ROUNDED)
                            ]
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                ft.Container(
                                    content=ft.Column(controls=red_tab_controls, expand=True),
                                    padding=10,
                                    expand=True
                                ),
                                ft.Container(
                                    content=ft.Column(controls=yellow_tab_controls, expand=True),
                                    padding=10,
                                    expand=True
                                )
                            ]
                        )
                    ]
                )
            )

            alerts_card_controls: list[ft.Control] = [
                ft.Text("Detalle de Alertas por Inasistencia", size=15, weight=ft.FontWeight.BOLD, color="#18181B"),
                ft.Text("Descuenta automáticamente los días de licencias y permisos aprobados en el sistema.", size=12, color="#71717A"),
                ft.Divider(color="#E4E4E7"),
                tabs
            ]

            alerts_card = ft.Container(
                content=ft.Column(
                    controls=alerts_card_controls,
                    spacing=5,
                    expand=True
                ),
                padding=20,
                border_radius=12,
                border=ft.Border.all(width=1, color="#E4E4E7"),
                bgcolor="#FFFFFF",
                expand=True,
                height=350
            )
            
            alerts_container.content = alerts_card
            
            # Restaurar vista principal
            root_container.content = main_column
            
        except Exception as e:
            error_card_controls: list[ft.Control] = [ # type: ignore
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color="#FF4D4D", size=48),
                ft.Text("Error al cargar la información del Dashboard", weight=ft.FontWeight.BOLD, size=16),
                ft.Text(str(e), color="#71717A", text_align=ft.TextAlign.CENTER),
                ft.ElevatedButton("Reintentar", on_click=lambda e: load_dashboard_data(), style=ft.ButtonStyle(bgcolor="#D81E05", color="#FFFFFF")) # type: ignore
            ]

            root_container.content = ft.Container(
                content=ft.Column(
                    controls=error_card_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.Alignment.CENTER,
                expand=True
            )
            
        root_container.update()

    # Cargar datos al renderizar inicialmente
    # Flet ejecuta después de que el elemento se añade a la página.
    # Usamos un timer o trigger diferido en Flet para evitar bloquear el hilo del UI.
    def on_init(e):
        load_dashboard_data()
        
    root_container.on_mount = on_init # type: ignore
    root_container.load_data = load_dashboard_data # type: ignore
    
    return root_container
