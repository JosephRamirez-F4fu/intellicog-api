from PIL import Image
import io
import os
from uuid import uuid4


def validar_imagen(content_type: str):
    if not content_type.startswith("image/"):
        raise ValueError("El archivo no es una imagen válida.")


def convertir_a_png(contenido_bytes: bytes) -> Image.Image:
    try:
        imagen = Image.open(io.BytesIO(contenido_bytes))
        return imagen.convert("RGBA")
    except Exception as e:
        raise ValueError(f"No se pudo procesar la imagen: {e}")


def guardar_imagen_png(imagen: Image.Image, path: str) -> str:
    nombre_archivo = f"{uuid4().hex}.png"
    ruta = os.path.join(path, nombre_archivo)
    imagen.save(ruta, format="PNG")
    return nombre_archivo


def eliminar_imagen(ruta: str):
    if os.path.exists(ruta):
        os.remove(ruta)
    else:
        raise FileNotFoundError(f"La imagen {ruta} no existe.")
