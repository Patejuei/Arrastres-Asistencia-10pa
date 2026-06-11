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
    "10-12": "10-12 Apoyo a otros Cuerpos de Bomberos",
    "10-13": "10-13 Llamado a Atentado o Amenaza de Bomba",
    "10-14": "10-14 Caida de Avioneta",
    "10-15": "10-15 Simulacro o Ejercicio de Entrenamiento",
    "10-16": "10-16 Llamado a Tunel",
    "10-17": "10-17 Emergencia en Metro o Subte",
    "10-18": "10-18 Llamado a Emergencia Sector Limite"
}

# 2. Claves definitivas por categoría (Segundo selector y clave definitiva)
CLAVES_DEFINITIVAS = {
    "10-0": [
        ("10-0-1", "10-0-1 Estructural de 1 Piso"),
        ("10-0-2", "10-0-2 Estructural de 2 o más Pisos"),
        ("10-0-3", "10-0-3 Estructural Comercial Mayor o Industrial"),
        ("10-0-4", "10-0-4 Estructural en Campamento"),
        ("10-0-5", "10-0-5 Estructural con Materiales Peligrosos"),  # Nueva clave para estructuras con materiales peligrosos
        ("10-0-6", "10-0-6 Estructural en Subterraneo"),  
        ("10-0-7", "10-0-7 Estructural con Escasa Información"),  
        ("10-0-8", "10-0-8 Estructural de Material Ligero o Temporal"),  
        ("10-0-9", "10-0-9 Estructural Comercial Menor"),  
    ],
    "10-1": [
        ("10-1-1", "10-1-1 Vehículo"),
        ("10-1-2", "10-1-2 Vehículo con Materiales Peligrosos"),
        ("10-1-3", "10-1-3 Vehículo Eléctrico o Híbrido")
    ],
    "10-2": [
        ("10-2-1", "10-2-1 Pastizal Menor"),
        ("10-2-2", "10-2-2 Mediana o Gran Estensión de Pastizal"),
        ("10-2-3", "10-2-3 Incendio de Interfase")
    ],
    "10-3": [
        ("10-3-1", "10-3-1 Salvamento por Persona Encerrada o Atrapada"),
        ("10-3-2", "10-3-2 Salvamento por Extremidad Atrapada o Aplastada"),
        ("10-3-3", "10-3-3 Salvamento en Cerro, Zanja o Pozo"),
        ("10-3-4", "10-3-4 Salvamento por Encierro en Ascensor"),
        ("10-3-5", "10-3-5 Salvamento en Altura"),
        ("10-3-6", "10-3-6 Salvamento Vehicular Complejo (Múltiples lesionados/buses)"),
        ("10-3-7", "10-3-7 Salvamento Simple"),
        ("10-3-8", "10-3-8 Salvamento por Intento de Suicidio"),
        ("10-3-9", "10-3-9 Rescate Animal"),
        ("10-3-10", "10-3-10 Salvamento por PCR"),
        ("10-3-11", "10-3-11 Salvamento en Río o Cuerpo de Agua"),
    ],
    "10-4": [
        ("10-4-1", "10-4-1 Accidente Vehicular Simple"),
        ("10-4-2", "10-4-2 Accidente Vehicular Complejo (Múltiples lesionados/buses)"),
        ("10-4-3", "10-4-3 Accidente Vehicular de Alto Tonelaje o Desbarrancamiento"),
        ("10-4-4", "10-4-4 Accidente Vehicular en Carretera o Autopista"),
        ("10-4-5", "10-4-5 Accidente Vehicular con Presencia de Materiales Peligrosos"),
    ],
    "10-5": [
        ("10-5-1", "10-5-1 Incidente Hazmat en Vía Pública"),
        ("10-5-2", "10-5-2 Incidente Hazmat al Interior de Edificio o Industria"),
    ],
    "10-6": [
        ("10-6-1", "10-6-1 Fuga de Gas al Interior de Casa Habitación"),
        ("10-6-2", "10-6-2 Fuga de Gas en Edificio"),
        ("10-6-3", "10-6-3 Fuga de Gas en Industria o Comercio"),
        ("10-6-4", "10-6-4 Fuga de Gas en Vía Pública"),
        ("10-6-5", "10-6-5 Fuga de Gas con Personas Intoxicadas")
    ],
    "10-7": [
        ("10-7-1", "10-7-1 Emergencia Eléctrica"),
    ],
    "10-8": [
        ("10-8-1", "10-8-1 Emergencia no clasificada"),
        ("10-8-2", "10-8-2 Activación de Alarma por Fuego en Edificio o Casa Habitación"),
        ("10-8-3", "10-8-3 Fuego en Letrero o Poste"),
        ("10-8-4", "10-8-4 Fuego en Basura")
    ],
    "10-9": [
        ("10-9-6", "10-9-6 Resguardo de Evento o Manifestación"),
        ("10-9-8", "10-9-8 Otros Servicios")
    ],
    "10-10": [
        ("10-10-1", "10-10-1 Rebrote de Incendio Estructural"),
        ("10-10-2", "10-10-2 Rebrote de Incendio Forestal o Pastizal"),
    ],
    "10-11": [
        ("10-11-1", "10-11-1 Actividad institucional / Desfiles / Guardias")
    ],
    "10-12": [
        ("10-12", "10-12 Apoyo institucional a otros cuerpos de bomberos"),
        ("0-11", "0-11 Cubrir Cuartel de otro Cuerpo de Bomberos"),
    ],
    "10-13": [
        ("10-13", "10-13 Llamado a Atentado o Amenaza de Bomba")
    ],
    "10-14": [
        ("10-14", "10-14 Caida de Avioneta")
    ],
    "10-15": [
        ("10-15", "10-15 Simulacro o Ejercicio de Entrenamiento")
    ],
    "10-16": [
        ("10-16", "10-16 Llamado a Tunel")
    ],
    "10-17": [
        ("10-17", "10-17 Emergencia en Metro o Subte")
    ],
    "10-18": [
        ("10-18", "10-18 Llamado a Emergencia Sector Limite")
    ],
}
