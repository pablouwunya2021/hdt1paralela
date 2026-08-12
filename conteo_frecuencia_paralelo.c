/*
 * HDT 1 - Computacion Paralela y Distribuida
 * Version PARALELA (POSIX threads) del conteo de frecuencia de palabras,
 * instrumentada para medir el tiempo de la fase de conteo.
 *
 * Estrategia:
 *   1. El texto se divide en N bloques contiguos; cada frontera se corre hacia
 *      adelante hasta un separador para no partir una palabra a la mitad.
 *   2. Cada hilo cuenta su bloque en una tabla PRIVADA (sin locks -> sin
 *      contencion durante la fase paralela).
 *   3. El hilo principal fusiona las N tablas privadas en la tabla final.
 *      Esta reduccion es la porcion secuencial del algoritmo (Amdahl).
 *
 * Compilacion:
 *     gcc -O2 -pthread -o conteo_paralelo conteo_frecuencia_paralelo.c
 *
 * Uso:
 *     ./conteo_paralelo archivo.txt [num_hilos] [--silencioso]
 */

#include <ctype.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_HILOS 64

typedef struct {
    char *palabra;
    size_t frecuencia;
} EntradaFrecuencia;

typedef struct {
    EntradaFrecuencia *entradas;
    size_t cantidad;
    size_t capacidad;
} TablaFrecuencias;

typedef struct {
    const char *texto;
    size_t inicio;
    size_t fin;
    TablaFrecuencias tabla; /* tabla privada del hilo */
    int ok;
} TareaHilo;

static char *duplicar_cadena(const char *texto)
{
    size_t longitud = strlen(texto) + 1;
    char *copia = malloc(longitud);

    if (copia != NULL) {
        memcpy(copia, texto, longitud);
    }

    return copia;
}

static int inicializar_tabla(TablaFrecuencias *tabla)
{
    tabla->cantidad = 0;
    tabla->capacidad = 16;
    tabla->entradas = malloc(tabla->capacidad * sizeof(*tabla->entradas));
    return tabla->entradas != NULL;
}

static void liberar_tabla(TablaFrecuencias *tabla)
{
    size_t i;

    for (i = 0; i < tabla->cantidad; i++) {
        free(tabla->entradas[i].palabra);
    }

    free(tabla->entradas);
    tabla->entradas = NULL;
    tabla->cantidad = 0;
    tabla->capacidad = 0;
}

/* Suma 'veces' ocurrencias de 'palabra' a la tabla. */
static int agregar_palabra(TablaFrecuencias *tabla, const char *palabra,
                           size_t veces)
{
    size_t i;

    for (i = 0; i < tabla->cantidad; i++) {
        if (strcmp(tabla->entradas[i].palabra, palabra) == 0) {
            tabla->entradas[i].frecuencia += veces;
            return 1;
        }
    }

    if (tabla->cantidad == tabla->capacidad) {
        size_t nueva_capacidad = tabla->capacidad * 2;
        EntradaFrecuencia *nuevas_entradas =
            realloc(tabla->entradas,
                    nueva_capacidad * sizeof(*nuevas_entradas));

        if (nuevas_entradas == NULL) {
            return 0;
        }

        tabla->entradas = nuevas_entradas;
        tabla->capacidad = nueva_capacidad;
    }

    tabla->entradas[tabla->cantidad].palabra = duplicar_cadena(palabra);
    if (tabla->entradas[tabla->cantidad].palabra == NULL) {
        return 0;
    }

    tabla->entradas[tabla->cantidad].frecuencia = veces;
    tabla->cantidad++;
    return 1;
}

static int es_caracter_de_palabra(unsigned char caracter)
{
    return isalnum(caracter) || caracter >= 128;
}

/*
 * ---------------------------------------------------------------------------
 * Misma funcion de conteo que la version secuencial (alli se invoca sobre todo
 * el texto; aqui cada hilo la invoca sobre su bloque [inicio, fin)).
 * ---------------------------------------------------------------------------
 */
static int contar_palabras(const char *texto, size_t inicio, size_t fin,
                           TablaFrecuencias *tabla)
{
    char *palabra;
    size_t longitud = 0;
    size_t capacidad = 32;
    size_t i;

    palabra = malloc(capacidad);
    if (palabra == NULL) {
        return 0;
    }

    for (i = inicio; i < fin; i++) {
        unsigned char actual = (unsigned char)texto[i];

        if (es_caracter_de_palabra(actual)) {
            if (longitud + 1 >= capacidad) {
                size_t nueva_capacidad = capacidad * 2;
                char *nueva_palabra = realloc(palabra, nueva_capacidad);

                if (nueva_palabra == NULL) {
                    free(palabra);
                    return 0;
                }

                palabra = nueva_palabra;
                capacidad = nueva_capacidad;
            }

            palabra[longitud++] =
                actual < 128 ? (char)tolower(actual) : (char)actual;
        } else if (longitud > 0) {
            palabra[longitud] = '\0';

            if (!agregar_palabra(tabla, palabra, 1)) {
                free(palabra);
                return 0;
            }

            longitud = 0;
        }
    }

    if (longitud > 0) {
        palabra[longitud] = '\0';
        if (!agregar_palabra(tabla, palabra, 1)) {
            free(palabra);
            return 0;
        }
    }

    free(palabra);
    return 1;
}

static void *trabajo_hilo(void *argumento)
{
    TareaHilo *tarea = argumento;
    tarea->ok = contar_palabras(tarea->texto, tarea->inicio, tarea->fin,
                                &tarea->tabla);
    return NULL;
}

static int comparar_entradas(const void *a, const void *b)
{
    const EntradaFrecuencia *entrada_a = a;
    const EntradaFrecuencia *entrada_b = b;
    return strcmp(entrada_a->palabra, entrada_b->palabra);
}

static void mostrar_tabla(TablaFrecuencias *tabla)
{
    size_t i;

    qsort(tabla->entradas, tabla->cantidad, sizeof(*tabla->entradas),
          comparar_entradas);

    printf("\n%-30s %s\n", "Palabra", "Frecuencia");
    printf("%-30s %s\n", "------------------------------", "----------");

    for (i = 0; i < tabla->cantidad; i++) {
        printf("%-30s %zu\n",
               tabla->entradas[i].palabra,
               tabla->entradas[i].frecuencia);
    }
}

static char *leer_archivo(const char *nombre, size_t *tamano)
{
    FILE *archivo = fopen(nombre, "rb");
    char *contenido;
    long bytes;

    if (archivo == NULL) {
        return NULL;
    }

    if (fseek(archivo, 0, SEEK_END) != 0) {
        fclose(archivo);
        return NULL;
    }

    bytes = ftell(archivo);
    if (bytes < 0) {
        fclose(archivo);
        return NULL;
    }

    rewind(archivo);

    contenido = malloc((size_t)bytes + 1);
    if (contenido == NULL) {
        fclose(archivo);
        return NULL;
    }

    if (fread(contenido, 1, (size_t)bytes, archivo) != (size_t)bytes) {
        free(contenido);
        fclose(archivo);
        return NULL;
    }

    contenido[bytes] = '\0';
    *tamano = (size_t)bytes;
    fclose(archivo);
    return contenido;
}

static double segundos_transcurridos(struct timespec inicio,
                                     struct timespec fin)
{
    return (double)(fin.tv_sec - inicio.tv_sec) +
           (double)(fin.tv_nsec - inicio.tv_nsec) / 1e9;
}

int main(int argc, char *argv[])
{
    const char *nombre_archivo;
    char nombre_ingresado[1024];
    char *texto;
    size_t tamano = 0;
    int num_hilos = 4;
    int silencioso = 0;
    int i;
    pthread_t hilos[MAX_HILOS];
    TareaHilo tareas[MAX_HILOS];
    struct timespec inicio, fin;
    double tiempo;
    int error = 0;

    if (argc >= 2) {
        nombre_archivo = argv[1];
    } else {
        printf("Ingrese el nombre del archivo .txt: ");
        if (fgets(nombre_ingresado, sizeof(nombre_ingresado), stdin) == NULL) {
            fprintf(stderr, "Error: no se pudo leer el nombre del archivo.\n");
            return EXIT_FAILURE;
        }

        nombre_ingresado[strcspn(nombre_ingresado, "\r\n")] = '\0';
        nombre_archivo = nombre_ingresado;
    }

    if (argc >= 3 && strcmp(argv[2], "--silencioso") != 0) {
        num_hilos = atoi(argv[2]);
    }

    for (i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--silencioso") == 0) {
            silencioso = 1;
        }
    }

    if (num_hilos < 1 || num_hilos > MAX_HILOS) {
        fprintf(stderr, "Error: la cantidad de hilos debe estar entre 1 y %d.\n",
                MAX_HILOS);
        return EXIT_FAILURE;
    }

    texto = leer_archivo(nombre_archivo, &tamano);
    if (texto == NULL) {
        fprintf(stderr, "Error: no se pudo abrir o leer '%s'.\n",
                nombre_archivo);
        return EXIT_FAILURE;
    }

    /* ================= INICIO DE LA MEDICION ================= */
    clock_gettime(CLOCK_MONOTONIC, &inicio);

    /* 1. Reparto del texto en bloques alineados a frontera de palabra. */
    {
        size_t corte_anterior = 0;

        for (i = 0; i < num_hilos; i++) {
            size_t corte;

            if (i == num_hilos - 1) {
                corte = tamano;
            } else {
                corte = tamano * (size_t)(i + 1) / (size_t)num_hilos;

                /* Avanzar hasta el siguiente separador para no partir palabras. */
                while (corte < tamano &&
                       es_caracter_de_palabra((unsigned char)texto[corte])) {
                    corte++;
                }
            }

            if (corte < corte_anterior) {
                corte = corte_anterior;
            }

            tareas[i].texto = texto;
            tareas[i].inicio = corte_anterior;
            tareas[i].fin = corte;
            tareas[i].ok = 0;

            if (!inicializar_tabla(&tareas[i].tabla)) {
                error = 1;
            }

            corte_anterior = corte;
        }
    }

    if (error) {
        fprintf(stderr, "Error: no hay memoria suficiente.\n");
        free(texto);
        return EXIT_FAILURE;
    }

    /* 2. Fase paralela: cada hilo cuenta su bloque en su tabla privada. */
    for (i = 0; i < num_hilos; i++) {
        if (pthread_create(&hilos[i], NULL, trabajo_hilo, &tareas[i]) != 0) {
            fprintf(stderr, "Error: no se pudo crear el hilo %d.\n", i);
            free(texto);
            return EXIT_FAILURE;
        }
    }

    for (i = 0; i < num_hilos; i++) {
        pthread_join(hilos[i], NULL);
        if (!tareas[i].ok) {
            error = 1;
        }
    }

    /* 3. Reduccion: fusionar las tablas privadas en la del hilo 0. */
    for (i = 1; i < num_hilos && !error; i++) {
        size_t j;

        for (j = 0; j < tareas[i].tabla.cantidad; j++) {
            if (!agregar_palabra(&tareas[0].tabla,
                                 tareas[i].tabla.entradas[j].palabra,
                                 tareas[i].tabla.entradas[j].frecuencia)) {
                error = 1;
                break;
            }
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &fin);
    /* ================== FIN DE LA MEDICION =================== */

    tiempo = segundos_transcurridos(inicio, fin);

    if (error) {
        fprintf(stderr, "Error: no se pudo procesar el texto.\n");
        for (i = 0; i < num_hilos; i++) {
            liberar_tabla(&tareas[i].tabla);
        }
        free(texto);
        return EXIT_FAILURE;
    }

    if (!silencioso) {
        mostrar_tabla(&tareas[0].tabla);
    }

    printf("\n=== VERSION PARALELA (%d hilos) ===\n", num_hilos);
    printf("Archivo procesado      : %s (%zu bytes)\n", nombre_archivo, tamano);
    printf("Palabras diferentes    : %zu\n", tareas[0].tabla.cantidad);
    printf("TIEMPO DE CONTEO       : %.6f segundos\n", tiempo);

    for (i = 0; i < num_hilos; i++) {
        liberar_tabla(&tareas[i].tabla);
    }

    free(texto);
    return EXIT_SUCCESS;
}
