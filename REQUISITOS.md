# Requisitos de seguridad – R-01 depurador-adjuntos

Versión 1.0 · Origen: matriz de riesgos del hogar (R2) y LDS-LAB · Aprobados por: Padre – Jefe de hogar (dueño de la información).

| ID | Requisito | Origen | Criterio de verificación | Prueba asociada |
|---|---|---|---|---|
| REQ-01-01 | Modo simulación por defecto: sin `--ejecutar` no se borra nada | R2; LDS-LAB 8 (valores seguros por defecto) | La ejecución sin parámetros no elimina archivos | `test_req01_01_modo_simulacion_por_defecto_no_borra` |
| REQ-01-02 | Solo se borran archivos respaldados (manifiesto) y más antiguos que el plazo | R2 (regla de conservación) | Los no respaldados y los recientes se conservan | `test_req01_02_solo_borra_respaldados_y_antiguos` |
| REQ-01-03 | Actuar solo dentro de la raíz permitida | R2; A.8.28; CWE-22 | Rutas con `../` fuera de la raíz se rechazan y se registran | `test_req01_03_rechaza_rutas_fuera_de_la_raiz` |
| REQ-01-04 | No seguir enlaces simbólicos | A.8.28; CWE-59 | Un enlace a un archivo externo no lo borra | `test_req01_04_no_sigue_enlaces_simbolicos` |
| REQ-01-05 | Fallo seguro: validar todo antes de borrar; si algo falla, no borrar nada | A.8.27 | Ante un error de permisos ningún archivo se borra | `test_req01_05_falla_segura_no_borra_a_medias` |
| REQ-01-06 | La bitácora registra nombre, tamaño y fecha, nunca el contenido | Ley 1581 art. 4 lit. g y h; A.8.15 | El contenido no aparece en la bitácora | `test_req01_06_bitacora_sin_contenido` |
| REQ-01-07 | La ruta por defecto es la del entorno de prueba | A.8.31 | Sin configuración, la carpeta es `datos_prueba/` | `test_req01_07_ruta_por_defecto_es_la_de_prueba` |
| REQ-01-08 | Confirmación explícita antes de borrar | R2 | `--ejecutar` sin `--confirmar` exige escribir BORRAR | Verificación manual (LC-08) |
