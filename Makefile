# ---------------------------------------------------------------------------
# HDT 1 - Computacion Paralela y Distribuida
# Conteo de frecuencia de palabras: version secuencial y paralela.
#
#   make            compila ambas versiones
#   make verificar  comprueba que la salida paralela sea identica a la secuencial
#   make benchmark  ejecuta 5 corridas por configuracion y calcula speedup
#   make clean      elimina ejecutables y archivos generados
# ---------------------------------------------------------------------------

CC      = gcc
CFLAGS  = -O2 -Wall
LDFLAGS = -pthread

ARCHIVO = archivo.txt
REPS    = 5

BINARIOS = conteo_secuencial conteo_paralelo

.PHONY: all verificar benchmark clean ayuda

all: $(BINARIOS)

conteo_secuencial: conteo_frecuencia_secuencial.c
	$(CC) $(CFLAGS) -o $@ $<

conteo_paralelo: conteo_frecuencia_paralelo.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

verificar: $(BINARIOS)
	./verificar.sh $(ARCHIVO)

benchmark: $(BINARIOS)
	./benchmark.sh $(ARCHIVO) $(REPS)

clean:
	rm -f $(BINARIOS)

ayuda:
	@echo "Objetivos disponibles:"
	@echo "  make            compila ambas versiones"
	@echo "  make verificar  comprueba que la salida paralela sea identica"
	@echo "  make benchmark  ejecuta 5 corridas y calcula speedup y efficiency"
	@echo "  make clean      elimina los ejecutables"
	@echo ""
	@echo "Variables: ARCHIVO=$(ARCHIVO)  REPS=$(REPS)"
	@echo "Ejemplo:   make benchmark ARCHIVO=archivo_grande.txt REPS=10"
