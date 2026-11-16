import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Optional


class EstadoSesion(Enum):
    INACTIVA = "INACTIVA"
    LEYENDO = "LEYENDO"
    PAUSADA = "PAUSADA"
    FINALIZADA = "FINALIZADA"
    GUARDADA = "GUARDADA"


class SesionLectura:
    """Entidad que gestiona el ciclo de vida y métricas de una sesión de lectura."""

    def __init__(
        self,
        libro_id: str,
        usuario_id: str,
        pagina_inicio: int,
        id_sesion: Optional[str] = None,
    ):
        self.id_sesion = id_sesion if id_sesion else str(uuid.uuid4())
        self.libro_id = libro_id
        self.usuario_id = usuario_id
        self.pagina_inicio = pagina_inicio
        self.pagina_fin: Optional[int] = None

        self.inicio_utc: Optional[datetime] = None
        self.fin_utc: Optional[datetime] = None
        self.minutos_pausa: float = 0.0
        # Recordatorio: agregar al diagrama
        self._inicio_pausa_temp: Optional[datetime] = None
        self.estado: EstadoSesion = EstadoSesion.INACTIVA

    def iniciar(self) -> None:
        """Transiciona a LEYENDO y registra la marca de tiempo de inicio UTC."""
        self.inicio_utc = datetime.now(UTC)
        self.estado = EstadoSesion.LEYENDO

    def pausar(self) -> None:
        """Transiciona a PAUSADA y registra el inicio del intervalo de pausa."""
        if self.estado == EstadoSesion.LEYENDO:
            self._inicio_pausa_temp = datetime.now(UTC)
            self.estado = EstadoSesion.PAUSADA

    def reanudar(self) -> None:
        """Reanuda la lectura acumulando la duración del intervalo de pausa."""
        if self.estado == EstadoSesion.PAUSADA and self._inicio_pausa_temp:
            ahora = datetime.now(UTC)
            delta_pausa = (ahora - self._inicio_pausa_temp).total_seconds() / 60.0
            self.minutos_pausa += delta_pausa
            self._inicio_pausa_temp = None
            self.estado = EstadoSesion.LEYENDO

    def detener(self, pagina_fin: int) -> None:
        """Detiene el conteo registrando la marca final UTC y la página alcanzada."""
        if self.estado == EstadoSesion.PAUSADA:
            self.reanudar()

        if pagina_fin < self.pagina_inicio:
            raise ValueError("La página final no puede ser menor a la página inicial.")

        self.fin_utc = datetime.now(UTC)
        self.pagina_fin = pagina_fin
        self.estado = EstadoSesion.FINALIZADA

    def calcular_minutos_netos(self) -> float:
        """Calcula el tiempo neto transcurrido descontando el tiempo en pausa."""
        if not self.inicio_utc or not self.fin_utc:
            return 0.0
        duracion_total = (self.fin_utc - self.inicio_utc).total_seconds() / 60.0
        tiempo_neto = duracion_total - self.minutos_pausa
        return max(round(tiempo_neto, 2), 0.01)

    def calcular_paginas_leidas(self) -> int:
        """Retorna la cantidad de páginas leídas en la sesión."""
        if self.pagina_fin is None:
            return 0
        return self.pagina_fin - self.pagina_inicio

    def calcular_velocidad_ppm(self) -> float:
        """Calcula la velocidad de lectura en Páginas Por Minuto (PPM)."""
        paginas = self.calcular_paginas_leidas()
        minutos = self.calcular_minutos_netos()
        if minutos <= 0:
            return 0.0
        return round(paginas / minutos, 2)
