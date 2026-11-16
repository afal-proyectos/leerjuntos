# from servicio_metricaspersonal import ServicioMetricasPersonal
from persistencia.repositorio import IRepositorioDatos

from dominio.calcular_proyecciones import CalculadorProyecciones
from dominio.models_libro import Libro
from dominio.models_sesion import EstadoSesion, SesionLectura
from dominio.servicio_metricaslibro import ServicioMetricasLibro


class ControladorLectura:
    """
    Controlador central de la Capa de Dominio.
    Coordina la interacción entre la UI, los modelos, los servicios de cálculo y el repositorio.
    """

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
