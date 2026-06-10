import re

def clean_rut(rut: str) -> str:
    """Remueve todos los caracteres no alfanuméricos del RUT."""
    if not rut:
        return ""
    return re.sub(r"[^0-9kK]", "", rut)

def format_rut(rut: str) -> str:
    """Formatea un RUT limpio en formato estándar chileno (XX.XXX.XXX-X)."""
    cleaned = clean_rut(rut)
    if not cleaned:
        return ""
    
    if len(cleaned) < 2:
        return cleaned
        
    cuerpo = cleaned[:-1]
    dv = cleaned[-1].upper()
    
    # Formatear el cuerpo con miles
    cuerpo_formateado = []
    for i, char in enumerate(reversed(cuerpo)):
        if i > 0 and i % 3 == 0:
            cuerpo_formateado.append(".")
        cuerpo_formateado.append(char)
        
    return "".join(reversed(cuerpo_formateado)) + "-" + dv

def validate_rut(rut: str) -> bool:
    """
    Valida un RUT chileno usando el algoritmo módulo 11.
    Retorna True si es válido, False de lo contrario.
    """
    cleaned = clean_rut(rut)
    if len(cleaned) < 8 or len(cleaned) > 9:
        return False
        
    cuerpo = cleaned[:-1]
    dv = cleaned[-1].upper()
    
    if not cuerpo.isdigit():
        return False
        
    # Algoritmo de validación del RUT (Módulo 11)
    suma = 0
    multiplo = 2
    for char in reversed(cuerpo):
        suma += int(char) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
            
    dv_esperado = 11 - (suma % 11)
    if dv_esperado == 11:
        dv_esperado_str = "0"
    elif dv_esperado == 10:
        dv_esperado_str = "K"
    else:
        dv_esperado_str = str(dv_esperado)
        
    return dv == dv_esperado_str
