#!/bin/bash
# ---------------------------------------------------------------------------
# HDT 1 - Computacion Paralela y Distribuida
# Ejecuta 5 corridas de cada configuracion (secuencial, 2 hilos, 4 hilos)
# sobre el MISMO archivo de texto y calcula promedio, speedup y efficiency.
#
# Uso:  ./benchmark.sh [archivo.txt] [repeticiones]
# ---------------------------------------------------------------------------

set -e

ARCHIVO="${1:-archivo.txt}"
REPS="${2:-5}"
SALIDA="resultados.csv"

if [ ! -f "$ARCHIVO" ]; then
    echo "Error: no existe el archivo '$ARCHIVO'."
    exit 1
fi

echo ">>> Compilando..."
gcc -O2 -Wall -o conteo_secuencial conteo_frecuencia_secuencial.c
gcc -O2 -Wall -pthread -o conteo_paralelo conteo_frecuencia_paralelo.c

# Extrae el tiempo impreso por el programa.
tiempo_de() {
    grep "TIEMPO DE CONTEO" | awk '{print $5}'
}

echo ">>> Archivo de prueba: $ARCHIVO ($(wc -c < "$ARCHIVO" | tr -d ' ') bytes)"
echo ">>> Repeticiones por configuracion: $REPS"
echo ""

declare -a T_SEC T_P2 T_P4

printf "%-6s %-22s %-22s %-22s\n" "NUM." "T. SECUENCIAL (s)" "T. PARALELA 2 HILOS (s)" "T. PARALELA 4 HILOS (s)"
printf "%-6s %-22s %-22s %-22s\n" "-----" "---------------------" "-----------------------" "-----------------------"

for ((i = 1; i <= REPS; i++)); do
    ts=$(./conteo_secuencial "$ARCHIVO" --silencioso | tiempo_de)
    t2=$(./conteo_paralelo "$ARCHIVO" 2 --silencioso | tiempo_de)
    t4=$(./conteo_paralelo "$ARCHIVO" 4 --silencioso | tiempo_de)

    T_SEC[$i]=$ts
    T_P2[$i]=$t2
    T_P4[$i]=$t4

    printf "%-6s %-22s %-22s %-22s\n" "$i" "$ts" "$t2" "$t4"
done

# --- Promedios, speedup y efficiency (con awk para aritmetica flotante) ---
resumen=$(
    printf '%s\n' "${T_SEC[@]:1}" "${T_P2[@]:1}" "${T_P4[@]:1}" |
        awk -v n="$REPS" '
        { v[NR] = $1 }
        END {
            for (i = 1; i <= n; i++)     { s += v[i] }
            for (i = n+1; i <= 2*n; i++) { p2 += v[i] }
            for (i = 2*n+1; i <= 3*n; i++) { p4 += v[i] }
            s /= n; p2 /= n; p4 /= n
            printf "%.6f %.6f %.6f %.4f %.4f %.4f %.4f", \
                   s, p2, p4, s/p2, s/p4, (s/p2)/2, (s/p4)/4
        }'
)

read -r AVG_S AVG_P2 AVG_P4 SU2 SU4 EF2 EF4 <<< "$resumen"

echo ""
printf "%-6s %-22s %-22s %-22s\n" "PROM." "$AVG_S" "$AVG_P2" "$AVG_P4"
echo ""
echo "=========================== RESULTADOS ==========================="
printf "Tiempo promedio secuencial : %s s\n" "$AVG_S"
printf "Tiempo promedio 2 hilos    : %s s\n" "$AVG_P2"
printf "Tiempo promedio 4 hilos    : %s s\n" "$AVG_P4"
echo "------------------------------------------------------------------"
printf "Speedup   2 hilos = T_sec / T_2 = %s\n" "$SU2"
printf "Speedup   4 hilos = T_sec / T_4 = %s\n" "$SU4"
printf "Efficiency 2 hilos = S2 / 2     = %s  (%.2f%%)\n" "$EF2" "$(awk -v e="$EF2" 'BEGIN{print e*100}')"
printf "Efficiency 4 hilos = S4 / 4     = %s  (%.2f%%)\n" "$EF4" "$(awk -v e="$EF4" 'BEGIN{print e*100}')"
echo "=================================================================="

# --- CSV para la documentacion ---
{
    echo "num,tiempo_secuencial,tiempo_2_hilos,tiempo_4_hilos,speedup_2,speedup_4,efficiency_2,efficiency_4"
    for ((i = 1; i <= REPS; i++)); do
        awk -v n="$i" -v s="${T_SEC[$i]}" -v a="${T_P2[$i]}" -v b="${T_P4[$i]}" \
            'BEGIN { printf "%d,%s,%s,%s,%.4f,%.4f,%.4f,%.4f\n", n, s, a, b, s/a, s/b, (s/a)/2, (s/b)/4 }'
    done
    awk -v s="$AVG_S" -v a="$AVG_P2" -v b="$AVG_P4" \
        'BEGIN { printf "promedio,%s,%s,%s,%.4f,%.4f,%.4f,%.4f\n", s, a, b, s/a, s/b, (s/a)/2, (s/b)/4 }'
} > "$SALIDA"

echo ""
echo ">>> Resultados detallados guardados en '$SALIDA'"
