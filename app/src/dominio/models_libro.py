import uuid


class Libro:
    """Entidad que representa un libro en la biblioteca del usuario."""

    def __init__(
        self,
        usuario_id: str,
        titulo: str,
        autor: str,
        genero: str,
        total_paginas: int,
        id_libro: str | None = None,
        portada_url: str | None = None,
    ):
        if total_paginas <= 0:
            raise ValueError("El total de páginas debe ser mayor a cero.")

        self.id_libro = id_libro if id_libro else str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.total_paginas = total_paginas
        self.portada_url = portada_url if portada_url else ""

    def calcular_porcentaje_avance(self, pagina_actual: int) -> float:
        """Calcula el porcentaje completado de la lectura (0 a 100%)."""
        if pagina_actual < 0:
            return 0.0
        if pagina_actual >= self.total_paginas:
            return 100.0
        return round((pagina_actual / self.total_paginas) * 100, 2)

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario para serialización JSON."""
        return {
            "id_libro": self.id_libro,
            "usuario_id": self.usuario_id,
            "titulo": self.titulo,
            "autor": self.autor,
            "genero": self.genero,
            "total_paginas": self.total_paginas,
            "portada_url": self.portada_url,
        }

    @classmethod
    def from_dict(
        cls, data: dict
    ) -> "Libro":  # Reconstruye una instancia de Libro desde un diccionario JSON
        return cls(
            id_libro=data["id_libro"],
            usuario_id=data["usuario_id"],
            titulo=data["titulo"],
            autor=data["autor"],
            genero=data["genero"],
            total_paginas=data["total_paginas"],
            portada_url=data.get("portada_url", ""),
        )
