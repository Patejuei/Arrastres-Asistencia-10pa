# Configuración de Claves de Despacho del Cuerpo de Bomberos
# Modificá este archivo para personalizar las claves del sistema.

# 1. Categorías principales (Filtro inicial)
CLAVES_DESPACHO = {
    "10-0": "10-0 Estructural (Estructuras, casas, edificios)",
    "10-1": "10-1 Vehículos (Autos, camiones, buses)",
    "10-2": "10-2 Pastizales y/o Basura (Forestal, vertederos)",
    "10-3": "10-3 Rescate Vehicular (Accidentes de tránsito)",
    "10-4": "10-4 Rescate de Personas (Ascensores, pozos, derrumbes)",
    "10-5": "10-5 Materias Peligrosas (Químicos, Hazmat)",
    "10-6": "10-6 Escape de Gas (U otros hidrocarburos)",
    "10-7": "10-7 Llamado Eléctrico (Postes, transformadores)",
    "10-8": "10-8 Llamado No Clasificado (Inundaciones, caídas)",
    "10-9": "10-9 Servicios Especiales (Apoyo instituciones)",
    "10-10": "10-10 Escombros (Derrumbes sin personas)",
    "10-11": "10-11 Comandancia (Desfiles, ceremonias, guardias)",
    "10-12": "10-12 Apoyo a otros Cuerpos de Bomberos"
}

# 2. Claves definitivas por categoría (Segundo selector y clave definitiva)
CLAVES_DEFINITIVAS = {
    "10-0": [
        ("10-0-1", "10-0-1 Estructural Menor (Casas, habitaciones)"),
        ("10-0-2", "10-0-2 Estructural Mediano (Comercios, talleres)"),
        ("10-0-3", "10-0-3 Estructural Mayor (Edificios, industrias)")
    ],
    "10-1": [
        ("10-1-1", "10-1-1 Vehículo Menor (Sedán, SUV, moto)"),
        ("10-1-2", "10-1-2 Vehículo Mayor (Camiones, buses)"),
        ("10-1-3", "10-1-3 Vehículo de Carga / Maquinaria")
    ],
    "10-2": [
        ("10-2-1", "10-2-1 Pastizal Menor / Basura"),
        ("10-2-2", "10-2-2 Incendio Forestal / Interface"),
        ("10-2-3", "10-2-3 Vertedero / Microbasural")
    ],
    "10-3": [
        ("10-3-1", "10-3-1 Colisión Menor (Choques sin atrapados)"),
        ("10-3-2", "10-3-2 Rescate Vehicular Mediano (Con atrapados)"),
        ("10-3-3", "10-3-3 Rescate Vehicular Complejo (Múltiples lesionados/buses)")
    ],
    "10-4": [
        ("10-4-1", "10-4-1 Rescate de personas en ascensores"),
        ("10-4-2", "10-4-2 Rescate en pozos o cámaras de alcantarillado"),
        ("10-4-3", "10-4-3 Rescate por derrumbes o estructuras colapsadas")
    ],
    "10-5": [
        ("10-5-1", "10-5-1 Incidente Hazmat Menor (Derrame doméstico)"),
        ("10-5-2", "10-5-2 Incidente Hazmat Mayor (Carretera/Industria)"),
        ("10-5-3", "10-5-3 Emergencia de gases tóxicos o químicos reactivos")
    ],
    "10-6": [
        ("10-6-1", "10-6-1 Escape en cilindros de gas licuado"),
        ("10-6-2", "10-6-2 Escape en instalaciones domiciliarias/red de gas"),
        ("10-6-3", "10-6-3 Escape en vía pública o industrias")
    ],
    "10-7": [
        ("10-7-1", "10-7-1 Emergencia eléctrica domiciliaria"),
        ("10-7-2", "10-7-2 Emergencia en postes y transformadores aéreos"),
        ("10-7-3", "10-7-3 Emergencia en subestaciones o líneas de alta tensión")
    ],
    "10-8": [
        ("10-8-1", "10-8-1 Emergencia no clasificada")
    ],
    "10-9": [
        ("10-9-1", "10-9-1 Servicios especiales de apoyo civil"),
        ("10-9-2", "10-9-2 Servicios de abastecimiento de agua")
    ],
    "10-10": [
        ("10-10-1", "10-10-1 Remoción de escombros post-siniestro")
    ],
    "10-11": [
        ("10-11-1", "10-11-1 Actividad institucional / Desfiles / Guardias")
    ],
    "10-12": [
        ("10-12-1", "10-12-1 Apoyo institucional a otros cuerpos de bomberos")
    ]
}
