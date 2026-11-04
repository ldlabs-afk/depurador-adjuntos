#!/usr/bin/env python3
"""R-01 depurador-adjuntos.

Aplica la regla de conservación de adjuntos del hogar (tratamiento del riesgo R2):
borra de la carpeta local los adjuntos del trabajo que ya están respaldados en la
nube corporativa y que superan el plazo de conservación.

Principios de diseño (ver DISENO.md):
- Modo simulación por defecto: sin --ejecutar no se borra nada.
- Solo actúa dentro de la raíz permitida (DEPURADOR_RAIZ).
- No sigue enlaces simbólicos.
- Valida todo antes de borrar: si algo falla, no borra nada.
- La bitácora registra nombre, tamaño y fecha; nunca el contenido.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path

DIRECTORIO_HERRAMIENTA = Path(__file__).resolve().parent
CARPETA_PRUEBA = DIRECTORIO_HERRAMIENTA / "datos_prueba"
MANIFIESTO = "respaldados.txt"
DIAS_POR_DEFECTO = 30
SEGUNDOS_POR_DIA = 86400

log = logging.getLogger("depurador")


class RutaNoPermitida(Exception):
    """La ruta solicitada está fuera de la raíz permitida."""


class ValidacionFallida(Exception):
    """Algún archivo seleccionado no se puede borrar de forma segura."""


def configurar_bitacora(ruta_bitacora: Path) -> None:
    formato = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    manejador = logging.FileHandler(ruta_bitacora, encoding="utf-8")
    manejador.setFormatter(formato)
    consola = logging.StreamHandler(sys.stdout)
    consola.setFormatter(logging.Formatter("%(message)s"))
    log.handlers.clear()
    log.addHandler(manejador)
    log.addHandler(consola)
    log.setLevel(logging.INFO)


def raiz_permitida() -> Path:
    """Raíz dentro de la cual la herramienta puede actuar."""
    valor = os.environ.get("DEPURADOR_RAIZ")
    return Path(valor).resolve() if valor else CARPETA_PRUEBA.resolve()


def resolver_carpeta(solicitada: str | None) -> Path:
    """Resuelve la carpeta de trabajo y verifica que esté dentro de la raíz permitida."""
    raiz = raiz_permitida()
    if solicitada is None:
        solicitada = os.environ.get("DEPURADOR_CARPETA", str(raiz))
    carpeta = Path(solicitada).resolve()
    if carpeta != raiz and raiz not in carpeta.parents:
        log.warning("RECHAZADO ruta fuera de la raíz permitida: %s (raíz: %s)", solicitada, raiz)
        raise RutaNoPermitida(f"La ruta {solicitada} está fuera de la raíz permitida {raiz}")
    try:
        es_carpeta = carpeta.is_dir()
    except OSError:
        es_carpeta = False
    if not es_carpeta:
        raise RutaNoPermitida(f"La carpeta {carpeta} no existe o no es accesible")
    return carpeta


def cargar_respaldados(carpeta: Path) -> set[str]:
    """Nombres de archivo que ya están respaldados en la nube corporativa."""
    manifiesto = carpeta / MANIFIESTO
    if not manifiesto.is_file():
        return set()
    nombres = set()
    for linea in manifiesto.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#"):
            nombres.add(linea)
    return nombres


def seleccionar(carpeta: Path, dias: int, ahora: float | None = None) -> list[Path]:
    """Archivos respaldados y más antiguos que el plazo. No sigue enlaces simbólicos."""
    respaldados = cargar_respaldados(carpeta)
    limite = (ahora if ahora is not None else time.time()) - dias * SEGUNDOS_POR_DIA
    seleccion = []
    for entrada in sorted(carpeta.iterdir()):
        if entrada.name == MANIFIESTO or entrada.name.startswith("~$"):
            continue
        if entrada.is_symlink():
            log.warning("OMITIDO enlace simbólico: %s", entrada.name)
            continue
        if not entrada.is_file():
            continue
        if entrada.name not in respaldados:
            continue
        if entrada.stat().st_mtime > limite:
            continue
        seleccion.append(entrada)
    return seleccion


def validar_antes_de_borrar(carpeta: Path, archivos: list[Path]) -> None:
    """Fallo seguro: si un archivo no cumple, se aborta sin borrar ninguno."""
    for archivo in archivos:
        real = archivo.resolve()
        if real.parent != carpeta:
            raise ValidacionFallida(f"{archivo.name} no está directamente en la carpeta de trabajo")
        if archivo.is_symlink() or not archivo.is_file():
            raise ValidacionFallida(f"{archivo.name} ya no es un archivo regular")
        if not os.access(carpeta, os.W_OK):
            raise ValidacionFallida("Sin permiso de escritura en la carpeta de trabajo")


def describir(archivo: Path) -> str:
    datos = archivo.stat()
    fecha = time.strftime("%Y-%m-%d", time.localtime(datos.st_mtime))
    return f"{archivo.name} ({datos.st_size} bytes, modificado {fecha})"


def depurar(carpeta: Path, dias: int, ejecutar: bool) -> list[Path]:
    seleccion = seleccionar(carpeta, dias)
    if not seleccion:
        log.info("Sin archivos para depurar en %s", carpeta)
        return []
    if not ejecutar:
        for archivo in seleccion:
            log.info("SIMULACIÓN se borraría: %s", describir(archivo))
        log.info("SIMULACIÓN %d archivo(s). Use --ejecutar para borrar.", len(seleccion))
        return seleccion
    validar_antes_de_borrar(carpeta, seleccion)
    for archivo in seleccion:
        descripcion = describir(archivo)
        archivo.unlink()
        log.info("BORRADO %s", descripcion)
    log.info("Depuración terminada: %d archivo(s) borrado(s)", len(seleccion))
    return seleccion


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Depura adjuntos ya respaldados (R-01).")
    parser.add_argument("--carpeta", help="Carpeta de trabajo (por defecto, la de prueba)")
    parser.add_argument("--dias", type=int, default=int(os.environ.get("DEPURADOR_DIAS", DIAS_POR_DEFECTO)))
    parser.add_argument("--ejecutar", action="store_true", help="Borrar de verdad (sin esto, solo simula)")
    parser.add_argument("--confirmar", action="store_true", help="No pedir confirmación interactiva")
    args = parser.parse_args(argv)

    bitacora = Path(os.environ.get("DEPURADOR_BITACORA", "bitacora_depurador.log"))
    try:
        configurar_bitacora(bitacora)
    except OSError:
        print("ABORTADO sin borrar nada: no se puede escribir la bitácora")
        return 3

    try:
        carpeta = resolver_carpeta(args.carpeta)
        if args.ejecutar and not args.confirmar:
            respuesta = input(f"Se borrarán archivos de {carpeta}. Escriba BORRAR para continuar: ")
            if respuesta.strip() != "BORRAR":
                log.info("Cancelado por el usuario; no se borró nada")
                return 1
        depurar(carpeta, args.dias, args.ejecutar)
    except (RutaNoPermitida, ValidacionFallida) as error:
        log.error("ABORTADO sin borrar nada: %s", error)
        return 2
    except OSError:
        log.error("ABORTADO: error de acceso a archivos; revise la bitácora y los permisos")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
