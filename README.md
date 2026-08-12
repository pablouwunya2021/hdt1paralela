# HDT 1 — Medición de Rendimiento en Conteo de Frecuencia de Palabras

Hoja de trabajo 1 del curso de **Computación Paralela y Distribuida**.
Se toma como base el programa de conteo de frecuencia de palabras del **Corto 02** y
se le agrega instrumentación de tiempo para comparar la versión secuencial contra la
paralela, calculando **speedup** y **efficiency**.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| [`conteo_frecuencia_secuencial.c`](conteo_frecuencia_secuencial.c) | Versión secuencial con medición de tiempo |
| [`conteo_frecuencia_paralelo.c`](conteo_frecuencia_paralelo.c) | Versión paralela con POSIX threads y medición de tiempo |
| [`benchmark.sh`](benchmark.sh) | Ejecuta 5 corridas por configuración y calcula promedios, speedup y efficiency |
| [`verificar.sh`](verificar.sh) | Comprueba que la salida paralela sea idéntica a la secuencial (9 configuraciones de hilos + 7 casos borde) |
| [`Makefile`](Makefile) | Compilación y atajos: `make`, `make verificar`, `make benchmark`, `make clean` |
| [`RESULTADOS.md`](RESULTADOS.md) | **Informe completo**: tablas, cálculos y análisis |
| `archivo.txt` | Texto de prueba principal (24 KB) |
| `archivo_grande.txt` | Texto de prueba complementario (958 KB) |
| `resultados_archivo.csv` / `resultados_grande.csv` | Tiempos crudos de cada corrida |

## Compilación

```bash
make
```

O bien, de forma manual:

```bash
gcc -O2 -Wall -o conteo_secuencial conteo_frecuencia_secuencial.c
gcc -O2 -Wall -pthread -o conteo_paralelo conteo_frecuencia_paralelo.c
```

El `Makefile` incluye además `make verificar`, `make benchmark`, `make clean` y
`make ayuda`. Ambos scripts aceptan otro archivo: `make benchmark ARCHIVO=archivo_grande.txt`.

## Uso

```bash
./conteo_secuencial archivo.txt
./conteo_paralelo   archivo.txt 4
```

La bandera `--silencioso` omite la impresión de la tabla de frecuencias y muestra
únicamente el tiempo medido:

```bash
./conteo_paralelo archivo.txt 4 --silencioso
```

## Benchmark automático

```bash
./benchmark.sh archivo.txt 5
```

Ejecuta 5 veces cada configuración (secuencial, 2 hilos, 4 hilos), promedia los
tiempos, calcula speedup y efficiency, e imprime las tablas del informe.

## Qué se mide

El cronómetro (`clock_gettime(CLOCK_MONOTONIC)`) cubre **exclusivamente la fase de
conteo**, idéntica en ambas versiones. La lectura del archivo, el ordenamiento y la
impresión quedan **fuera** de la medición.

En la versión paralela la región medida incluye el reparto del texto, la ejecución de
los hilos y la **reducción** de las tablas privadas — es decir, todo el overhead del
paralelismo se contabiliza honestamente.

## Estrategia de paralelización

1. El texto se divide en N bloques contiguos; cada frontera se avanza hasta un
   separador para **no partir palabras** entre hilos.
2. Cada hilo cuenta su bloque en una tabla **privada**, por lo que la fase paralela
   está **libre de locks y de contención**.
3. El hilo principal **fusiona** las N tablas privadas en la tabla final. Esta
   reducción es la porción secuencial del algoritmo (ley de Amdahl).

## Verificación de correctitud

```bash
./verificar.sh archivo.txt
```

Comprueba que la salida paralela sea **idéntica** a la secuencial con 1, 2, 3, 4, 5,
7, 8, 16 y 32 hilos (904 palabras distintas con las mismas frecuencias en las nueve),
más 7 casos borde —archivo vacío, una sola palabra, solo espacios, más hilos que
bytes, sin salto de línea final— cada uno con 1, 2, 4 y 8 hilos.

## Resumen de resultados

Apple M5 (4 núcleos P + 6 núcleos E), promedio de 5 corridas:

| Archivo | Config. | Tiempo prom. (s) | Speedup | Efficiency |
|---|---|---:|---:|---:|
| `archivo.txt` (24 KB) | Secuencial | 0.003578 | 1.0000 | 100.00 % |
| | 2 hilos | 0.002188 | 1.6353 | 81.76 % |
| | 4 hilos | 0.001745 | 2.0504 | 51.26 % |
| `archivo_grande.txt` (958 KB) | Secuencial | 0.071592 | 1.0000 | 100.00 % |
| | 2 hilos | 0.042284 | 1.6931 | 84.66 % |
| | 4 hilos | 0.024765 | 2.8909 | 72.27 % |

**Hallazgo principal:** el mayor speedup se obtuvo con 4 hilos, pero la mayor
eficiencia con 2 hilos. El speedup crece de forma **sublineal** y la eficiencia
**disminuye** al agregar hilos. El mismo código con 4 hilos pasó de 51 % a 72 % de
eficiencia únicamente al aumentar el tamaño del archivo, lo que confirma que el
beneficio del paralelismo depende de que haya trabajo suficiente para amortizar el
overhead de coordinación.

El análisis completo está en **[RESULTADOS.md](RESULTADOS.md)**.
