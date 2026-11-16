import os
import sys

# Añadir directorio 'src' al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.dominio.servicio import ControladorLectura
from src.persistencia.repo_json import RepositorioJSON
from src.presentacion.cliente import CLI


def main():
    print("Iniciando LeerJuntos (MVP Sprint 1)...")

    # 1. Instanciar Repositorio JSON (crea data/libros.json y data/sesiones.json si no existen)
    repositorio = RepositorioJSON(ruta_base="data")

    # 2. Instanciar Controlador de la Capa de Dominio
    controlador = ControladorLectura(repositorio=repositorio)

    # 3. Lanzar Interfaz CLI
    app = CLI(controlador=controlador, usuario_id_defecto="usuario_afal_demo")
    app.iniciar()


if __name__ == "__main__":
    main()
