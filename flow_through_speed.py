import streamlit as st
import math
from config import CONSTANTS

st.header("Предварительный расчет потока газа через щель при заданной скорости")
st.subheader("Задайте геометрию щели")

diameter = st.number_input("Введите диаметр вала в мм")
clearance = st.number_input("Введите радиальный зазор в щели в мм")
area = math.pi * diameter * clearance / (10**6)
st.write(f"Площадь щели: {area * 10**6:.2f} мм²")

calc_flow = st.radio(
    "Определить:",
    ["расход газа", "скорость"],
    captions=["для заданной скорости", "для указанного расхода"],
)

pressure = st.number_input("Введите избыточное давление газа в МПа")
pressure = pressure * 10**6 + CONSTANTS["atm_pressure"]

if calc_flow == "расход газа":
    speed = st.number_input("Введите скорость газа в м/с.")
    flow = area * speed * (pressure / CONSTANTS["atm_pressure"] * 3600)
    st.write(f"Расход газа: {flow:.2f} нм³/ч, {flow * 1000 / 60:.2f} нл/мин")
else:
    flow = st.number_input("Введите нормальный расход газа в нм³/ч.")
    speed = (flow / area / 3600) * (CONSTANTS["atm_pressure"] / pressure)
    st.write(f"Скорость газа: {speed:.2f} м/с")

if speed >= 7:
    st.success("Скорость выше 7 м/с. Обратные перетечки в щели невозможны", icon="✅")
elif speed < 5:
    st.error("Скорость ниже 5 м/с. Высокий риск перетечек", icon="🚨")
else:
    st.warning("Скорость выше 5, но ниже 7 м/с. Есть риск перетечек", icon="⚠️")

st.session_state["flow"] = flow
