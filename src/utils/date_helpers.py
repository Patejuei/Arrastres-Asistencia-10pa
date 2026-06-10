import datetime
from src.database.db_service import db_service

def parse_date(date_val) -> datetime.date:
    """Parsea un valor de fecha a objeto datetime.date."""
    if isinstance(date_val, datetime.date):
        return date_val
    if isinstance(date_val, datetime.datetime):
        return date_val.date()
    if isinstance(date_val, str):
        # Intentar parsear YYYY-MM-DD
        try:
            return datetime.datetime.strptime(date_val[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    return datetime.date.today()

def calculate_overlap_days(lic_desde: datetime.date, lic_hasta: datetime.date, ref_desde: datetime.date, ref_hasta: datetime.date) -> int:
    """Calcula cuántos días de una licencia se superponen con un período de inactividad de referencia."""
    start_intersection = max(lic_desde, ref_desde)
    end_intersection = min(lic_hasta, ref_hasta)
    
    if start_intersection <= end_intersection:
        return (end_intersection - start_intersection).days + 1
    return 0

def get_bomberos_alertas() -> tuple[list[dict], list[dict]]:
    """
    Calcula los bomberos activos que se encuentran en alerta amarilla (>= 30 días) o roja (>= 90 días)
    de inactividad no justificada (descontando licencias aprobadas).
    Retorna (alertas_rojas, alertas_amarillas).
    """
    # 1. Obtener todos los bomberos activos
    bomberos = db_service.get_bomberos_activos()
    if not bomberos:
        return [], []

    # 2. Obtener licencias y asistencias en bloque para evitar consultas en bucle N+1
    # Obtener todas las licencias
    licencias_raw = db_service.get_licencias()
    licencias_aprobadas = [l for l in licencias_raw if l.get("aprobado", False)]
    
    # Obtener asistencias
    asistencias = db_service.get_todas_asistencias_bomberos()
    
    # Mapear asistencias por bombero
    asis_por_bombero = {}
    for asis in asistencias:
        reg = asis.get("reg_bombero")
        # El objeto actos_servicio contiene la fecha del acto
        acto = asis.get("actos_servicio")
        if acto and acto.get("fecha"):
            fecha_acto = parse_date(acto["fecha"])
            if reg not in asis_por_bombero:
                asis_por_bombero[reg] = []
            asis_por_bombero[reg].append(fecha_acto)
            
    # Ordenar las fechas de asistencia de cada bombero (más reciente al final)
    for reg in asis_por_bombero:
        asis_por_bombero[reg].sort()

    hoy = datetime.date.today()
    alertas_rojas = []
    alertas_amarillas = []

    for bombero in bomberos:
        reg = bombero["registro_general"]
        nombre_completo = f"{bombero['nombres']} {bombero['apellido_paterno']} {bombero['apellido_materno']}"
        
        # A. Determinar fecha de última asistencia o en su defecto fecha de ingreso
        fecha_referencia = None
        
        if reg in asis_por_bombero and asis_por_bombero[reg]:
            # Su última asistencia registrada con cantidad_listas > 0
            fecha_referencia = asis_por_bombero[reg][-1]
        else:
            # Si no tiene asistencias, buscar movimientos para ver su ingreso más reciente
            movs = db_service.get_movimientos_by_bombero(reg)
            if movs:
                # El más reciente ingreso
                fecha_referencia = parse_date(movs[0]["fecha_ingreso"])
            else:
                # Si no tiene nada, asumimos que no tiene inactividad acumulada
                fecha_referencia = hoy

        if fecha_referencia > hoy:
            # Por consistencia si hay fechas futuras
            fecha_referencia = hoy

        # B. Calcular días transcurridos
        dias_transcurridos = (hoy - fecha_referencia).days
        
        if dias_transcurridos < 30:
            # Si lleva menos de 30 días, no hay alerta de ningún tipo
            continue

        # C. Buscar licencias del bombero que se superpongan con [fecha_referencia, hoy]
        dias_licencia = 0
        licencias_bombero = [l for l in licencias_aprobadas if l.get("reg_bombero") == reg]
        
        for lic in licencias_bombero:
            l_desde = parse_date(lic["fecha_desde"])
            l_hasta = parse_date(lic["fecha_hasta"])
            
            dias_licencia += calculate_overlap_days(l_desde, l_hasta, fecha_referencia, hoy)

        # D. Calcular días netos de inactividad
        dias_inactividad_neta = max(0, dias_transcurridos - dias_licencia)
        
        # E. Clasificar en alertas
        bombero_info = {
            "registro_general": reg,
            "nombres": bombero["nombres"],
            "apellido_paterno": bombero["apellido_paterno"],
            "apellido_materno": bombero["apellido_materno"],
            "nombre_completo": nombre_completo,
            "ultima_asistencia": fecha_referencia.strftime("%d-%m-%Y") if reg in asis_por_bombero and asis_por_bombero[reg] else "Sin asistencias (Fecha de ingreso)",
            "dias_inactividad": dias_inactividad_neta,
            "dias_licencia_descontados": dias_licencia
        }

        if dias_inactividad_neta >= 90:
            alertas_rojas.append(bombero_info)
        elif dias_inactividad_neta >= 30:
            alertas_amarillas.append(bombero_info)

    # Ordenar alertas por días de inactividad descendente
    alertas_rojas.sort(key=lambda x: x["dias_inactividad"], reverse=True)
    alertas_amarillas.sort(key=lambda x: x["dias_inactividad"], reverse=True)

    return alertas_rojas, alertas_amarillas
