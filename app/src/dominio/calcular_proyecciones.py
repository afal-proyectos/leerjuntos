from datetime import UTC, datetime, timedelta
from typing import Any

from dominio.models_libro import Libro
from dominio.models_sesion import EstadoSesion, SesionLectura


class CalculadorProyecciones:
    """
    Servicio encargado de generar pares ordenados (tiempo, páginas)
    y realizar proyecciones de finalización de lectura mediante regresión lineal/promedio.
    """

    @staticmethod
    def obtener_pares_ordenados(
        sesiones: list[SesionLectura],
    ) -> list[tuple[float, int]]:
        """
        Genera una lista de pares ordenados (x, y) donde:
        - x = tiempo acumulado neto en minutos
        - y = página final alcanzada en cada sesión
        """
        # Filtrar solo sesiones finalizadas o guardadas
        sesiones_completas = [
            s
            for s in sesiones
            if s.estado in (EstadoSesion.FINALIZADA, EstadoSesion.GUARDADA)
            and s.pagina_fin is not None
        ]

        # Ordenar por tiempo de inicio UTC
        sesiones_completas.sort(
            key=lambda s: s.inicio_utc if s.inicio_utc else datetime.min
        )

        pares: list[tuple[float, int]] = []
        tiempo_acumulado = 0.0

        for s in sesiones_completas:
            tiempo_acumulado += s.calcular_minutos_netos()
            if s.pagina_fin is not None:
                pares.append((round(tiempo_acumulado, 2), s.pagina_fin))

        return pares

    @classmethod
    def estimar_tiempo_restante(
        cls,
        libro: Libro,
        sesiones: list[SesionLectura],
        pagina_actual: int,
    ) -> dict[str, Any]:
        """
        Calcula los minutos restantes y la fecha estimada de finalización del libro
        basándose en la velocidad promedio obtenida de las sesiones históricas.
        """
        paginas_restantes = libro.total_paginas - pagina_actual
        if paginas_restantes <= 0:
            return {
                "paginas_restantes": 0,
                "minutos_estimados_restantes": 0.0,
                "horas_estimadas_restantes": 0.0,
                "fecha_estimada_fin": datetime.now(UTC).strftime("%Y-%m-%d"),
                "completado": True,
            }

        pares = cls.obtener_pares_ordenados(sesiones)
        if not pares:
            return {
                "paginas_restantes": paginas_restantes,
                "minutos_estimados_restantes": None,
                "horas_estimadas_restantes": None,
                "fecha_estimada_fin": None,
                "completado": False,
            }

        # Cálculo de la tasa promedio (PPM global para este libro)
        total_minutos = pares[-1][0]
        paginas_avanzadas = (
            pagina_actual - sesiones[0].pagina_inicio if sesiones else pagina_actual
        )

        if total_minutos <= 0 or paginas_avanzadas <= 0:
            ppm_promedio = 0.5  # Valor por defecto prudente (0.5 pag/min)
        else:
            ppm_promedio = paginas_avanzadas / total_minutos

        minutos_restantes = round(paginas_restantes / ppm_promedio, 2)
        horas_restantes = round(minutos_restantes / 60.0, 2)

        # Estimación de fecha proyectando 30 minutos de lectura diaria promedio
        dias_estimados = max(1, int(minutos_restantes / 30.0))
        fecha_fin = datetime.now(UTC) + timedelta(days=dias_estimados)

        return {
            "paginas_restantes": paginas_restantes,
            "minutos_estimados_restantes": minutos_restantes,
            "horas_estimadas_restantes": horas_restantes,
            "fecha_estimada_fin": fecha_fin.strftime("%Y-%m-%d"),
            "ppm_utilizado": round(ppm_promedio, 2),
            "completado": False,
        }


"""
class ServicioMetricasLibro:
    #Calcula indicadores específicos por sesión y por libro.

    @staticmethod
    def calcular_metricas_sesion(
        sesion: SesionLectura, libro: Libro
    ) -> dict[str, float]:
        #Calcula el rendimiento puntual de una sesión finalizada
        minutos_netos = sesion.calcular_minutos_netos()
        paginas_leidas = sesion.calcular_paginas_leidas()
        velocidad_ppm = sesion.calcular_velocidad_ppm()
        porcentaje_avance = libro.calcular_porcentaje_avance(
            sesion.pagina_fin or sesion.pagina_inicio
        )

        return {
            "minutos_netos": minutos_netos,
            "paginas_leidas": paginas_leidas,
            "velocidad_ppm": velocidad_ppm,
            "porcentaje_avance_libro": porcentaje_avance,
        }

    @staticmethod
    def evaluar_dificultad_percibida(
        velocidad_sesion_ppm: float, promedio_usuario_ppm: float
    ) -> str:
        
        #Determina un indicador cualitativo de dificultad percibida
        #comparando la velocidad de la sesión contra la media histórica del usuario.
        
        if promedio_usuario_ppm <= 0:
            return "Normal / Estándar"

        ratio = velocidad_sesion_ppm / promedio_usuario_ppm
        if ratio >= 1.2:
            return "Lectura Fluida / Ligera"
        elif 0.8 <= ratio < 1.2:
            return "Normal / Estándar"
        else:
            return "Exigente / Densa"

"""
"""
class ServicioMetricasPersonal:
    #Calcula las métricas acumuladas anuales del usuario (HU-1.4).

    @staticmethod
    def calcular_acumulado_anual(
        sesiones_usuario: list[SesionLectura],
        libros_usuario: list[Libro],
        anio: Optional[int] = None,
    ) -> dict[str, float]:
        if anio is None:
            anio = datetime.now(UTC).year

        # Filtrar sesiones del año especificado
        sesiones_anio = [
            s for s in sesiones_usuario if s.inicio_utc and s.inicio_utc.year == anio
        ]

        minutos_totales = sum(s.calcular_minutos_netos() for s in sesiones_anio)
        horas_totales = round(minutos_totales / 60.0, 2)

        # Contar libros cuya última sesión registrada en el año llegó al 100% de páginas
        libros_map = {l.id_libro: l for l in libros_usuario}
        libros_completados = 0

        for libro in libros_usuario:
            sesiones_libro = [
                s
                for s in sesiones_anio
                if s.libro_id == libro.id_libro and s.pagina_fin is not None
            ]
            if sesiones_libro:
                max_pagina = max(s.pagina_fin for s in sesiones_libro if s.pagina_fin)
                if max_pagina >= libro.total_paginas:
                    libros_completados += 1

        return {
            "anio": anio,
            "horas_leidas_anual": horas_totales,
            "libros_terminados_anual": libros_completados,
            "total_sesiones_anual": len(sesiones_anio),
        }

"""
""""
class ControladorLectura:
    
    #Controlador central de la Capa de Dominio.
    #Coordina la interacción entre la UI, los modelos, los servicios de cálculo y el repositorio.
    

    def __init__(self, repositorio: IRepositorioDatos):
        self.repo = repositorio

    def registrar_libro(
        self,
        usuario_id: str,
        titulo: str,
        autor: str,
        genero: str,
        total_paginas: int,
    ) -> Libro:
        libro = Libro(
            usuario_id=usuario_id,
            titulo=titulo,
            autor=autor,
            genero=genero,
            total_paginas=total_paginas,
        )
        self.repo.guardar_libro(libro)
        return libro

    def obtener_biblioteca(self, usuario_id: str) -> list[Libro]:
        return self.repo.obtener_libros(usuario_id)

    def iniciar_sesion_lectura(
        self, libro_id: str, usuario_id: str, pagina_inicio: int
    ) -> SesionLectura:
        sesion = SesionLectura(
            libro_id=libro_id,
            usuario_id=usuario_id,
            pagina_inicio=pagina_inicio,
        )
        sesion.iniciar()
        return sesion

    def finalizar_y_guardar_sesion(
        self, sesion: SesionLectura, pagina_fin: int
    ) -> dict[str, object]:
        libro = self.repo.obtener_libro_por_id(sesion.libro_id)
        if not libro:
            raise ValueError(f"Libro con ID {sesion.libro_id} no encontrado.")

        # Transición de estado en la entidad
        sesion.detener(pagina_fin)

        # Cálculo de métricas
        metricas = ServicioMetricasLibro.calcular_metricas_sesion(sesion, libro)

        # Transición a GUARDADA y persistencia
        sesion.estado = EstadoSesion.GUARDADA
        self.repo.registrar_sesion(sesion)

        # Proyección de finalización actualizada
        sesiones_historia = self.repo.obtener_sesiones(libro.id_libro)
        proyeccion = CalculadorProyecciones.estimar_tiempo_restante(
            libro, sesiones_historia, pagina_fin
        )

        return {
            "sesion_id": sesion.id_sesion,
            "metricas_sesion": metricas,
            "proyeccion": proyeccion,
        }
"""
