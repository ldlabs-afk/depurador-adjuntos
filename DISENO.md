# Diseño de R-01 – aplicación de los principios de ingeniería segura (LDS-LAB, sección 8)

| Principio | Cómo se aplica en R-01 |
|---|---|
| Mínimo privilegio | En producción se ejecuta como el usuario `padre`, sin sudo, y solo tiene escritura en su carpeta de adjuntos |
| Valores seguros por defecto | Modo simulación por defecto; la carpeta por defecto es la de prueba |
| Defensa en profundidad | Raíz permitida + manifiesto de respaldados + plazo + confirmación escrita |
| Fallo seguro | Se valida toda la selección antes de borrar; un error aborta sin borrar nada |
| Separación de funciones | El hijo desarrolla; el padre aprueba los cambios y es quien ejecuta en producción |

Flujo: resolver carpeta → verificar raíz → leer manifiesto → seleccionar (sin enlaces) → simular o validar → borrar → bitácora.
