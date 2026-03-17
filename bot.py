import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import MessageHandler, filters

TOKEN = "8649883090:AAHi7sprbMsCgd7YZu4BoP5o1bGh4K8DVtY"

AUTHORIZED_USER_ID = 5014598475  # 👈 pegá tu ID real acá

CATEGORIAS = {
    "comida": ["mcdonalds", "burger", "comida", "restaurant", "mostaza", "pedidos ya"],
    "transporte": ["uber", "didi", "cabify", "taxi", "nafta", "shell", "ypf", "axxion"],
    "suscripciones": ["netflix", "spotify", "adobe", "Disney", "HBO", "amazon", "icloud", "google drive", "mercado pago"],
    "banda": ["grabacion", "ensayo"],
    "actividades chicos": ["voley", "futbol", "guitarra", "viaje de egresados"],
    "Ropa": ["roma mia", "ropa more", "ropa fran"],
    "Sevicios": ["gas", "luz", "agua", "municipal", "tasa de limpieza"],
    "Departamento": ["expensas", "arreglos"],
}


conn = sqlite3.connect("finanzas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    tipo TEXT,
    monto REAL,
    categoria TEXT
)
""")
conn.commit()

def autorizado(update: Update):
    return update.effective_user.id == AUTHORIZED_USER_ID

def detectar_categoria(texto):
    for categoria, palabras in CATEGORIAS.items():
        for palabra in palabras:
            if palabra in texto:
                return categoria
    return "otros"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("No autorizado 🚫")
        return

    await update.message.reply_text("Bot financiero listo 💰")


async def mi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"Tu ID es: {user_id}")


async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("No autorizado 🚫")
        return
    try:
        monto = float(context.args[0])
        categoria = context.args[1]

        cursor.execute(
            "INSERT INTO transacciones (fecha, tipo, monto, categoria) VALUES (datetime('now'), ?, ?, ?)",
            ("gasto", monto, categoria)
        )
        conn.commit()

        await update.message.reply_text(f"Gasto registrado: ${monto} en {categoria}")

    except:
        await update.message.reply_text("Uso: /gasto 3500 comida")

async def ingreso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("No autorizado 🚫")
        return
    try:
        monto = float(context.args[0])
        categoria = context.args[1]

        cursor.execute(
            "INSERT INTO transacciones (fecha, tipo, monto, categoria) VALUES (datetime('now'), ?, ?, ?)",
            ("ingreso", monto, categoria)
        )
        conn.commit()

        await update.message.reply_text(f"Ingreso registrado: ${monto}")

    except:
        await update.message.reply_text("Uso: /ingreso 500000 sueldo")

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        await update.message.reply_text("No autorizado 🚫")
        return
    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='gasto'")
    gastos = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='ingreso'")
    ingresos = cursor.fetchone()[0] or 0

    saldo = ingresos - gastos

    await update.message.reply_text(
        f"📊 Resumen:\nIngresos: ${ingresos}\nGastos: ${gastos}\nSaldo: ${saldo}"
    )
import re

async def procesar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not autorizado(update):
        return

    texto = update.message.text.lower()

    # buscar monto
    match = re.search(r"\d+", texto)
    if not match:
        return

    monto = float(match.group())

    # detectar tipo
    if any(p in texto for p in ["gaste", "pague", "gasto"]):
        tipo = "gasto"
    elif "cobre" in texto or "ingrese" in texto:
        tipo = "ingreso"
    else:
        return

    # categoría simple
    palabras = texto.split()
    categoria = detectar_categoria(texto)


    cursor.execute(
        "INSERT INTO transacciones (fecha, tipo, monto, categoria) VALUES (datetime('now'), ?, ?, ?)",
        (tipo, monto, categoria)
    )
    conn.commit()

    await update.message.reply_text(f"{tipo.capitalize()} registrado: ${monto} en {categoria}")



app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("miid", mi_id))
app.add_handler(CommandHandler("gasto", gasto))
app.add_handler(CommandHandler("ingreso", ingreso))
app.add_handler(CommandHandler("resumen", resumen))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_texto))


app.run_polling()
