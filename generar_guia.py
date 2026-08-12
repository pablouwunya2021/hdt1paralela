#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la guia explicativa en PDF del programa de conteo de frecuencia."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Flowable, Frame, KeepTogether,
                                NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Preformatted, Spacer, Table,
                                TableStyle)

# ---------------------------------------------------------------- paleta ---
AZUL     = colors.HexColor("#1B3A5C")
AZUL_CL  = colors.HexColor("#2E6DA4")
GRIS     = colors.HexColor("#444444")
GRIS_CL  = colors.HexColor("#F2F4F7")
BORDE    = colors.HexColor("#C8D0DA")
VERDE    = colors.HexColor("#1E7A46")
NARANJA  = colors.HexColor("#B45309")
ROJO     = colors.HexColor("#A32020")

SALIDA = "/Users/pablocabrera/paralela/hdt1paralela/GUIA_DEL_PROGRAMA.pdf"

# ---------------------------------------------------------------- estilos ---
ss = getSampleStyleSheet()

H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold",
                    fontSize=17, textColor=AZUL, spaceBefore=20, spaceAfter=10,
                    leading=21)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold",
                    fontSize=12.5, textColor=AZUL_CL, spaceBefore=14,
                    spaceAfter=6, leading=16)
BODY = ParagraphStyle("BODY", parent=ss["BodyText"], fontName="Helvetica",
                      fontSize=10, leading=15, alignment=TA_JUSTIFY,
                      textColor=GRIS, spaceAfter=8)
BULLET = ParagraphStyle("BULLET", parent=BODY, leftIndent=16, bulletIndent=4,
                        spaceAfter=5)
CODE = ParagraphStyle("CODE", parent=ss["Code"], fontName="Courier",
                      fontSize=8.2, leading=11.4, textColor=colors.HexColor("#12263A"),
                      backColor=GRIS_CL, borderColor=BORDE, borderWidth=0.6,
                      borderPadding=7, spaceBefore=5, spaceAfter=10)
NOTA = ParagraphStyle("NOTA", parent=BODY, fontSize=9.3, leading=13.6,
                      leftIndent=10, rightIndent=8, spaceAfter=8)
CAP = ParagraphStyle("CAP", parent=BODY, fontSize=8.6, leading=11,
                     alignment=TA_CENTER, textColor=colors.HexColor("#6B7280"),
                     spaceAfter=12)
TITULO = ParagraphStyle("TITULO", parent=ss["Title"], fontName="Helvetica-Bold",
                        fontSize=25, textColor=AZUL, leading=30, spaceAfter=6)
SUBT = ParagraphStyle("SUBT", parent=BODY, fontSize=12.5, alignment=TA_CENTER,
                      textColor=AZUL_CL, spaceAfter=4, leading=17)
PORT = ParagraphStyle("PORT", parent=BODY, fontSize=10.5, alignment=TA_CENTER,
                      textColor=GRIS, spaceAfter=3)


def P(t, s=BODY):
    return Paragraph(t, s)


def LI(t, s=BULLET):
    return Paragraph(t, s, bulletText="•")


def code(t):
    return Preformatted(t.strip("\n"), CODE)


def caja(texto, color_borde=AZUL_CL, color_fondo=colors.HexColor("#EEF4FA")):
    """Bloque destacado tipo 'callout'."""
    t = Table([[Paragraph(texto, NOTA)]], colWidths=[176 * mm - 26])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
        ("BOX", (0, 0), (-1, -1), 0.8, color_borde),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, color_borde),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def tabla(datos, anchos, alinear_der=None, tam=8.8):
    filas = []
    for i, fila in enumerate(datos):
        estilo = ParagraphStyle("c", parent=BODY, fontSize=tam, leading=tam + 3.4,
                                alignment=TA_CENTER if i == 0 else 0,
                                spaceAfter=0,
                                textColor=colors.white if i == 0 else GRIS,
                                fontName="Helvetica-Bold" if i == 0 else "Helvetica")
        filas.append([Paragraph(str(c), estilo) for c in fila])

    t = Table(filas, colWidths=anchos, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CL]),
    ]
    for col in (alinear_der or []):
        st.append(("ALIGN", (col, 1), (col, -1), "RIGHT"))
    t.setStyle(TableStyle(st))
    return t


# -------------------------------------------------------------- diagrama ---
class Diagrama(Flowable):
    """Diagrama de flujo de la version paralela."""

    def __init__(self, ancho, alto=420):
        Flowable.__init__(self)
        self.width, self.height = ancho, alto

    def _caja(self, x, y, w, h, texto, relleno, borde, tam=8.4, negrita=True):
        c = self.canv
        c.setFillColor(relleno)
        c.setStrokeColor(borde)
        c.setLineWidth(1)
        c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
        c.setFillColor(borde if relleno != borde else colors.white)
        lineas = texto.split("\n")
        c.setFont("Helvetica-Bold" if negrita else "Helvetica", tam)
        ty = y + h / 2 + (len(lineas) - 1) * (tam + 1.6) / 2 - tam / 2 + 1
        for ln in lineas:
            c.drawCentredString(x + w / 2, ty, ln)
            ty -= tam + 1.6

    def _flecha(self, x, y0, y1):
        c = self.canv
        c.setStrokeColor(colors.HexColor("#8A97A8"))
        c.setLineWidth(1.1)
        c.line(x, y0, x, y1)
        c.setFillColor(colors.HexColor("#8A97A8"))
        c.setStrokeColor(colors.HexColor("#8A97A8"))
        p = c.beginPath()
        p.moveTo(x - 3.4, y1 + 5.5)
        p.lineTo(x + 3.4, y1 + 5.5)
        p.lineTo(x, y1)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def _marca_reloj(self, y, texto, color):
        c = self.canv
        c.setStrokeColor(color)
        c.setLineWidth(1.1)
        c.setDash(4, 3)
        c.line(0, y, self.width, y)
        c.setDash()
        c.setFillColor(colors.white)
        tw = c.stringWidth(texto, "Helvetica-Bold", 7.6) + 12
        c.rect(self.width / 2 - tw / 2, y - 5.6, tw, 11.2, stroke=0, fill=1)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawCentredString(self.width / 2, y - 2.7, texto)

    def _etiqueta(self, y, texto, sub, color):
        """Texto con fondo blanco, para que no lo cruce ninguna linea."""
        c = self.canv
        w = max(c.stringWidth(texto, "Helvetica-Bold", 8.2),
                c.stringWidth(sub, "Helvetica-Oblique", 7.4)) + 16
        c.setFillColor(colors.white)
        c.rect(self.width / 2 - w / 2, y - 5, w, 24, stroke=0, fill=1)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawCentredString(self.width / 2, y + 10, texto)
        c.setFillColor(VERDE)
        c.setFont("Helvetica-Oblique", 7.4)
        c.drawCentredString(self.width / 2, y, sub)

    def draw(self):
        c = self.canv
        W = self.width
        cx = W / 2
        gris_b, gris_f = colors.HexColor("#6B7280"), colors.HexColor("#F3F4F6")
        az_b, az_f = AZUL_CL, colors.HexColor("#E8F1FA")
        vd_b, vd_f = VERDE, colors.HexColor("#E7F5ED")
        nj_b, nj_f = NARANJA, colors.HexColor("#FDF3E3")
        linea = colors.HexColor("#8A97A8")

        ancho_c, x_c = 250, cx - 125

        # --- 1. Lectura (fuera del cronometro) ---
        self._caja(x_c, 380, ancho_c, 30,
                   "1.  Leer el archivo completo a memoria", gris_f, gris_b)
        c.setFillColor(gris_b)
        c.setFont("Helvetica-Oblique", 7.4)
        c.drawString(x_c + ancho_c + 8, 392, "fuera de la medicion")
        self._flecha(cx, 380, 360)
        self._marca_reloj(354, "INICIA EL CRONOMETRO", VERDE)

        # --- 2. Division ---
        self._caja(x_c, 310, ancho_c, 32,
                   "2.  Dividir el texto en N bloques\n(cada corte se mueve hasta un separador)",
                   az_f, az_b, tam=7.9)

        # --- 3. Reparto a los hilos: bus horizontal, sin lineas cruzadas ---
        n, wh, gap = 4, 100, 16
        total = n * wh + (n - 1) * gap
        x0 = cx - total / 2
        centros = [x0 + i * (wh + gap) + wh / 2 for i in range(n)]
        y_bus, y_top = 262, 232

        c.setStrokeColor(linea)
        c.setLineWidth(1.1)
        c.line(cx, 310, cx, y_bus)                      # bajada desde la caja 2
        c.line(centros[0], y_bus, centros[-1], y_bus)   # bus de reparto
        for x in centros:
            self._flecha(x, y_bus, y_top)

        self._etiqueta(286, "3.  Cada hilo cuenta SU bloque en SU tabla privada",
                       "sin locks: nada compartido, cero contencion", az_b)

        etiquetas = ["Hilo 0", "Hilo 1", "Hilo 2", "Hilo N-1"]
        for i in range(n):
            self._caja(x0 + i * (wh + gap), 170, wh, 62,
                       "%s\n\nbloque %d\ntabla privada" % (etiquetas[i], i),
                       vd_f, vd_b, tam=7.6)

        # --- 4. Sincronizacion: bus de recoleccion ---
        c.setStrokeColor(linea)
        c.setLineWidth(1.1)
        for x in centros:
            c.line(x, 170, x, 150)
        c.line(centros[0], 150, centros[-1], 150)
        self._flecha(cx, 150, 132)

        self._caja(x_c, 106, ancho_c, 26,
                   "4.  pthread_join:  esperar a TODOS los hilos", nj_f, nj_b, tam=8.2)
        self._flecha(cx, 106, 88)

        # --- 5. Reduccion ---
        self._caja(x_c, 54, ancho_c, 32,
                   "5.  Fusionar las N tablas privadas en una\n(parte secuencial: el techo de Amdahl)",
                   nj_f, nj_b, tam=7.9)
        self._marca_reloj(42, "TERMINA EL CRONOMETRO", ROJO)

        # --- 6. Salida ---
        self._caja(x_c, 4, ancho_c, 26,
                   "6.  Ordenar alfabeticamente e imprimir", gris_f, gris_b)
        c.setFillColor(gris_b)
        c.setFont("Helvetica-Oblique", 7.4)
        c.drawString(x_c + ancho_c + 8, 14, "fuera de la medicion")


# ------------------------------------------------------------ documento ---
def pie(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDE)
    canvas.setLineWidth(0.6)
    canvas.line(60, 48, letter[0] - 60, 48)
    canvas.setFont("Helvetica", 7.8)
    canvas.setFillColor(colors.HexColor("#8A97A8"))
    canvas.drawString(60, 37, "HDT 1 — Conteo de frecuencia de palabras  |  "
                              "Computacion Paralela y Distribuida")
    canvas.drawRightString(letter[0] - 60, 37, "Pagina %d" % doc.page)
    canvas.restoreState()


def portada(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, letter[1] - 20, letter[0], 20, stroke=0, fill=1)
    canvas.setFillColor(AZUL_CL)
    canvas.rect(0, letter[1] - 26, letter[0], 6, stroke=0, fill=1)
    canvas.restoreState()


doc = BaseDocTemplate(SALIDA, pagesize=letter,
                      leftMargin=60, rightMargin=60,
                      topMargin=58, bottomMargin=62,
                      title="Guia del programa - Conteo de frecuencia de palabras",
                      author="Grupo HDT 1 - Computacion Paralela y Distribuida",
                      subject="Explicacion de las versiones secuencial y paralela")

marco = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")
doc.addPageTemplates([
    PageTemplate(id="portada", frames=[marco], onPage=portada),
    PageTemplate(id="normal", frames=[marco], onPage=pie),
])

W = doc.width
S = []

# =========================================================== PORTADA ===
S += [
    Spacer(1, 108),
    P("Conteo de frecuencia de palabras", TITULO),
    P("Guia para entender el programa", SUBT),
    Spacer(1, 26),
]
_l = Table([[""]], colWidths=[W * 0.5])
_l.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 2, AZUL_CL)]))
_l.hAlign = "CENTER"
S += [_l, Spacer(1, 26)]
S += [
    P("Version secuencial y version paralela con POSIX threads", PORT),
    P("Medicion de tiempo, speedup y efficiency", PORT),
    Spacer(1, 44),
    caja("<b>Para que sirve este documento.</b> Explica, de principio a fin, que hace el "
         "programa, como se paralelizo, por que se midio el tiempo donde se midio, y que "
         "significan los numeros que obtuvimos. Al final hay una seccion de preguntas "
         "frecuentes con las respuestas listas, por si las preguntan al exponer."),
    Spacer(1, 30),
    P("Hoja de Trabajo 1  —  Computacion Paralela y Distribuida", PORT),
    P("11 de agosto de 2026", PORT),
    NextPageTemplate("normal"),
    PageBreak(),
]

# ==================================================== 1. EL PROBLEMA ===
S += [
    P("1.  Que hace el programa", H1),
    P("El programa lee un archivo de texto y cuenta <b>cuantas veces aparece cada "
      "palabra</b>. El resultado es una tabla ordenada alfabeticamente con cada palabra "
      "distinta y su frecuencia."),
    code("""$ ./conteo_secuencial archivo.txt

Palabra                        Frecuencia
------------------------------ ----------
algoritmo                      12
computacion                    7
de                             214
paralela                       19
...
Total de palabras diferentes: 904"""),
    P("Antes de contar, cada palabra se <b>normaliza</b>: se pasa a minusculas y se "
      "descarta todo lo que no sea letra o numero. Asi <font face='Courier'>Casa</font>, "
      "<font face='Courier'>casa</font> y <font face='Courier'>casa,</font> cuentan como "
      "la misma palabra."),
    P("Un caracter forma parte de una palabra si cumple:"),
    code("""static int es_caracter_de_palabra(unsigned char caracter)
{
    /* Los bytes >= 128 permiten conservar letras acentuadas en UTF-8. */
    return isalnum(caracter) || caracter >= 128;
}"""),
    P("Cualquier otra cosa —espacio, coma, punto, salto de linea— marca el "
      "<b>final</b> de la palabra actual. Esa es toda la regla de separacion."),

    P("La estructura de datos", H2),
    P("Las frecuencias se guardan en un arreglo dinamico de pares "
      "<i>(palabra, frecuencia)</i> que crece al doble cuando se llena:"),
    code("""typedef struct {
    char   *palabra;        /* copia propia de la palabra   */
    size_t  frecuencia;     /* cuantas veces aparecio       */
} EntradaFrecuencia;

typedef struct {
    EntradaFrecuencia *entradas;
    size_t cantidad;        /* cuantas usadas               */
    size_t capacidad;       /* cuantas caben                */
} TablaFrecuencias;"""),
    caja("<b>Ojo con esto, es importante para entender los resultados.</b> Para insertar "
         "una palabra, <font face='Courier'>agregar_palabra()</font> recorre la tabla "
         "<b>de principio a fin</b> comparando con <font face='Courier'>strcmp</font>. "
         "Con 904 palabras distintas, cada insercion cuesta hasta 904 comparaciones: el "
         "algoritmo es <b>O(n²)</b>. Es lento, pero es justamente lo que hace que "
         "valga la pena paralelizarlo, porque hay bastante computo real que repartir.",
         NARANJA, colors.HexColor("#FDF3E3")),
    PageBreak(),
]

# ================================================== 2. LA SECUENCIAL ===
S += [
    P("2.  La version secuencial", H1),
    P("Un solo flujo de ejecucion recorre el texto de principio a fin, caracter por "
      "caracter, armando cada palabra y metiendola en la tabla:"),
    code("""for (i = inicio; i < fin; i++) {
    unsigned char actual = (unsigned char)texto[i];

    if (es_caracter_de_palabra(actual)) {
        palabra[longitud++] = tolower(actual);   /* sigue la palabra */
    } else if (longitud > 0) {
        palabra[longitud] = '\\0';                /* termino: guardarla */
        agregar_palabra(tabla, palabra, 1);
        longitud = 0;
    }
}
if (longitud > 0) {              /* por si el texto no termina en separador */
    palabra[longitud] = '\\0';
    agregar_palabra(tabla, palabra, 1);
}"""),
    P("Ese ultimo <font face='Courier'>if</font> no es un detalle menor: si el archivo "
      "termina justo con una letra y no con un salto de linea, sin el se perderia la "
      "ultima palabra."),

    P("Que le cambiamos respecto al Corto 02", H2),
    P("La logica de conteo es la misma que ya teniamos. Cambiaron tres cosas, y las tres "
      "existen para poder medir el tiempo de forma honesta:"),
    LI("<b>Se separo la lectura del conteo.</b> Antes se leia con "
       "<font face='Courier'>fgetc()</font> caracter por caracter <i>mientras</i> se "
       "contaba. Ahora el archivo se carga completo a memoria <b>antes</b> de arrancar "
       "el cronometro. Si no hicieramos esto, estariamos midiendo el disco en vez del "
       "procesador."),
    LI("<b>El conteo se aislo en una funcion.</b> "
       "<font face='Courier'>contar_palabras(texto, inicio, fin, tabla)</font> recibe un "
       "rango. La secuencial la llama una vez sobre todo el texto; en la paralela, cada "
       "hilo la llama sobre su pedazo. <b>Es literalmente la misma funcion en las dos "
       "versiones</b>, y por eso la comparacion de tiempos es valida."),
    LI("<b><font face='Courier'>agregar_palabra</font> recibe un parametro "
       "<font face='Courier'>veces</font>.</b> La secuencial siempre pasa 1. Sirve para "
       "la paralela, donde al fusionar hay que sumar de golpe \"esta palabra aparecio 7 "
       "veces en el bloque del hilo 2\"."),
    Spacer(1, 4),
    caja("<b>Regla de oro al comparar versiones:</b> si el cronometro no cubre "
         "exactamente el mismo trabajo en ambas, el speedup no significa nada. Por eso "
         "la lectura del archivo, el ordenamiento y la impresion quedan <b>fuera</b> de "
         "la medicion en las dos.", VERDE, colors.HexColor("#E7F5ED")),
    PageBreak(),
]

# ==================================================== 3. LA PARALELA ===
S += [
    P("3.  La version paralela", H1),
    P("La idea es simple: si el texto se parte en N pedazos, N hilos pueden contar al "
      "mismo tiempo, cada uno en su pedazo. Luego se juntan los resultados. El diagrama "
      "muestra el flujo completo."),
    Spacer(1, 6),
    Diagrama(W),
    P("Flujo de la version paralela. Solo la zona entre las lineas punteadas se mide.", CAP),
    PageBreak(),
]

S += [
    P("Etapa 2: dividir el texto sin partir palabras", H2),
    P("Este es <b>el detalle mas facil de arruinar</b>. Si cortamos el texto en pedazos "
      "iguales sin cuidado, un corte puede caer en medio de una palabra:"),
    code("""...el algoritmo para | lelo cuenta...
                     ^
                     corte a la mitad de "paralelo"

  Hilo 0 contaria "para"  (que no existe)
  Hilo 1 contaria "lelo"  (que tampoco)
  y "paralelo" desapareceria del conteo."""),
    P("La solucion: calcular el corte por division y luego <b>avanzarlo hacia adelante</b> "
      "hasta encontrar un separador."),
    code("""corte = tamano * (i + 1) / num_hilos;

/* Avanzar hasta el siguiente separador para no partir palabras. */
while (corte < tamano && es_caracter_de_palabra((unsigned char)texto[corte])) {
    corte++;
}"""),
    P("Como consecuencia los bloques no quedan exactamente del mismo tamano —uno "
      "puede tener unos bytes de mas—, pero cada palabra queda completa dentro de "
      "un solo bloque. Ese pequeno desbalance es una de las fuentes de overhead."),

    P("Etapa 3: por que cada hilo tiene su PROPIA tabla", H2),
    P("Esta es la decision de diseno mas importante del programa. Cada hilo escribe en "
      "una tabla que solo el toca:"),
    code("""typedef struct {
    const char *texto;
    size_t inicio, fin;      /* su bloque: [inicio, fin) */
    TablaFrecuencias tabla;  /* SU tabla, nadie mas la toca */
    int ok;
} TareaHilo;"""),
    P("La alternativa obvia —una sola tabla compartida protegida con un mutex— "
      "<b>habria sido un desastre</b>. Como practicamente toda la ejecucion consiste en "
      "insertar palabras en la tabla, cada hilo pasaria casi todo su tiempo esperando el "
      "candado. El programa quedaria serializado en la practica y, sumando el costo de "
      "pedir y soltar el mutex millones de veces, muy probablemente correria "
      "<b>mas lento que la version secuencial</b>."),
    caja("<b>Es la leccion central de la HDT.</b> Paralelizar no es \"repartir y ya\": es "
         "repartir <i>de forma que los hilos no se estorben</i>. Al darle a cada hilo "
         "datos privados, la fase paralela no tiene ni un solo lock. Todo el costo de "
         "coordinacion se concentra en un unico punto: la fusion final."),

    P("Etapas 4 y 5: sincronizar y fusionar", H2),
    P("<font face='Courier'>pthread_join</font> bloquea hasta que el hilo termina. Al "
      "hacerlo con los N, el programa no avanza hasta que <b>todos</b> acabaron:"),
    code("""for (i = 0; i < num_hilos; i++) {
    pthread_join(hilos[i], NULL);     /* esperar a que todos terminen */
}

/* Reduccion: volcar las tablas 1..N-1 sobre la del hilo 0. */
for (i = 1; i < num_hilos; i++) {
    for (j = 0; j < tareas[i].tabla.cantidad; j++) {
        agregar_palabra(&tareas[0].tabla,
                        tareas[i].tabla.entradas[j].palabra,
                        tareas[i].tabla.entradas[j].frecuencia);  /* suma de golpe */
    }
}"""),
    caja("<b>Aqui esta el cuello de botella.</b> La fusion la hace <b>un solo hilo</b>, "
         "mientras los demas ya terminaron y estan ociosos. Es la porcion secuencial del "
         "programa, y encima <b>crece con N</b>: con 2 hilos hay 1 tabla que fusionar, "
         "con 4 hay 3. Esto es exactamente lo que la <b>ley de Amdahl</b> describe, y "
         "explica por que el speedup nunca llega a ser 4x con 4 hilos.",
         ROJO, colors.HexColor("#FBECEC")),
]

# ================================================== 4. LA MEDICION ===
S += [
    P("4.  Como se mide el tiempo", H1),
    P("Se usa <font face='Courier'>clock_gettime</font> con "
      "<font face='Courier'>CLOCK_MONOTONIC</font>, que tiene resolucion de nanosegundos "
      "y —a diferencia del reloj de pared— <b>nunca retrocede</b> aunque el "
      "sistema ajuste la hora:"),
    code("""struct timespec inicio, fin;

clock_gettime(CLOCK_MONOTONIC, &inicio);      /* ---- ARRANCA ---- */

    contar_palabras(texto, 0, tamano, &tabla);   /* el trabajo real */

clock_gettime(CLOCK_MONOTONIC, &fin);         /* ---- PARA ---- */

double tiempo = (fin.tv_sec  - inicio.tv_sec)
              + (fin.tv_nsec - inicio.tv_nsec) / 1e9;"""),
    P("Que queda dentro y que queda fuera:"),
    tabla([
        ["", "Version secuencial", "Version paralela"],
        ["<b>FUERA</b> (antes)", "Leer el archivo a memoria", "Leer el archivo a memoria"],
        ["<b>DENTRO</b>", "Recorrer el texto y llenar la tabla",
         "Dividir + crear hilos + contar + join + <b>fusionar</b>"],
        ["<b>FUERA</b> (despues)", "Ordenar e imprimir", "Ordenar e imprimir"],
    ], [W * 0.20, W * 0.36, W * 0.44]),
    Spacer(1, 8),
    caja("Fijate que <b>todo el overhead del paralelismo esta adentro</b> de la medicion: "
         "el reparto, la creacion de hilos, la espera y la fusion. No hicimos trampa "
         "midiendo solo la parte bonita. Si alguien pregunta \"y el costo de crear los "
         "hilos?\", la respuesta es que ya esta contado."),

    P("Por que 5 ejecuciones y no una", H2),
    P("Los tiempos varian bastante entre corridas. Estas son las 5 mediciones "
      "secuenciales reales sobre el archivo de 24 KB:"),
    code("""#1  0.004635 s      <- la mas lenta
#2  0.004826 s
#3  0.003230 s
#4  0.002752 s
#5  0.002447 s      <- la mas rapida (casi 2x mas rapida que la #2)"""),
    P("Casi el doble de diferencia entre la mas lenta y la mas rapida, <b>con el mismo "
      "codigo y el mismo archivo</b>. Las causas: otros procesos compitiendo por el CPU, "
      "el planificador del sistema, la frecuencia del procesador que sube y baja, y el "
      "efecto de calentamiento de cache (las primeras corridas son mas lentas porque los "
      "datos todavia no estan en cache). Por eso se promedian 5 corridas: una sola "
      "medicion no significa nada."),
    PageBreak(),
]

# ======================================== 5. SPEEDUP Y EFFICIENCY ===
S += [
    P("5.  Speedup y efficiency", H1),
    P("<b>Speedup</b> responde: ¿cuantas veces mas rapido corre la version paralela?"),
    code("""            tiempo secuencial
Speedup  =  -----------------          S = 2  ->  el doble de rapido
             tiempo paralelo"""),
    P("<b>Efficiency</b> responde: ¿que tan bien se aprovecho cada hilo? Es el "
      "speedup repartido entre los hilos usados."),
    code("""             Speedup
Efficiency = ---------             E = 1.0 (100 %)  ->  aprovechamiento perfecto
              p hilos              E = 0.5 ( 50 %)  ->  se desperdicio la mitad"""),
    caja("<b>No son lo mismo, y confundirlos es el error tipico.</b> El speedup mide "
         "<i>velocidad</i>; la efficiency mide <i>aprovechamiento</i>. Una configuracion "
         "puede ser la mas rapida y a la vez la que peor usa los recursos — y eso "
         "es exactamente lo que nos paso."),

    P("Un ejemplo con nuestros numeros", H2),
    code("""Secuencial : 0.003578 s          Paralela 4 hilos : 0.001745 s

  Speedup    = 0.003578 / 0.001745 = 2.05   -> 2.05 veces mas rapido
  Efficiency = 2.05 / 4            = 0.51   -> solo 51 % de aprovechamiento

Interpretacion: usamos 4 hilos pero solo obtuvimos el rendimiento
de 2.05. Casi la mitad de la capacidad se fue en coordinacion."""),

    P("Resultados obtenidos", H2),
    P("Equipo de prueba: Apple M5, 10 nucleos (4 de rendimiento + 6 de eficiencia). "
      "Promedio de 5 corridas."),
    tabla([
        ["Archivo", "Configuracion", "Tiempo prom.", "Speedup", "Efficiency"],
        ["<b>archivo.txt</b><br/>24 KB", "Secuencial", "0.003578 s", "1.00", "100 %"],
        ["", "2 hilos", "0.002188 s", "1.64", "<b>81.8 %</b>"],
        ["", "4 hilos", "0.001745 s", "<b>2.05</b>", "51.3 %"],
        ["<b>archivo_grande.txt</b><br/>958 KB", "Secuencial", "0.071592 s", "1.00", "100 %"],
        ["", "2 hilos", "0.042284 s", "1.69", "<b>84.7 %</b>"],
        ["", "4 hilos", "0.024765 s", "<b>2.89</b>", "72.3 %"],
    ], [W * 0.24, W * 0.21, W * 0.19, W * 0.16, W * 0.20], alinear_der=[2, 3, 4]),
    PageBreak(),
]

# ======================================== 6. QUE SIGNIFICAN ===
S += [
    P("6.  Que significan los resultados", H1),

    P("Hallazgo 1: mas rapido no es mas eficiente", H2),
    P("Con 4 hilos obtuvimos <b>el mayor speedup</b> (2.05x), pero con 2 hilos obtuvimos "
      "<b>la mayor eficiencia</b> (81.8 % contra 51.3 %). Son configuraciones ganadoras "
      "distintas segun lo que se quiera optimizar: si importa terminar rapido, 4 hilos; "
      "si importa no desperdiciar recursos, 2 hilos."),

    P("Hallazgo 2: el speedup crece cada vez menos", H2),
    P("Al pasar de 2 a 4 hilos duplicamos los recursos, pero el tiempo solo bajo de "
      "0.002188 s a 0.001745 s: un <b>20 % de mejora a cambio del doble de hilos</b>. El "
      "segundo par de hilos aporto una fraccion minima de lo que aporto el primero."),
    tabla([
        ["Hilos", "Speedup ideal", "Obtenido (24 KB)", "Obtenido (958 KB)"],
        ["2", "2.00", "1.64  (82 % del ideal)", "1.69  (85 % del ideal)"],
        ["4", "4.00", "2.05  (51 % del ideal)", "2.89  (72 % del ideal)"],
    ], [W * 0.14, W * 0.20, W * 0.33, W * 0.33]),
    Spacer(1, 10),
    P("La brecha contra el ideal <b>se ensancha</b> conforme se agregan hilos. Eso es la "
      "ley de Amdahl en accion: la fusion de tablas es secuencial y le pone un techo al "
      "speedup, sin importar cuantos hilos se agreguen."),

    P("Hallazgo 3: el tamano del problema lo cambia todo", H2),
    P("Este es el resultado mas interesante del trabajo. <b>El mismo codigo, sin cambiar "
      "una sola linea</b>, con 4 hilos:"),
    code("""archivo.txt        (24 KB)  ->  efficiency 51.3 %
archivo_grande.txt (958 KB) ->  efficiency 72.3 %"""),
    P("La diferencia no esta en el paralelismo sino en <b>cuanto trabajo util habia para "
      "repartir</b>. El costo de crear hilos y fusionar tablas es practicamente fijo: si "
      "el trabajo real es pequeno, ese costo se lo come todo; si es grande, se diluye. "
      "Un archivo de 24 KB simplemente <b>no es lo bastante grande</b> para justificar 4 "
      "hilos."),

    P("Hallazgo 4: mas hilos no siempre es mejor", H2),
    P("No es solo que el promedio empeore. En corridas individuales sobre el archivo "
      "pequeno, <b>4 hilos fue mas lento que 2</b>:"),
    code("""Corrida #5:   2 hilos = 0.001376 s     4 hilos = 0.001426 s   <- mas lento
Corrida #4:   2 hilos = 0.001510 s     4 hilos = 0.001490 s   <- empate"""),
    P("Agregar hilos ahi no aporto absolutamente nada. Nuestro procesador tiene 10 "
      "nucleos, pero con este archivo ya a los 4 hilos la eficiencia estaba por debajo "
      "del 52 %: usar 10 hilos sobre 24 KB de texto seria <b>contraproducente</b>, "
      "porque crear y fusionar 10 tablas costaria mas que el conteo mismo."),
    PageBreak(),
]

# ============================================ 7. OVERHEAD ===
S += [
    P("7.  De donde sale el overhead", H1),
    P("Todo lo que la version paralela hace y la secuencial no. Ordenado por impacto:"),
    tabla([
        ["Fuente", "Por que cuesta"],
        ["<b>Fusion de las tablas</b><br/>(la principal)",
         "Es 100 % secuencial y crece con N. Con 4 hilos hay 3 tablas de hasta 904 "
         "palabras que fusionar, y cada insercion hace busqueda lineal. Es el techo "
         "de Amdahl."],
        ["<b>Crear y destruir hilos</b>",
         "Cada <font face='Courier'>pthread_create</font> cuesta decenas de "
         "microsegundos. Sobre un trabajo total de 3.5 ms, 4 hilos son un costo fijo "
         "nada despreciable."],
        ["<b>La espera del join</b>",
         "El tiempo lo marca el hilo <b>mas lento</b>, no el promedio. Los demas "
         "quedan ociosos esperando."],
        ["<b>Desbalance de carga</b>",
         "Los bloques se reparten por bytes, no por palabras. Un bloque con palabras "
         "largas tiene menos palabras que contar que uno con palabras cortas."],
        ["<b>Nucleos heterogeneos</b>",
         "El M5 tiene nucleos rapidos (P) y lentos (E). Si un hilo cae en un nucleo E, "
         "tarda mas y <b>todos</b> lo esperan en el join."],
        ["<b>Memoria duplicada</b>",
         "Con 4 hilos existen 4 tablas simultaneas: 4x la memoria y 4x las llamadas a "
         "<font face='Courier'>malloc</font>."],
        ["<b>Contencion en malloc</b>",
         "El asignador del sistema usa locks internos. Varios hilos pidiendo memoria "
         "a la vez se serializan parcialmente sin que el codigo lo note."],
    ], [W * 0.27, W * 0.73], tam=8.5),
    PageBreak(),
]

# ============================================ 8. USO ===
S += [
    P("8.  Como correrlo", H1),
    code("""make                # compila las dos versiones
make verificar      # comprueba que la paralela da lo mismo que la secuencial
make benchmark      # 5 corridas por configuracion + speedup y efficiency
make clean          # borra los ejecutables

# Con otro archivo o mas repeticiones:
make benchmark ARCHIVO=archivo_grande.txt REPS=10"""),
    P("Y a mano, si hace falta:"),
    code("""gcc -O2 -Wall          -o conteo_secuencial conteo_frecuencia_secuencial.c
gcc -O2 -Wall -pthread -o conteo_paralelo   conteo_frecuencia_paralelo.c

./conteo_secuencial archivo.txt              # tabla completa + tiempo
./conteo_paralelo   archivo.txt 4            # con 4 hilos
./conteo_paralelo   archivo.txt 4 --silencioso   # solo el tiempo"""),
    caja("La version paralela necesita <b><font face='Courier'>-pthread</font></b> y la "
         "secuencial no. Si se te olvida, el error es un "
         "<font face='Courier'>undefined symbol: _pthread_create</font> al enlazar. Por "
         "eso existe el Makefile."),

    P("Verificar que ambas versiones dan lo mismo", H2),
    P("Un speedup solo vale si las dos versiones calculan lo mismo. "
      "<font face='Courier'>verificar.sh</font> lo comprueba automaticamente y devuelve "
      "codigo de salida 0 o 1:"),
    LI("Compara la salida completa contra la secuencial con <b>1, 2, 3, 4, 5, 7, 8, 16 y "
       "32 hilos</b>. Se incluyen impares y numeros que no dividen el tamano, para forzar "
       "cortes en posiciones raras. Identica en las nueve."),
    LI("Prueba <b>7 casos borde</b> —archivo vacio, una sola palabra, solo espacios, "
       "dos palabras de 3 bytes, palabras repetidas, mayusculas y minusculas, y texto sin "
       "salto de linea final— cada uno con 1, 2, 4 y 8 hilos. Los de 3 y 4 bytes son "
       "los mas exigentes: con 8 hilos varios reciben bloques vacios."),
    PageBreak(),
]

# ============================================ 9. FAQ ===
faq = [
    ("¿Por que usaron pthreads y no OpenMP?",
     "Porque el enunciado no exige ninguna libreria en particular: pide \"al menos dos "
     "procesos o hilos\" y permite \"C, C++ u otro lenguaje\". pthreads es parte del "
     "estandar POSIX y compila sin instalar nada, mientras que OpenMP en macOS requiere "
     "instalar libomp aparte. El analisis seria identico: OpenMP con tablas privadas por "
     "hilo hace exactamente lo mismo por debajo."),
    ("¿Por que el speedup con 4 hilos no fue 4x?",
     "Por la ley de Amdahl. La fusion de las tablas es secuencial —la hace un solo "
     "hilo mientras los demas esperan— y ademas crece con el numero de hilos. A eso "
     "se suma el costo de crear los hilos y el desbalance de carga. Ninguna parte "
     "secuencial se acelera por agregar hilos, y esa parte le pone un techo al speedup."),
    ("Si tienen 10 nucleos, ¿por que no usaron 10 hilos?",
     "Porque no habria ayudado, y con el archivo pequeno habria empeorado. Ya con 4 hilos "
     "la eficiencia cayo al 51 %. Con 10 hilos habria que crear y fusionar 10 tablas "
     "sobre solo 24 KB de texto: el costo de coordinacion superaria el ahorro del "
     "conteo. El numero optimo de hilos depende de cuanto trabajo hay, no de cuantos "
     "nucleos tiene la maquina."),
    ("¿Por que cada hilo tiene su propia tabla en vez de compartir una?",
     "Porque compartirla exigiria un mutex, y como casi todo el programa consiste en "
     "insertar en la tabla, los hilos pasarian el tiempo esperando el candado. Quedaria "
     "serializado y probablemente mas lento que la secuencial. Con tablas privadas la "
     "fase paralela no tiene ni un lock; el costo se paga una sola vez, al fusionar."),
    ("¿Como evitan partir una palabra entre dos hilos?",
     "Cada corte se calcula por division y luego se <b>avanza hacia adelante</b> hasta "
     "encontrar un separador. Los bloques quedan de tamanos ligeramente distintos, pero "
     "cada palabra queda completa dentro de un solo bloque."),
    ("¿Como saben que la paralela da el resultado correcto?",
     "Lo verificamos automaticamente con <font face='Courier'>verificar.sh</font>: la "
     "salida completa —904 palabras con sus frecuencias— es identica a la "
     "secuencial con 1, 2, 3, 4, 5, 7, 8, 16 y 32 hilos, mas 7 casos borde probados con "
     "1, 2, 4 y 8 hilos cada uno."),
    ("¿Por que promediaron 5 corridas en vez de tomar una sola?",
     "Porque los tiempos varian mucho por causas externas al programa: otros procesos, el "
     "planificador, la frecuencia del CPU y el calentamiento de cache. En nuestras "
     "mediciones la corrida secuencial mas lenta fue casi el doble que la mas rapida, con "
     "el mismo codigo y el mismo archivo. Una sola medicion no seria confiable."),
    ("¿Por que la eficiencia baja al agregar hilos?",
     "Porque el overhead crece con el numero de hilos (mas hilos que crear, mas tablas "
     "que fusionar) mientras el trabajo util por hilo se reduce. La relacion trabajo "
     "util / overhead empeora en cada paso."),
    ("¿Por que midieron tambien con un archivo grande?",
     "Para aislar el efecto del tamano del problema. Con 24 KB los tiempos son de "
     "milisegundos y el overhead pesa muchisimo. Al repetir el mismo texto 40 veces y "
     "medir de nuevo, la eficiencia con 4 hilos subio de 51 % a 72 % <b>sin cambiar el "
     "codigo</b>. Es la evidencia mas clara de que el beneficio del paralelismo depende "
     "de que haya trabajo suficiente."),
    ("¿La medicion incluye el tiempo de leer el archivo?",
     "No, a proposito. Leer del disco no es trabajo de computo y depende del cache del "
     "sistema operativo; incluirlo distorsionaria la comparacion. El archivo se carga "
     "completo a memoria <b>antes</b> de arrancar el cronometro en <b>las dos</b> "
     "versiones. Lo que si esta incluido es todo el overhead del paralelismo."),
]

S += [P("9.  Preguntas frecuentes", H1),
      P("Con las respuestas listas, por si las preguntan al exponer."), Spacer(1, 4)]

PREG = ParagraphStyle("PREG", parent=BODY, fontName="Helvetica-Bold", fontSize=10,
                      textColor=AZUL, spaceAfter=4, leading=13.5)
RESP = ParagraphStyle("RESP", parent=BODY, fontSize=9.4, leading=13.6,
                      leftIndent=12, spaceAfter=0)

for preg, resp in faq:
    t = Table([[Paragraph(preg, PREG)], [Paragraph(resp, RESP)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, AZUL_CL),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (0, 0), 3),
        ("BOTTOMPADDING", (0, -1), (0, -1), 10),
    ]))
    S.append(KeepTogether(t))

# ============================================ CIERRE ===
S += [
    Spacer(1, 16),
    caja("<b>En una frase.</b> Repartir el texto entre varios hilos si acelera el conteo, "
         "pero cada hilo agregado rinde menos que el anterior, porque la fusion final es "
         "secuencial y el costo de coordinacion crece. Cuanto mas grande el archivo, mas "
         "vale la pena — con 24 KB, 4 hilos aprovechan la mitad de su capacidad; con "
         "958 KB, casi tres cuartas partes.", VERDE, colors.HexColor("#E7F5ED")),
]

doc.build(S)
print("PDF generado:", SALIDA)
