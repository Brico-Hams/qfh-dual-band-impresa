# QFH doble banda – piezas impresas y montaje

Tubo central 30 mm · varilla de cortina 10 mm · hilo de cobre 2,5 mm (cable de 35 mm² destrenzado)

## Qué imprimir (PETG o ASA, 4 perímetros, 40 % relleno)

| STL | Cantidad | Uso |
|---|---|---|
| cruceta_vhf.stl | 1 | Arriba, VHF (4 brazos) |
| barra_vhf.stl | 4 | VHF: 2 abajo + 2 a media altura |
| punta.stl | 12 | Aislador en el extremo de cada varilla |
| grapa.stl | 8 | Separa el hilo horizontal 12 mm de la varilla |
| cruceta_uhf.stl | 1 | Arriba, UHF (brazos impresos) |
| barra_uhf_grande.stl | 1 | Abajo, UHF espira grande |
| barra_uhf_peq.stl | 1 | Abajo, UHF espira pequeña |

Tornillería: 8 tornillos M4 x 16 + tuerca (fijación al tubo), 12 tornillos M3 x 8 (fijan la varilla en la punta).

## Varillas de 10 mm a cortar (12 trozos)

| Espira | Radio al hilo | Largo varilla | Trozos |
|---|---|---|---|
| VHF grande | 143 mm | 108 mm | 6 |
| VHF pequeña | 135,5 mm | 100 mm | 6 |

Con la varilla metida 20 mm en la punta, el hilo queda en el radio nominal.
Empujando la punta hasta el fondo, el radio baja 10 mm (lo que tuvo que reducir EA1PA).

## Posiciones en el tubo (desde la cruceta VHF superior, z = 0)

| Pieza | Altura | Giro |
|---|---|---|
| cruceta_vhf | 0 | brazos 0°/180° = espira grande, 90°/270° = pequeña |
| cruceta_uhf | −30 mm | igual que la VHF |
| barra_vhf (media grande) | −325 mm | 90° |
| barra_vhf (media pequeña) | −307 mm | 0° |
| barra_uhf_peq | −30 − 206 = −236 mm | 90° |
| barra_uhf_grande | −30 − 218 = −248 mm | 0° |
| barra_vhf (abajo pequeña) | −615 mm | 90° |
| barra_vhf (abajo grande) | −650 mm | 0° |

Las hélices dan media vuelta: el extremo inferior queda en la misma línea que el superior,
y a media altura el hilo pasa a 90° del brazo superior. Todas giran en el mismo sentido.

## Plantilla de taladros (papel)

Para marcar todos los taladros del tubo de 30 mm sin medir: `plantilla_taladros.pdf`
(3 hojas A4, generadas con `python plantilla_taladros.py`; también `plantilla_taladros_p1.svg` …
`_p3.svg` y la tira completa `plantilla_taladros.svg`, todo en la raíz del repositorio).

1. **Imprime al 100 %** (sin «ajustar a página»). En cada hoja comprueba que el cuadrado mide
   50 mm y la barra de escala 100 mm.
2. **Recorta** cada hoja por la línea superior (salvo la 1) y pon su borde sobre la línea
   discontinua de la hoja anterior («une con hoja 2»), alineando las líneas de ángulo y de altura.
   Pega con cinta. Recorta la tira por el contorno (94,25 mm de circunferencia + 15 mm de solapa).
3. **Enrolla** la tira sobre el tubo con el dibujo hacia fuera y la parte superior (z = 0) arriba.
   Alinea la línea **0°** con los brazos del primer soporte (cruceta VHF) y pega la solapa
   «PEGAR AQUÍ» por debajo del borde contrario. Los ángulos crecen hacia la derecha.
4. **Marca** el centro de cada cruz con un granete, quita la plantilla o déjala puesta.
5. **Taladra** perpendicular al eje del tubo, con el tubo en un bloque en V: primero broca de 2 mm
   y luego la final. T1–T8 (tornillo M4 de cada soporte): **4,3 mm**. F1–F4 (entrada de los hilos de
   alimentación): **4 mm**.

Ángulo y altura de cada taladro (ángulo = giro del soporte + posición del tornillo en la pieza: 45°
en crucetas y barras UHF, 90° en barras VHF):

| Taladro | Soporte | z | Ángulo |
|---|---|---|---|
| T1 | cruceta_vhf | 0 | 45° |
| T2 | cruceta_uhf | −30 mm | 45° |
| T3 | barra_uhf_peq | −236 mm | 135° |
| T4 | barra_uhf_grande | −248 mm | 45° |
| T5 | barra_vhf media pequeña | −307 mm | 90° |
| T6 | barra_vhf media grande | −325 mm | 180° |
| T7 | barra_vhf abajo pequeña | −615 mm | 180° |
| T8 | barra_vhf abajo grande | −650 mm | 90° |
| F1–F4 | entrada de hilos | −15 mm | 0°, 90°, 180°, 270° |

Suposiciones: la altura de la tabla es el eje del soporte (el tornillo está en su mitad,
`manguito_h/2`); los hilos de alimentación entran a −15 mm, el hueco entre los manguitos VHF y UHF.
Comprobación: `python test_plantilla.py`.

## Consejos

- Si la varilla de cortina es metálica, el hilo nunca debe tocarla: usa siempre la punta y las grapas.
  Si puedes, usa varilla de madera o fibra de 10 mm: sirve igual y no altera la antena.
- Arriba, los tramos horizontales se cortan en el centro: esos extremos entran al tubo por un
  taladro y se sueldan al coaxial (punto de alimentación, como en el artículo de EA1PA).
- La ranura de hilo es de clic para 2,5 mm. Si tu hilo es otro, cambia `hilo_d` en el .scad.
- Si el tubo entra duro o flojo, cambia `holgura` en el .scad y vuelve a exportar.
