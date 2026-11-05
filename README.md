# R-01 depurador-adjuntos

Herramienta interna del hogar (laboratorio académico). Aplica la regla de conservación de adjuntos del
tratamiento del riesgo **R2** de la matriz de riesgos: borra de la carpeta local los adjuntos del trabajo
que ya están respaldados en la nube corporativa y que superan el plazo de conservación.

> Escenario de laboratorio: todos los datos son ficticios. Ver `SECURITY.md`.

## Uso

```bash
python3 depurador.py                      # simulación sobre la carpeta de prueba (no borra)
python3 depurador.py --dias 30 --ejecutar # borra, previa confirmación escrita "BORRAR"
```

Variables de entorno:

| Variable | Uso | Valor por defecto |
|---|---|---|
| `DEPURADOR_RAIZ` | Raíz dentro de la cual puede actuar | `datos_prueba/` |
| `DEPURADOR_CARPETA` | Carpeta de trabajo | la raíz |
| `DEPURADOR_DIAS` | Plazo de conservación | 30 |
| `DEPURADOR_BITACORA` | Archivo de bitácora | `bitacora_depurador.log` |

El entorno de producción solo se activa con configuración explícita (`/opt/herramientas/depurador.env`).
# prueba
