/*
 * HDT 1 - Computacion Paralela y Distribuida
 * Version SECUENCIAL del conteo de frecuencia de palabras (base: Corto 02),
 * instrumentada para medir el tiempo de la fase de conteo.
 *
 * Compilacion:
 *     gcc -O2 -o conteo_secuencial conteo_frecuencia_secuencial.c
 *
 * Uso:
 *     ./conteo_secuencial archivo.txt [--silencioso]
 */

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef struct {
    char *palabra;
    size_t frecuencia;
} EntradaFrecuencia;

typedef struct {
    EntradaFrecuencia *entradas;
    size_t cantidad;
    size_t capacidad;
} TablaFrecuencias;

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

    /* Buscar la palabra en la tabla. */
    for (i = 0; i < tabla->cantidad; i++) {
        if (strcmp(tabla->entradas[i].palabra, palabra) == 0) {
            tabla->entradas[i].frecuencia += veces;
            return 1;
        }
    }

    /* Ampliar la tabla si ya no tiene espacio. */
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
    /* Los bytes >= 128 permiten conservar letras acentuadas en UTF-8. */
    return isalnum(caracter) || caracter >= 128;
}

/*
 * ---------------------------------------------------------------------------
 * REGION MEDIDA: esta es exactamente la misma funcion de conteo que ejecuta
 * cada hilo en la version paralela, para que los tiempos sean comparables.
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

            /* La conversion a minuscula se aplica a caracteres ASCII. */
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

    /* Agregar la ultima palabra si el bloque no termina con separador. */
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

/* Lee todo el archivo a memoria. La E/S queda FUERA de la region medida. */
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
    TablaFrecuencias tabla;
    struct timespec inicio, fin;
    double tiempo;
    int silencioso = 0;
    int i;

    for (i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--silencioso") == 0) {
            silencioso = 1;
        }
    }

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

    texto = leer_archivo(nombre_archivo, &tamano);
    if (texto == NULL) {
        fprintf(stderr, "Error: no se pudo abrir o leer '%s'.\n",
                nombre_archivo);
        return EXIT_FAILURE;
    }

    if (!inicializar_tabla(&tabla)) {
        fprintf(stderr, "Error: no hay memoria suficiente.\n");
        free(texto);
        return EXIT_FAILURE;
    }

    /* ================= INICIO DE LA MEDICION ================= */
    clock_gettime(CLOCK_MONOTONIC, &inicio);

    if (!contar_palabras(texto, 0, tamano, &tabla)) {
        clock_gettime(CLOCK_MONOTONIC, &fin);
        fprintf(stderr, "Error: no se pudo procesar el texto.\n");
        liberar_tabla(&tabla);
        free(texto);
        return EXIT_FAILURE;
    }

    clock_gettime(CLOCK_MONOTONIC, &fin);
    /* ================== FIN DE LA MEDICION =================== */

    tiempo = segundos_transcurridos(inicio, fin);

    if (!silencioso) {
        mostrar_tabla(&tabla);
    }

    printf("\n=== VERSION SECUENCIAL ===\n");
    printf("Archivo procesado      : %s (%zu bytes)\n", nombre_archivo, tamano);
    printf("Palabras diferentes    : %zu\n", tabla.cantidad);
    printf("TIEMPO DE CONTEO       : %.6f segundos\n", tiempo);

    liberar_tabla(&tabla);
    free(texto);
    return EXIT_SUCCESS;
}
