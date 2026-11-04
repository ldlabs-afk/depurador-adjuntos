"""Pruebas de seguridad y funcionales de R-01 (requisitos en REQUISITOS.md)."""
import os
import time
from pathlib import Path

import pytest

import depurador

HACE_60_DIAS = time.time() - 60 * 86400


def crear(carpeta: Path, nombre: str, viejo: bool = True) -> Path:
    archivo = carpeta / nombre
    archivo.write_text("contenido ficticio de prueba", encoding="utf-8")
    if viejo:
        os.utime(archivo, (HACE_60_DIAS, HACE_60_DIAS))
    return archivo


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    raiz = tmp_path / "raiz"
    carpeta = raiz / "adjuntos"
    carpeta.mkdir(parents=True)
    monkeypatch.setenv("DEPURADOR_RAIZ", str(raiz))
    monkeypatch.setenv("DEPURADOR_BITACORA", str(tmp_path / "bitacora.log"))
    depurador.configurar_bitacora(tmp_path / "bitacora.log")
    return carpeta


def test_req01_01_modo_simulacion_por_defecto_no_borra(entorno):
    viejo = crear(entorno, "balance_enero.pdf")
    (entorno / "respaldados.txt").write_text("balance_enero.pdf\n", encoding="utf-8")
    seleccion = depurador.depurar(entorno, dias=30, ejecutar=False)
    assert seleccion == [viejo]
    assert viejo.exists()


def test_req01_02_solo_borra_respaldados_y_antiguos(entorno):
    respaldado_viejo = crear(entorno, "acta_enero.pdf")
    respaldado_nuevo = crear(entorno, "acta_octubre.pdf", viejo=False)
    sin_respaldo = crear(entorno, "inventario.xlsx")
    (entorno / "respaldados.txt").write_text("acta_enero.pdf\nacta_octubre.pdf\n", encoding="utf-8")
    depurador.depurar(entorno, dias=30, ejecutar=True)
    assert not respaldado_viejo.exists()
    assert respaldado_nuevo.exists()
    assert sin_respaldo.exists()


def test_req01_03_rechaza_rutas_fuera_de_la_raiz(entorno):
    with pytest.raises(depurador.RutaNoPermitida):
        depurador.resolver_carpeta(str(entorno / ".." / ".." / ".."))


def test_req01_04_no_sigue_enlaces_simbolicos(entorno, tmp_path):
    externo = tmp_path / "fuera.txt"
    externo.write_text("archivo externo", encoding="utf-8")
    os.utime(externo, (HACE_60_DIAS, HACE_60_DIAS))
    (entorno / "enlace.txt").symlink_to(externo)
    (entorno / "respaldados.txt").write_text("enlace.txt\n", encoding="utf-8")
    depurador.depurar(entorno, dias=30, ejecutar=True)
    assert externo.exists()


def test_req01_05_falla_segura_no_borra_a_medias(entorno, monkeypatch):
    a = crear(entorno, "a.pdf")
    b = crear(entorno, "b.pdf")
    (entorno / "respaldados.txt").write_text("a.pdf\nb.pdf\n", encoding="utf-8")
    monkeypatch.setattr(depurador.os, "access", lambda *_: False)
    with pytest.raises(depurador.ValidacionFallida):
        depurador.depurar(entorno, dias=30, ejecutar=True)
    assert a.exists() and b.exists()


def test_req01_06_bitacora_sin_contenido(entorno, tmp_path):
    crear(entorno, "estado_financiero.pdf")
    (entorno / "respaldados.txt").write_text("estado_financiero.pdf\n", encoding="utf-8")
    depurador.depurar(entorno, dias=30, ejecutar=True)
    texto = (tmp_path / "bitacora.log").read_text(encoding="utf-8")
    assert "BORRADO estado_financiero.pdf" in texto
    assert "contenido ficticio" not in texto


def test_req01_07_ruta_por_defecto_es_la_de_prueba(monkeypatch):
    monkeypatch.delenv("DEPURADOR_RAIZ", raising=False)
    monkeypatch.delenv("DEPURADOR_CARPETA", raising=False)
    assert depurador.resolver_carpeta(None) == depurador.CARPETA_PRUEBA.resolve()


def test_req01_02_omite_temporales_de_office(entorno):
    temporal = crear(entorno, "~$acta_enero.docx")
    (entorno / "respaldados.txt").write_text("~$acta_enero.docx\n", encoding="utf-8")
    depurador.depurar(entorno, dias=30, ejecutar=True)
    assert temporal.exists()


def test_req01_02_conserva_acta_no_respaldada(entorno):
    import shutil
    from pathlib import Path
    origen = Path(__file__).parent / "fixtures" / "acta_asamblea_marzo.txt"
    copia = entorno / origen.name
    shutil.copy(origen, copia)
    os.utime(copia, (HACE_60_DIAS, HACE_60_DIAS))
    depurador.depurar(entorno, dias=30, ejecutar=True)
    assert copia.exists()
