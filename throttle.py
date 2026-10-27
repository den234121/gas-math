import math
import streamlit as st
from config import CONSTANTS
from utils import get_shared_gas_inputs  # Import the new function

st.header("Измерение расхода газа через сужающее устройство")
R = CONSTANTS["universal_gas_constant"]

# Get all dependencies, inputs, and environment baselines dynamically
po, Rgas, k, M, mu, P1, T1 = get_shared_gas_inputs(page_prefix="crit")


# 3. Flow Rate Input
if "flow" in st.session_state and st.session_state["flow"] > 0:
    flow = st.session_state["flow"]
else:
    flow = st.number_input(
        'Проведите расчет в закладке "Расход через скорость газа в щели".\nЛибо вручную введите расход газа в нм³/ч',
        min_value=0.0,
        value=0.0,
    )
flow_si = flow / 3600  # Convert flow from nм³/ч to m³/s

Tnom = 293.15

d_pipe = st.number_input(
    "Введите диаметр проходного сечения трубы в мм",
    min_value=0.0,
    value=20.0,
    key="crit_d_pipe",
)
d_pipe_si = d_pipe / 1000  # Convert mm to meters
flow_si = flow / 3600

st.write(f"Расход газа: {flow:.2f} нм³/ч, {flow * 1000 / 60:.2f} нл/мин")
Re = 4 / math.pi * flow_si * po / d_pipe_si / mu

st.write(f"Re = {Re:.2f}")


if Re < 50000:
    throttle_type = "conical"
    st.write("Рекомендуется использовать диафрагму с коническим входом")
    d_max = d_pipe / 2
elif 50000 <= Re <= 1e7:
    throttle_type = "standart"
    st.write("Рекомендуется использовать стандартную диафрагму")
    d_max = int(d_pipe * math.sqrt(0.7))
else:
    st.error("Очень большой расход, необходимо увеличить диаметр трубопровода")

throttle_type_user_choice = st.radio(
    "При необходимости измените тип диафрагмы (не рекомендуется)",
    ["с коническим входом", "стандартная"],
    index=0 if throttle_type == "conical" else 1,
)

d_min = 6 if throttle_type_user_choice == "с коническим входом" else 7
d_min_si = d_min / 1000  # Convert mm to meters

d = st.slider(
    "Установите диаметр дросселя в мм",
    min_value=float(d_min),
    max_value=float(d_max),
    value=float((d_max + d_min) // 2),
    step=0.5,
    format="%.1f",
)

d_si = d / 1000  # Convert mm to meters
st.write(f"Диаметр диафрагмы: {d:.1f}мм")

m = d**2 / d_pipe**2
if throttle_type_user_choice == "с коническим входом":
    alfa = 0.73095 + 0.2726 * m - 0.7138 * m**2 + 5.0623 * m**3

elif throttle_type_user_choice == "стандартная":
    if m <= 0.3:
        alfa_c = 0.595 + 0.04 * m + 0.3 * m**2
    elif m > 0.5:
        alfa_c = 0.3495 + 1.4454 * m - 2.4249 * m**2 + 1.8333 * m**3
    else:
        alfa_c = 0.61 - 0.055 * m + 0.45 * m**2

    if d > 10:
        alfa = (0.99626 + 0.260435 / d - 0.79761 / d**2 + 1.13279 / d**3) * alfa_c
    else:
        alfa = (1.0068 + 0.08287 / d) * alfa_c

st.write(f"Коэффициент диафрагмы равен: {alfa:.2f}")

x = (
    alfa
    * math.sqrt(2)
    * math.pi
    * d_si**2
    / 4
    * math.sqrt(Tnom / (po * CONSTANTS["atm_pressure"] * T1))
)
# Q = x * sqrt(p *delta_p) -> delta_p = Q**2 / (x**2 * p)
delta_p = flow_si**2 / (x**2 * P1)
st.write(f"Перепад на диафрагме {round(delta_p / 1000, 3)} кПа")

st.subheader("Вывод формулы для АЛ:")
temp_sensor = st.checkbox(
    "Есть контроль температуры газа до диафрагмы, показания которого будут учитываться при расчете расхода"
)
p_sensor = st.radio("Измерение давления в:", ["MPa", "kPa"])
dp_sensor = st.radio("Измерение перепада давления на диафрагме в:", ["kPa", "Pa"])
if p_sensor == "MPa" and dp_sensor == "kPa":
    y = 1000**1.5
elif p_sensor == "kPa" and dp_sensor == "Pa":
    y = 1000**0.5
else:
    y = 1000

if temp_sensor:
    x *= math.sqrt(T1)

x *= y * 3600
x = round(x, 3)

p_atm_koef = 0.1013 if p_sensor == "MPa" else 101.3
if temp_sensor:
    st.latex(
        f"Q = {x} \\times \\sqrt{{ \\frac{{({p_atm_koef} + P) \\times \\Delta p}}{{273.15 + T}} }}"
    )
else:
    st.latex(f"Q = {x} \\times \\sqrt{{ ({p_atm_koef} + P) \\times \\Delta p }}")
