import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# conectar DB
conn = sqlite3.connect("finanzas.db")

df = pd.read_sql_query("SELECT * FROM transacciones", conn)

st.title("📊 Dashboard de Finanzas")

if df.empty:
    st.write("No hay datos todavía")
else:
    df["fecha"] = pd.to_datetime(df["fecha"])

    # separar
    gastos = df[df["tipo"] == "gasto"]
    ingresos = df[df["tipo"] == "ingreso"]

    # 💰 resumen
    total_gastos = gastos["monto"].sum()
    total_ingresos = ingresos["monto"].sum()
    saldo = total_ingresos - total_gastos

    st.metric("Ingresos", f"${total_ingresos}")
    st.metric("Gastos", f"${total_gastos}")
    st.metric("Saldo", f"${saldo}")

    # 📊 gastos por categoría
    st.subheader("Gastos por categoría")
    gastos_cat = gastos.groupby("categoria")["monto"].sum()

    fig1, ax1 = plt.subplots()
    gastos_cat.plot(kind="bar", ax=ax1)
    st.pyplot(fig1)

    # 📈 evolución en el tiempo
    st.subheader("Evolución de gastos")
    gastos_fecha = gastos.groupby(gastos["fecha"].dt.date)["monto"].sum()

    fig2, ax2 = plt.subplots()
    gastos_fecha.plot(ax=ax2)
    st.pyplot(fig2)
