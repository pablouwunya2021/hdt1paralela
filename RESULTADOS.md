# HDT 1 — Medición de Rendimiento: Conteo de Frecuencia de Palabras

**Curso:** Computación Paralela y Distribuida
**Base:** versión secuencial y paralela del programa del Corto 02
**Fecha:** 11 de agosto de 2026

---

## 1. Entorno de pruebas

| Elemento | Valor |
|---|---|
| Procesador | Apple M5 (arquitectura ARM64) |
| Núcleos | 10 lógicos = **4 de rendimiento (P) + 6 de eficiencia (E)** |
| Sistema operativo | macOS 26.5.2 |
| Compilador | Apple clang 21.0.0 |
| Banderas de compilación | `-O2 -Wall` (secuencial), `-O2 -Wall -pthread` (paralelo) |
| Modelo de paralelismo | **POSIX threads (pthreads)** — memoria compartida |
| Reloj utilizado | `clock_gettime(CLOCK_MONOTONIC)`, resolución de nanosegundos |
| Archivo de prueba principal | `archivo.txt` — 24,530 bytes, 4,589 palabras, **904 palabras distintas** |
| Archivo de prueba complementario | `archivo_grande.txt` — 981,240 bytes, 183,560 palabras, 904 distintas |

### Verificación de correctitud

Un speedup solo tiene sentido si ambas versiones calculan lo mismo. Antes de medir se
comprobó que la versión paralela produce **exactamente la misma tabla de frecuencias**
que la secuencial. La verificación está automatizada en [`verificar.sh`](verificar.sh):

**Prueba 1 — distinta cantidad de hilos sobre `archivo.txt`.** Se comparó la salida
completa (904 palabras con sus frecuencias) contra la referencia secuencial con
**1, 2, 3, 4, 5, 7, 8, 16 y 32 hilos**: idéntica en las nueve configuraciones. Se
incluyen números impares y no divisores del tamaño del archivo para forzar cortes en
posiciones irregulares.

**Prueba 2 — casos borde.** Cada uno comparado con 1, 2, 4 y 8 hilos:

| Caso | Bytes | Qué ejercita | Resultado |
|---|---:|---|---|
| Archivo vacío | 0 | Todos los bloques vacíos | ✅ idéntico |
| Una sola palabra | 4 | Menos palabras que hilos | ✅ idéntico |
| Solo espacios y tabuladores | 7 | Ninguna palabra que contar | ✅ idéntico |
| Dos palabras de un carácter | 3 | Más hilos que bytes | ✅ idéntico |
| Palabras repetidas | 16 | Acumulación entre bloques | ✅ idéntico |
| Mayúsculas y minúsculas | 21 | Normalización a minúscula | ✅ idéntico |
| Sin salto de línea final | 15 | Última palabra al borde del bloque | ✅ idéntico |

Los casos de 3 y 4 bytes son los más exigentes: con 8 hilos varios reciben bloques
vacíos y el corte por frontera de palabra puede dejar bloques de longitud cero. El
programa los maneja sin fallar y sin perder ni duplicar palabras.

```bash
./verificar.sh archivo.txt    # reproduce ambas pruebas
```

---

## 2. Qué se midió exactamente

La medición cubre **la misma parte del algoritmo en ambas versiones**: la fase de
conteo de palabras. Queda **fuera** de la medición la lectura del archivo desde
disco, la impresión de la tabla y la liberación de memoria, para que el tiempo
comparado sea únicamente el trabajo de cómputo.

| | Secuencial | Paralela |
|---|---|---|
| **Fuera** del cronómetro | Lectura del archivo a memoria | Lectura del archivo a memoria |
| **Dentro** del cronómetro | Recorrer todo el texto → tokenizar → acumular en la tabla | 1) Repartir el texto en N bloques<br>2) Crear N hilos; cada uno cuenta su bloque en una tabla **privada**<br>3) `pthread_join` de los N hilos<br>4) **Reducción**: fusionar las N tablas privadas en la tabla final |
| **Fuera** del cronómetro | Ordenar e imprimir | Ordenar e imprimir |

Ambas versiones invocan la **misma función** `contar_palabras(texto, inicio, fin, tabla)`.
La secuencial la llama una vez sobre `[0, tamaño)`; la paralela la llama desde cada
hilo sobre su bloque. Así, cualquier diferencia de tiempo proviene del paralelismo
y no de un cambio de algoritmo.

> **Nota de diseño:** los cortes entre bloques se avanzan hasta el siguiente
> separador para que ninguna palabra quede partida entre dos hilos. Cada hilo
> escribe solo en su tabla privada, por lo que **no hay locks ni contención**
> durante la fase paralela; todo el costo de sincronización se concentra en la
> reducción final.

---

## 3. Tabla de tiempos — 5 ejecuciones

### 3.1 Archivo principal (`archivo.txt`, 24,530 bytes)

| NUM. | TIEMPO SECUENCIAL (s) | TIEMPO PARALELA 2 HILOS (s) | TIEMPO PARALELA 4 HILOS (s) |
|:---:|---:|---:|---:|
| 1 | 0.004635 | 0.003043 | 0.002097 |
| 2 | 0.004826 | 0.002977 | 0.001848 |
| 3 | 0.003230 | 0.002034 | 0.001863 |
| 4 | 0.002752 | 0.001510 | 0.001490 |
| 5 | 0.002447 | 0.001376 | 0.001426 |
| **PROMEDIO** | **0.003578** | **0.002188** | **0.001745** |

### 3.2 Archivo complementario (`archivo_grande.txt`, 981,240 bytes)

| NUM. | TIEMPO SECUENCIAL (s) | TIEMPO PARALELA 2 HILOS (s) | TIEMPO PARALELA 4 HILOS (s) |
|:---:|---:|---:|---:|
| 1 | 0.078007 | 0.046513 | 0.024097 |
| 2 | 0.069338 | 0.047642 | 0.026287 |
| 3 | 0.077322 | 0.041301 | 0.022825 |
| 4 | 0.065508 | 0.038404 | 0.023097 |
| 5 | 0.067785 | 0.037561 | 0.027518 |
| **PROMEDIO** | **0.071592** | **0.042284** | **0.024765** |

---

## 4. Cálculo del Speedup

$$S_p = \frac{T_{secuencial}}{T_{paralelo}}$$

### 4.1 Archivo principal

| NUM. | SPEEDUP 2 HILOS | SPEEDUP 4 HILOS |
|:---:|---:|---:|
| 1 | 1.5232 | 2.2103 |
| 2 | 1.6211 | 2.6115 |
| 3 | 1.5880 | 1.7338 |
| 4 | 1.8225 | 1.8470 |
| 5 | 1.7783 | 1.7160 |
| **Con los tiempos promedio** | **1.6353** | **2.0504** |

Cálculo con los promedios:

- $S_2 = 0.003578 / 0.002188 = \mathbf{1.6353}$
- $S_4 = 0.003578 / 0.001745 = \mathbf{2.0504}$

### 4.2 Archivo complementario

| NUM. | SPEEDUP 2 HILOS | SPEEDUP 4 HILOS |
|:---:|---:|---:|
| 1 | 1.6771 | 3.2372 |
| 2 | 1.4554 | 2.6377 |
| 3 | 1.8722 | 3.3876 |
| 4 | 1.7058 | 2.8362 |
| 5 | 1.8047 | 2.4633 |
| **Con los tiempos promedio** | **1.6931** | **2.8909** |

- $S_2 = 0.071592 / 0.042284 = \mathbf{1.6931}$
- $S_4 = 0.071592 / 0.024765 = \mathbf{2.8909}$

---

## 5. Cálculo de la Efficiency

$$E_p = \frac{S_p}{p}$$

### 5.1 Archivo principal

| NUM. | EFFICIENCY 2 HILOS | EFFICIENCY 4 HILOS |
|:---:|---:|---:|
| 1 | 0.7616 (76.16 %) | 0.5526 (55.26 %) |
| 2 | 0.8105 (81.05 %) | 0.6529 (65.29 %) |
| 3 | 0.7940 (79.40 %) | 0.4334 (43.34 %) |
| 4 | 0.9113 (91.13 %) | 0.4617 (46.17 %) |
| 5 | 0.8892 (88.92 %) | 0.4290 (42.90 %) |
| **Con los tiempos promedio** | **0.8176 (81.76 %)** | **0.5126 (51.26 %)** |

- $E_2 = 1.6353 / 2 = \mathbf{0.8176}$
- $E_4 = 2.0504 / 4 = \mathbf{0.5126}$

### 5.2 Archivo complementario

| NUM. | EFFICIENCY 2 HILOS | EFFICIENCY 4 HILOS |
|:---:|---:|---:|
| 1 | 0.8386 (83.86 %) | 0.8093 (80.93 %) |
| 2 | 0.7277 (72.77 %) | 0.6594 (65.94 %) |
| 3 | 0.9361 (93.61 %) | 0.8469 (84.69 %) |
| 4 | 0.8529 (85.29 %) | 0.7091 (70.91 %) |
| 5 | 0.9023 (90.23 %) | 0.6158 (61.58 %) |
| **Con los tiempos promedio** | **0.8466 (84.66 %)** | **0.7227 (72.27 %)** |

- $E_2 = 1.6931 / 2 = \mathbf{0.8466}$
- $E_4 = 2.8909 / 4 = \mathbf{0.7227}$

---

## 6. Tabla final de resultados

### Archivo principal (`archivo.txt`, 24 KB)

| Configuración | Tiempo promedio (s) | Speedup | Efficiency |
|---|---:|---:|---:|
| Secuencial (1 hilo) | 0.003578 | 1.0000 | 100.00 % |
| Paralela — 2 hilos | 0.002188 | 1.6353 | 81.76 % |
| Paralela — 4 hilos | 0.001745 | 2.0504 | 51.26 % |

### Archivo complementario (`archivo_grande.txt`, 958 KB)

| Configuración | Tiempo promedio (s) | Speedup | Efficiency |
|---|---:|---:|---:|
| Secuencial (1 hilo) | 0.071592 | 1.0000 | 100.00 % |
| Paralela — 2 hilos | 0.042284 | 1.6931 | 84.66 % |
| Paralela — 4 hilos | 0.024765 | 2.8909 | 72.27 % |

### Comparación visual del speedup

```
Speedup ideal      2 hilos: ████████████████████ 2.00   4 hilos: ████████████████████████████████████████ 4.00

archivo.txt        2 hilos: ████████████████▎    1.64   4 hilos: ████████████████████▌                    2.05
archivo_grande.txt 2 hilos: ████████████████▉    1.69   4 hilos: ████████████████████████████▉            2.89
```

---

## 7. Análisis de resultados

### 7.1 ¿Con qué cantidad de procesos o hilos obtuvieron el mayor speedup?

**Con 4 hilos**, en ambos archivos. En `archivo.txt` el speedup pasó de 1.6353 (2 hilos)
a 2.0504 (4 hilos), y en `archivo_grande.txt` de 1.6931 a 2.8909. El mejor resultado
absoluto fue **2.8909× con 4 hilos sobre el archivo grande**.

Nótese, sin embargo, que el salto de 2 a 4 hilos rindió mucho menos de lo esperado:
duplicar los hilos debería duplicar el speedup, pero en el archivo pequeño solo lo
aumentó un 25 % (1.64 → 2.05), y en el grande un 71 % (1.69 → 2.89).

### 7.2 ¿Con qué configuración obtuvieron la mayor eficiencia?

**Con 2 hilos**: 81.76 % en el archivo pequeño y 84.66 % en el grande. En las dos
pruebas la eficiencia con 2 hilos superó a la de 4 hilos. La peor eficiencia se dio
con **4 hilos sobre el archivo pequeño (51.26 %)**: la mitad de la capacidad de cómputo
asignada se desperdició en overhead.

Esto ilustra la tensión clásica del cómputo paralelo: **la configuración más rápida
(4 hilos) no es la más eficiente (2 hilos)**. Con 2 hilos se aprovecha mejor cada
núcleo asignado; con 4 hilos se termina antes, pero se paga con recursos ociosos.

### 7.3 ¿El speedup aumentó proporcionalmente al incrementar la cantidad de hilos?

**No.** El crecimiento fue claramente **sublineal** y se alejó del ideal a medida que
se agregaron hilos:

| Hilos | Speedup ideal | archivo.txt | archivo_grande.txt |
|:---:|---:|---:|---:|
| 2 | 2.00 | 1.64 (82 % del ideal) | 1.69 (85 % del ideal) |
| 4 | 4.00 | 2.05 (51 % del ideal) | 2.89 (72 % del ideal) |

Con 2 hilos se alcanzó ~82–85 % del ideal, pero con 4 hilos solo 51–72 %. La brecha
respecto al speedup lineal **se ensancha** conforme crece el número de hilos, que es
exactamente lo que predice la **ley de Amdahl**: la porción secuencial del programa
(en nuestro caso, la fusión de las tablas privadas) impone un techo al speedup
alcanzable sin importar cuántos hilos se agreguen.

### 7.4 ¿La eficiencia aumentó o disminuyó al utilizar más recursos?

**Disminuyó de forma consistente** en las dos pruebas:

- `archivo.txt`: 81.76 % (2 hilos) → 51.26 % (4 hilos) — **caída de 30.5 puntos**
- `archivo_grande.txt`: 84.66 % (2 hilos) → 72.27 % (4 hilos) — **caída de 12.4 puntos**

La razón es que el overhead (creación de hilos, reparto del texto, reducción final)
**crece con el número de hilos**, mientras que el trabajo útil por hilo **se reduce**.
La relación trabajo-útil / overhead empeora en cada paso.

Es revelador comparar las dos caídas: con el archivo grande la pérdida de eficiencia
fue **menos de la mitad** que con el pequeño, porque hay mucho más trabajo real entre
el cual repartir el mismo costo fijo de coordinación.

### 7.5 ¿Qué factores consideran que pudieron afectar el tiempo de ejecución?

1. **Tamaño del archivo (el factor más determinante).** Fue el efecto más marcado de
   todo el experimento. Con 24 KB, el trabajo por hilo es tan pequeño que el costo de
   crear hilos y fusionar tablas pesa casi tanto como el conteo mismo (E₄ = 51 %). Al
   pasar a 958 KB —40× más texto— la eficiencia con 4 hilos subió a 72 % **sin cambiar
   una sola línea de código**. El paralelismo necesita un problema suficientemente
   grande para amortizar su costo de entrada.

2. **Arquitectura heterogénea del procesador.** El Apple M5 tiene 4 núcleos de
   rendimiento (P) y 6 de eficiencia (E), que **no** son igual de rápidos. Si el
   planificador del sistema coloca alguno de los hilos en un núcleo E, ese hilo tarda
   más y los demás deben **esperarlo en el `pthread_join`**. El tiempo total lo marca
   el hilo más lento, no el promedio.

3. **Variabilidad del sistema operativo.** Los tiempos de una misma configuración
   varían de forma notable: la ejecución secuencial del archivo pequeño osciló entre
   0.002447 s y 0.004826 s (una diferencia de casi 2×). Esto se debe a otros procesos
   compitiendo por CPU, al planificador expulsando hilos y a los cambios dinámicos de
   frecuencia del procesador. **Por eso se promedian 5 corridas** en lugar de confiar
   en una sola medición.

4. **Efectos de caché y calentamiento.** Las primeras corridas son sistemáticamente
   más lentas (0.004635 s la #1 frente a 0.002447 s la #5): el texto y las tablas aún
   no están en caché, y el procesador todavía no ha escalado su frecuencia.

5. **Desbalance de carga.** Los bloques se reparten por **bytes**, no por palabras. Un
   bloque con palabras más largas contiene menos palabras que uno con palabras cortas,
   de modo que los hilos no reciben exactamente la misma cantidad de trabajo.

6. **El algoritmo de la tabla es O(n²).** `agregar_palabra` recorre linealmente la
   tabla buscando cada palabra. Con 904 palabras distintas, cada inserción cuesta
   hasta 904 comparaciones `strcmp`. Este costo cuadrático es, paradójicamente, lo que
   hace que valga la pena paralelizar: hay suficiente cómputo que repartir.

### 7.6 ¿Qué posibles fuentes de overhead identifican en su programa?

| Fuente de overhead | Dónde ocurre | Impacto |
|---|---|---|
| **Reducción de las tablas privadas** ⭐ | Fusionar N tablas en una sola al final | **La principal.** Es 100 % secuencial y crece con N: con 4 hilos hay que fusionar 3 tablas de hasta 904 palabras cada una, y cada inserción hace búsqueda lineal O(904). Es el techo de Amdahl del programa. |
| **Creación y destrucción de hilos** | `pthread_create` / `pthread_join` | Cada hilo cuesta decenas de microsegundos en crearse. Con un archivo de 3.5 ms de trabajo total, 4 hilos representan un costo fijo nada despreciable. |
| **Barrera implícita del `join`** | Espera a que terminen todos los hilos | El tiempo lo dicta el hilo **más lento**; los demás quedan ociosos. Se agrava con el desbalance de carga y con los núcleos heterogéneos. |
| **Trabajo duplicado en memoria** | Cada hilo mantiene su propia tabla | Con 4 hilos existen 4 tablas de hasta 904 entradas: 4× el uso de memoria y 4× las llamadas a `malloc`/`realloc`. |
| **Contención en el asignador de memoria** | `malloc`, `realloc`, `strdup` dentro de los hilos | El asignador del sistema usa locks internos; varios hilos pidiendo memoria a la vez se serializan parcialmente sin que el código lo note. |
| **Cálculo de los cortes** | Ajustar fronteras a límite de palabra | Costo menor, pero es trabajo que la versión secuencial **no** realiza en absoluto. |
| **False sharing** | Estructuras `TareaHilo` contiguas en el arreglo | Estructuras de distintos hilos pueden caer en la misma línea de caché, provocando invalidaciones cruzadas. |

Es importante notar que la fuente de overhead que **evitamos** también explica los
buenos resultados con 2 hilos: al darle a cada hilo una tabla privada en vez de una
tabla compartida con mutex, la fase paralela queda **libre de contención**. Una
implementación con un solo mutex global sobre la tabla habría serializado el programa
casi por completo y probablemente habría resultado *más lenta* que la secuencial.

### 7.7 ¿Agregar más procesos o hilos garantiza siempre un mejor rendimiento? Justifiquen.

**No, definitivamente no.** Nuestros datos lo demuestran en tres niveles:

**a) El rendimiento mejora, pero cada vez menos.** Al duplicar de 2 a 4 hilos en el
archivo pequeño, el tiempo bajó apenas de 0.002188 s a 0.001745 s: **duplicamos los
recursos para ganar solo 20 % de tiempo**. El segundo par de hilos aportó una fracción
mínima de lo que aportó el primero.

**b) La eficiencia se derrumba.** Pasar de 2 a 4 hilos hundió la eficiencia de 81.76 %
a 51.26 % en el archivo pequeño. En términos prácticos: con 4 hilos, **casi la mitad
de la capacidad de cómputo asignada se desperdició** en coordinación. Si el criterio
fuera el uso racional de recursos, la configuración de 2 hilos es la mejor decisión.

**c) Hay ejecuciones individuales donde 4 hilos fue *más lento* que 2.** No es solo un
promedio que se degrada — en el archivo pequeño, la corrida #5 dio 0.001376 s con 2
hilos frente a 0.001426 s con 4 hilos, y la corrida #4 fue prácticamente un empate
(0.001510 s vs 0.001490 s). Agregar hilos allí **no aportó absolutamente nada**.

**La conclusión.** El número óptimo de hilos depende de la relación entre el trabajo
útil y el overhead, no del número de núcleos disponibles. Nuestro procesador tiene 10
núcleos, pero con `archivo.txt` ya a los 4 hilos la eficiencia estaba por debajo del
52 %; usar 10 hilos sobre 24 KB de texto sería contraproducente, porque el costo de
crear y fusionar 10 tablas superaría el ahorro del conteo.

El propio experimento sugiere la regla práctica: **el mismo código con 4 hilos alcanzó
51 % de eficiencia con 24 KB y 72 % con 958 KB**. No fue el paralelismo lo que cambió,
sino cuánto trabajo útil había para repartir. Más hilos ayudan solo mientras exista
trabajo suficiente para mantenerlos ocupados; pasado ese punto, la ley de Amdahl y el
overhead de coordinación cobran su precio.

---

## 8. Reproducción de los resultados

```bash
gcc -O2 -Wall -o conteo_secuencial conteo_frecuencia_secuencial.c
gcc -O2 -Wall -pthread -o conteo_paralelo conteo_frecuencia_paralelo.c

./conteo_secuencial archivo.txt --silencioso
./conteo_paralelo   archivo.txt 2 --silencioso
./conteo_paralelo   archivo.txt 4 --silencioso

# Las 5 corridas, promedios, speedup y efficiency de forma automática:
./benchmark.sh archivo.txt 5
./benchmark.sh archivo_grande.txt 5
```

Los tiempos crudos de cada corrida están en `resultados_archivo.csv` y
`resultados_grande.csv`.
