from dominio.models_libro import Libro
from dominio.models_sesion import SesionLectura


class ServicioMetricasLibro:
    """Calcula indicadores específicos por sesión y por libro."""

    @staticmethod
    def calcular_metricas_sesion(
        sesion: SesionLectura, libro: Libro
    ) -> dict[str, float]:
        """Calcula el rendimiento puntual de una sesión finalizada."""
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
        """
        Determina un indicador cualitativo de dificultad percibida
        comparando la velocidad de la sesión contra la media histórica del usuario.
        """
        if promedio_usuario_ppm <= 0:
            return "Normal / Estándar"

        ratio = velocidad_sesion_ppm / promedio_usuario_ppm
        if ratio >= 1.2:
            return "Lectura Fluida / Ligera"
        elif 0.8 <= ratio < 1.2:
            return "Normal / Estándar"
        else:
            return "Exigente / Densa"
