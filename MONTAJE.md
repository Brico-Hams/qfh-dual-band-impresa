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

Tornillería: 7 tornillos M4 x 16 + tuerca (fijación al tubo), 12 tornillos M3 x 8 (fijan la varilla en la punta).

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

## Consejos

- Si la varilla de cortina es metálica, el hilo nunca debe tocarla: usa siempre la punta y las grapas.
  Si puedes, usa varilla de madera o fibra de 10 mm: sirve igual y no altera la antena.
- Arriba, los tramos horizontales se cortan en el centro: esos extremos entran al tubo por un
  taladro y se sueldan al coaxial (punto de alimentación, como en el artículo de EA1PA).
- La ranura de hilo es de clic para 2,5 mm. Si tu hilo es otro, cambia `hilo_d` en el .scad.
- Si el tubo entra duro o flojo, cambia `holgura` en el .scad y vuelve a exportar.
