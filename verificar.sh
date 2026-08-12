#!/bin/bash
# ---------------------------------------------------------------------------
# HDT 1 - Computacion Paralela y Distribuida
# Verifica el requisito del enunciado:
#   "Ejecuten ambas versiones con el mismo archivo de prueba y verifiquen que
#    produzcan exactamente las mismas palabras y frecuencias."
#
# Compara la salida de la version paralela contra la secuencial con distintas
# cantidades de hilos y con archivos de casos borde.
#
# Uso:  ./verificar.sh [archivo.txt]
# ---------------------------------------------------------------------------

set -e

ARCHIVO="${1:-archivo.txt}"
HILOS="1 2 3 4 5 7 8 16 32"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

fallos=0

echo ">>> Compilando..."
gcc -O2 -Wall -o conteo_secuencial conteo_frecuencia_secuencial.c
gcc -O2 -Wall -pthread -o conteo_paralelo conteo_frecuencia_paralelo.c

# Extrae solo la tabla de frecuencias, sin el bloque de tiempos.
tabla_de() {
    sed -n '/^Palabra /,/^$/p'
}

# ---------------------------------------------------------------------------
echo ""
echo "=============================================================="
echo " PRUEBA 1: misma salida con distinta cantidad de hilos"
echo " Archivo: $ARCHIVO"
echo "=============================================================="

./conteo_secuencial "$ARCHIVO" | tabla_de > "$TMP/base.tab"
palabras=$(( $(grep -c . "$TMP/base.tab") - 2 ))
echo "Referencia secuencial: $palabras palabras distintas"
echo ""

for n in $HILOS; do
    ./conteo_paralelo "$ARCHIVO" "$n" | tabla_de > "$TMP/n$n.tab"

    if diff -q "$TMP/base.tab" "$TMP/n$n.tab" > /dev/null; then
        printf "  %2s hilos ... IDENTICO\n" "$n"
    else
        printf "  %2s hilos ... *** DIFERENTE ***\n" "$n"
        diff "$TMP/base.tab" "$TMP/n$n.tab" | head -10
        fallos=$((fallos + 1))
    fi
done

# ---------------------------------------------------------------------------
echo ""
echo "=============================================================="
echo " PRUEBA 2: casos borde"
echo "=============================================================="

printf ''                      > "$TMP/vacio.txt"
printf 'hola'                  > "$TMP/una.txt"
printf '   \n\t  '             > "$TMP/blancos.txt"
printf 'a b'                   > "$TMP/dos.txt"
printf 'perro gato perro'      > "$TMP/repetidas.txt"
printf 'nino arbol NINO Arbol' > "$TMP/casos.txt"
printf 'final sin salto'       > "$TMP/sinsalto.txt"

for caso in vacio una blancos dos repetidas casos sinsalto; do
    ruta="$TMP/$caso.txt"
    bytes=$(wc -c < "$ruta" | tr -d ' ')
    ./conteo_secuencial "$ruta" | tabla_de > "$TMP/c_base.tab"
    estado="IDENTICO"

    # Se prueba con mas hilos que bytes: algunos reciben bloques vacios.
    for n in 1 2 4 8; do
        ./conteo_paralelo "$ruta" "$n" | tabla_de > "$TMP/c_$n.tab"
        if ! diff -q "$TMP/c_base.tab" "$TMP/c_$n.tab" > /dev/null; then
            estado="*** DIFERENTE con $n hilos ***"
            fallos=$((fallos + 1))
        fi
    done

    printf "  %-12s %5s bytes ... %s\n" "$caso.txt" "$bytes" "$estado"
done

# ---------------------------------------------------------------------------
echo ""
echo "=============================================================="
if [ "$fallos" -eq 0 ]; then
    echo " RESULTADO: todas las pruebas pasaron."
    echo " La version paralela produce exactamente las mismas palabras y"
    echo " frecuencias que la secuencial en toda configuracion probada."
    echo "=============================================================="
    exit 0
else
    echo " RESULTADO: $fallos prueba(s) fallaron."
    echo "=============================================================="
    exit 1
fi
