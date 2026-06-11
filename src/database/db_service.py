from typing import Any, cast
from postgrest.types import CountMethod
from src.config.supabase_client import get_supabase_client, is_configured

class DBService:
    def _get_supabase(self):
        if not is_configured():
            raise ValueError("La base de datos de Supabase no está configurada. Verificá el archivo .env.")
        return get_supabase_client()

    # ==========================================
    # BOMBEROS
    # ==========================================

    def get_bomberos(self) -> list[dict[str, Any]]:
        """Obtiene la lista de bomberos ordenados por apellido paterno y nombres."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("bomberos").select("*").order("apellido_paterno").order("nombres").execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener bomberos: {e}")
            return []

    def get_bomberos_activos(self) -> list[dict[str, Any]]:
        """Obtiene la lista de bomberos que están activos en el sistema."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("bomberos").select("*").eq("estado", "Activo").order("apellido_paterno").execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener bomberos activos: {e}")
            return []

    def get_bombero(self, registro_general: str) -> dict[str, Any] | None:
        """Obtiene un bombero específico por su registro general."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("bomberos").select("*").eq("registro_general", registro_general).execute()
            return cast(dict[str, Any], res.data[0]) if res.data else None
        except Exception as e:
            print(f"Error al obtener bombero {registro_general}: {e}")
            return None

    def create_bombero(self, data: dict) -> tuple[bool, str]:
        """Crea un nuevo bombero en el sistema."""
        try:
            supabase = self._get_supabase()
            supabase.table("bomberos").insert(data).execute()
            return True, "Bombero registrado exitosamente."
        except Exception as e:
            err_msg = str(e)
            if "duplicate key" in err_msg:
                return False, f"El Registro General '{data.get('registro_general')}' ya existe."
            if "bomberos_rut_key" in err_msg:
                return False, f"El RUT '{data.get('rut')}' ya está registrado."
            return False, f"Error al crear bombero: {err_msg}"

    def update_bombero(self, registro_general: str, data: dict) -> tuple[bool, str]:
        """Actualiza la información de un bombero."""
        try:
            supabase = self._get_supabase()
            supabase.table("bomberos").update(data).eq("registro_general", registro_general).execute()
            return True, "Bombero actualizado exitosamente."
        except Exception as e:
            err_msg = str(e)
            if "bomberos_rut_key" in err_msg:
                return False, f"El RUT '{data.get('rut')}' ya pertenece a otro bombero."
            return False, f"Error al actualizar bombero: {err_msg}"

    # ==========================================
    # MOVIMIENTOS DEL PERSONAL
    # ==========================================

    def get_movimientos_by_bombero(self, reg_bombero: str) -> list[dict[str, Any]]:
        """Obtiene el historial de movimientos de un bombero ordenado por fecha de ingreso descendente."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("movimientos_personal").select("*").eq("reg_bombero", reg_bombero).order("fecha_ingreso", desc=True).execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener movimientos del bombero {reg_bombero}: {e}")
            return []

    def create_movimiento(self, data: dict) -> tuple[bool, str]:
        """Crea un nuevo movimiento de personal."""
        try:
            supabase = self._get_supabase()
            supabase.table("movimientos_personal").insert(data).execute()
            return True, "Movimiento de personal registrado exitosamente."
        except Exception as e:
            return False, f"Error al registrar movimiento: {str(e)}"

    def update_movimiento(self, movimiento_id: int, data: dict) -> tuple[bool, str]:
        """Actualiza un movimiento de personal existente."""
        try:
            supabase = self._get_supabase()
            supabase.table("movimientos_personal").update(data).eq("id", movimiento_id).execute()
            return True, "Movimiento de personal actualizado exitosamente."
        except Exception as e:
            return False, f"Error al actualizar movimiento: {str(e)}"

    def delete_movimiento(self, movimiento_id: int) -> tuple[bool, str]:
        """Elimina un movimiento de personal."""
        try:
            supabase = self._get_supabase()
            supabase.table("movimientos_personal").delete().eq("id", movimiento_id).execute()
            return True, "Movimiento eliminado exitosamente."
        except Exception as e:
            return False, f"Error al eliminar movimiento: {str(e)}"

    # ==========================================
    # LICENCIAS
    # ==========================================

    def get_licencias(self) -> list[dict[str, Any]]:
        """Obtiene todas las licencias ordenadas por fecha desde descendente, incluyendo info del bombero."""
        try:
            supabase = self._get_supabase()
            # Hacer join con bomberos para obtener nombres
            res = supabase.table("licencias").select("*, bomberos(nombres, apellido_paterno, apellido_materno)").order("fecha_desde", desc=True).execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener licencias: {e}")
            return []

    def get_licencias_activas_en_fecha(self, fecha: str) -> list[dict[str, Any]]:
        """Obtiene las licencias que están vigentes en una fecha dada."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("licencias").select("*, bomberos(nombres, apellido_paterno)").lte("fecha_desde", fecha).gte("fecha_hasta", fecha).eq("aprobado", True).execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener licencias activas: {e}")
            return []

    def get_licencias_by_bombero(self, reg_bombero: str) -> list[dict[str, Any]]:
        """Obtiene todas las licencias de un bombero en particular."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("licencias").select("*").eq("reg_bombero", reg_bombero).order("fecha_desde", desc=True).execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener licencias del bombero {reg_bombero}: {e}")
            return []

    def create_licencia(self, data: dict) -> tuple[bool, str]:
        """Crea una nueva licencia de inasistencia."""
        try:
            supabase = self._get_supabase()
            supabase.table("licencias").insert(data).execute()
            return True, "Licencia registrada exitosamente."
        except Exception as e:
            return False, f"Error al registrar licencia: {str(e)}"

    def update_licencia(self, licencia_id: int, data: dict) -> tuple[bool, str]:
        """Actualiza una licencia existente."""
        try:
            supabase = self._get_supabase()
            supabase.table("licencias").update(data).eq("id", licencia_id).execute()
            return True, "Licencia actualizada exitosamente."
        except Exception as e:
            return False, f"Error al actualizar licencia: {str(e)}"

    def delete_licencia(self, licencia_id: int) -> tuple[bool, str]:
        """Elimina una licencia."""
        try:
            supabase = self._get_supabase()
            supabase.table("licencias").delete().eq("id", licencia_id).execute()
            return True, "Licencia eliminada exitosamente."
        except Exception as e:
            return False, f"Error al eliminar licencia: {str(e)}"

    # ==========================================
    # ACTOS DE SERVICIO Y ASISTENCIAS
    # ==========================================

    def get_actos(self, mes: int | None = None, anio: int | None = None, clave: str | None = None, query: str | None = None) -> list[dict[str, Any]]:
        """
        Obtiene el listado de actos de servicio aplicando filtros opcionales.
        Buscador (query) busca por fecha (YYYY-MM-DD), dirección o correlativo general.
        """
        try:
            supabase = self._get_supabase()
            # Seleccionar el acto y traer los nombres del bombero a cargo
            select_query = "*, a_cargo:bomberos!actos_servicio_a_cargo_cia_fkey(nombres, apellido_paterno)"
            builder = supabase.table("actos_servicio").select(select_query)
            
            if mes:
                # Filtrar por mes. En postgrest podemos usar filtros de cadena sobre la fecha
                # O filtrar en memoria. Dado que la base de datos puede crecer, intentaremos filtrar
                # usando operadores de fecha de postgres si es posible, o en memoria si es más seguro.
                # Para mayor robustez y compatibilidad con postgrest:
                # Usaremos gte y lte.
                if anio:
                    import calendar
                    ultimo_dia = calendar.monthrange(anio, mes)[1]
                    fecha_inicio = f"{anio}-{mes:02d}-01"
                    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia:02d}"
                    builder = builder.gte("fecha", fecha_inicio).lte("fecha", fecha_fin)
            
            if clave:
                builder = builder.eq("clave", clave)
                
            res = builder.order("fecha", desc=True).order("corr_cia", desc=True).execute()
            data = cast(list[dict[str, Any]], res.data or [])

            # Si hay un buscador textual (query)
            if query:
                q = query.lower().strip()
                filtered: list[dict[str, Any]] = []
                for acto in data:
                    fecha_str = str(acto.get("fecha", ""))
                    direccion = str(acto.get("direccion", "")).lower()
                    esquina = str(acto.get("esquina", "") or "").lower()
                    corr_gen = str(acto.get("corr_general", "") or "")
                    corr_cia = str(acto.get("corr_cia", ""))
                    clave_acto = str(acto.get("clave", "")).lower()
                    
                    if (q in fecha_str or 
                        q in direccion or 
                        q in esquina or
                        q in corr_gen or 
                        q in corr_cia or
                        q in clave_acto):
                        filtered.append(acto)
                return filtered
                
            return data
        except Exception as e:
            print(f"Error al obtener actos de servicio: {e}")
            return []

    def get_acto_detalles(self, id_acto: int) -> dict[str, Any] | None:
        """Obtiene un acto de servicio completo con su lista de asistencias."""
        try:
            supabase = self._get_supabase()
            # Traer el acto
            res_acto = supabase.table("actos_servicio").select("*, a_cargo:bomberos!actos_servicio_a_cargo_cia_fkey(registro_general, nombres, apellido_paterno), tomo_lista:bomberos!actos_servicio_tomo_lista_fkey(registro_general, nombres, apellido_paterno)").eq("id", id_acto).execute()
            if not res_acto.data:
                return None
                
            acto = cast(dict[str, Any], res_acto.data[0])
            
            # Traer asistencias asociadas, uniendo con bombero para mostrar sus nombres en el listado
            res_asistencias = supabase.table("asistencias").select("*, bomberos(registro_general, nombres, apellido_paterno, apellido_materno)").eq("id_acto", id_acto).execute()
            acto["asistencias"] = res_asistencias.data or []
            
            return acto
        except Exception as e:
            print(f"Error al obtener detalles de acto {id_acto}: {e}")
            return None

    def create_acto_completo(self, acto_data: dict, asistencias_list: list[dict]) -> tuple[bool, str]:
        """
        Registra un acto de servicio e inserta sus asistencias asociadas.
        Calcula el total de asistencia sumando los bomberos que registran cantidad_listas > 0.
        """
        try:
            supabase = self._get_supabase()
            
            # 1. Calcular total_asistencia en base a asistencias con listas > 0
            # (generalmente cada bombero que asiste suma 1 o la cantidad que tenga)
            total_asistieron = sum(1 for a in asistencias_list if a.get("cantidad_listas", 0) > 0)
            acto_data["total_asistencia"] = total_asistieron
            
            # 2. Insertar acto de servicio
            res_acto = supabase.table("actos_servicio").insert(acto_data).execute()
            if not res_acto.data:
                return False, "No se pudo crear el acto de servicio."
            
            acto_id = cast(dict[str, Any], res_acto.data[0])["id"]
            
            # 3. Preparar e insertar asistencias
            asistencias_insert = []
            for asis in asistencias_list:
                # Solo guardamos asistencias si corresponden a bomberos que asistieron (cantidad_listas >= 0)
                # Guardar todos los bomberos mapeados es útil para saber quién no fue,
                # pero en base de datos basta con guardar los que tienen cantidad_listas > 0
                # para ahorrar espacio, o guardarlos a todos. Guardaremos los que tienen listas > 0.
                if asis.get("cantidad_listas", 0) > 0:
                    asistencias_insert.append({
                        "id_acto": acto_id,
                        "reg_bombero": asis["reg_bombero"],
                        "cantidad_listas": asis["cantidad_listas"]
                    })
                    
            if asistencias_insert:
                supabase.table("asistencias").insert(asistencias_insert).execute()
                
            return True, "Acto de servicio y asistencia guardados exitosamente."
        except Exception as e:
            return False, f"Error al crear acto completo: {str(e)}"

    def update_acto_completo(self, id_acto: int, acto_data: dict, asistencias_list: list[dict]) -> tuple[bool, str]:
        """
        Actualiza los datos de un acto de servicio y sus asistencias asociadas.
        Calcula el total de asistencia y sincroniza la tabla 'asistencias'.
        """
        try:
            supabase = self._get_supabase()
            
            # 1. Calcular total_asistencia en base a asistencias con listas > 0
            total_asistieron = sum(1 for a in asistencias_list if a.get("cantidad_listas", 0) > 0)
            acto_data["total_asistencia"] = total_asistieron
            
            # 2. Actualizar acto de servicio
            supabase.table("actos_servicio").update(acto_data).eq("id", id_acto).execute()
            
            # 3. Eliminar asistencias anteriores del acto
            supabase.table("asistencias").delete().eq("id_acto", id_acto).execute()
            
            # 4. Insertar las nuevas asistencias (con cantidad_listas > 0)
            asistencias_insert = []
            for asis in asistencias_list:
                if asis.get("cantidad_listas", 0) > 0:
                    asistencias_insert.append({
                        "id_acto": id_acto,
                        "reg_bombero": asis["reg_bombero"],
                        "cantidad_listas": asis["cantidad_listas"]
                    })
                    
            if asistencias_insert:
                supabase.table("asistencias").insert(asistencias_insert).execute()
                
            return True, "Acto de servicio y asistencia actualizados exitosamente."
        except Exception as e:
            return False, f"Error al actualizar acto completo: {str(e)}"

    def delete_acto(self, id_acto: int) -> tuple[bool, str]:
        """Elimina un acto de servicio (borrado en cascada para asistencias)."""
        try:
            supabase = self._get_supabase()
            supabase.table("actos_servicio").delete().eq("id", id_acto).execute()
            return True, "Acto de servicio eliminado exitosamente."
        except Exception as e:
            return False, f"Error al eliminar acto de servicio: {str(e)}"

    # ==========================================
    # CONSULTAS ESPECIALES PARA DASHBOARD
    # ==========================================

    def get_servicios_ultimo_mes(self) -> int:
        """Obtiene la cantidad de servicios ocurridos en los últimos 30 días."""
        try:
            import datetime
            supabase = self._get_supabase()
            hace_un_mes = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            res = supabase.table("actos_servicio").select("id", count=CountMethod.exact).gte("fecha", hace_un_mes).execute()
            # En supabase-py res.count contiene el conteo exacto si count='exact'
            return res.count if res.count is not None else len(res.data)
        except Exception as e:
            print(f"Error al obtener servicios del último mes: {e}")
            return 0

    def get_promedio_asistencia_ultimo_mes(self) -> float:
        """Obtiene el promedio de asistencia de los actos ocurridos en los últimos 30 días."""
        try:
            import datetime
            supabase = self._get_supabase()
            hace_un_mes = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            res = supabase.table("actos_servicio").select("total_asistencia").gte("fecha", hace_un_mes).execute()
            actos: list[dict[str, Any]] = cast(list[dict[str, Any]], res.data or [])
            if not actos:
                return 0.0
            total = sum(cast(int, acto.get("total_asistencia", 0)) for acto in actos)
            return round(total / len(actos), 1)
        except Exception as e:
            print(f"Error al obtener promedio de asistencia: {e}")
            return 0.0

    def get_resumen_llamados_ultimo_mes(self) -> dict[str, int]:
        """Obtiene el conteo de actos del último mes agrupados por su clave/acto."""
        try:
            import datetime
            supabase = self._get_supabase()
            hace_un_mes = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
            res = supabase.table("actos_servicio").select("clave").gte("fecha", hace_un_mes).execute()
            actos: list[dict[str, Any]] = cast(list[dict[str, Any]], res.data or [])
            resumen: dict[str, int] = {}
            for acto in actos:
                clave = str(acto.get("clave", "Desconocido"))
                resumen[clave] = resumen.get(clave, 0) + 1
            return resumen
        except Exception as e:
            print(f"Error al obtener resumen de llamados: {e}")
            return {}

    def get_todas_asistencias_bomberos(self) -> list[dict[str, Any]]:
        """Obtiene todas las asistencias registradas de todos los bomberos (para lógica de alertas)."""
        try:
            supabase = self._get_supabase()
            res = supabase.table("asistencias").select("reg_bombero, cantidad_listas, actos_servicio(fecha)").gt("cantidad_listas", 0).execute()
            return cast(list[dict[str, Any]], res.data or [])
        except Exception as e:
            print(f"Error al obtener todas las asistencias de bomberos: {e}")
            return []

# Instancia global del servicio
db_service = DBService()
