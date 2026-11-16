from datetime import UTC, datetime

from dominio.models_libro import Libro
from dominio.models_sesion import SesionLectura


class ServicioMetricasPersonal:
    """Calcula las métricas acumuladas anuales del usuario (HU-1.4)."""

    @staticmethod
    def calcular_acumulado_anual(
        sesiones_usuario: list[SesionLectura],
        libros_usuario: list[Libro],
        anio: int | None = None,
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
