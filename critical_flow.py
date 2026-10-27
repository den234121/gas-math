import math
import streamlit as st
from config import CONSTANTS
from utils import get_shared_gas_inputs  # Import the new function

st.header("Расчет критического истечения газа через дюзу")
R = CONSTANTS["universal_gas_constant"]

# Get all dependencies, inputs, and environment baselines dynamically
po, Rgas, k, M, mu, P1, T1 = get_shared_gas_inputs(page_prefix="crit")

P2 = (
    st.number_input(
        "Введите давление газ после дросселя в МПа(изб.)",
        min_value=0.0,
        value=0.0,
        max_value=P1 / 10**6 - CONSTANTS["atm_pressure"] / 10**6,
        # key=f"{page_prefix}_p2",
    )
    * 10**6
    + CONSTANTS["atm_pressure"]
)

# Calculations of critical flow parameters
b_critical = (2 / (k + 1)) ** (k / (k - 1))
st.write(f"Критическое отношение давлений: {b_critical:.4f}")
po1 = P1 / (Rgas * T1)

orifice_type = st.radio(
    "Тип дюзы:", ["плоская диафрагма", "скругленное сопло"], key="crit_orifice_type"
)
mu = 0.61 if orifice_type == "плоская диафрагма" else 0.96

calc_type = st.radio(
    "Определить:",
    ["диаметр дюзы", "расход газа"],
    captions=["для заданного расхода", "для выбранного диаметра дюзы"],
)

if calc_type == "диаметр дюзы":
    # Flow Rate Input
    if "flow" in st.session_state and st.session_state["flow"] > 0:
        flow = st.session_state["flow"]
    else:
        flow = st.number_input(
            'Проведите расчет в закладке "Расход через скорость газа в щели".\nЛибо вручную введите расход газа в нм³/ч',
            min_value=0.0,
            value=0.0,
        )
    flow_si = flow / 3600  # Convert flow from nm³/hr to m³/s
    Qm = flow_si * po

    # Flow Regime Logic Block
    if P2 / P1 <= b_critical:
        st.success(
            f"Критическое истечение газа через дюзу. P2/P1 <= b_critical ({P2 / P1:.4f} <= {b_critical:.4f})"
        )
        sp_cr = ((2 * k) / (k + 1) * (P1 / po1)) ** 0.5
        f = Qm / (
            (mu * P1)
            * ((k / (Rgas * T1)) * (2 / (k + 1)) ** ((k + 1) / (k - 1))) ** 0.5
        )
    else:
        st.warning(
            f"Критическое истечение газа через дюзу невозможно. P2/P1 > b_critical ({P2 / P1:.4f} > {b_critical:.4f})"
        )
        sp_cr = (
            (2 * k) / (k - 1) * (P1 / po1) * (1 - (P2 / P1) ** ((k - 1) / k))
        ) ** 0.5
        multiplier = math.sqrt(
            (2 * k) / (k - 1) * ((P2 / P1) ** (2 / k) - (P2 / P1) ** ((k + 1) / k))
        )
        f = Qm / (mu * P1 * multiplier * (1 / (Rgas * T1)) ** 0.5)

    # Convert area to diameter (in mm)
    d = math.sqrt(4 * f / math.pi) * 1000

if calc_type == "расход газа":
    d = st.number_input(
        "Введите диаметр дюзы в мм",
        min_value=0.0,
        value=2.0,
    )
    f = math.pi * (d / 1000) ** 2 / 4

    # Flow Regime Logic Block
    if P2 / P1 <= b_critical:
        st.success(
            f"Критическое истечение газа через дюзу. P2/P1 <= b_critical ({P2 / P1:.4f} <= {b_critical:.4f})"
        )
        sp_cr = ((2 * k) / (k + 1) * (P1 / po1)) ** 0.5
        Qm = f * (
            (mu * P1)
            * ((k / (Rgas * T1)) * (2 / (k + 1)) ** ((k + 1) / (k - 1))) ** 0.5
        )
    else:
        st.warning(
            f"Критическое истечение газа через дюзу невозможно. P2/P1 > b_critical ({P2 / P1:.4f} > {b_critical:.4f})"
        )
        sp_cr = (
            (2 * k) / (k - 1) * (P1 / po1) * (1 - (P2 / P1) ** ((k - 1) / k))
        ) ** 0.5
        multiplier = math.sqrt(
            (2 * k) / (k - 1) * ((P2 / P1) ** (2 / k) - (P2 / P1) ** ((k + 1) / k))
        )
        Qm = f * (mu * P1 * multiplier * (1 / (Rgas * T1)) ** 0.5)

    flow_si = Qm / po  # Convert mass flow rate to volumetric flow rate
    flow = flow_si * 3600  # Convert flow from m³/s to nm³/hr

# 8. Output Results
st.subheader("Параметры критического истечения")
out_col1, out_col2, out_col3, out_col4, out_col5, out_col6 = st.columns(6)
with out_col1:
    st.metric(
        "Давление до дросселя, МПа(изб)",
        f"{(P1 - CONSTANTS['atm_pressure']) / 10**6:.3f}",
    )
with out_col2:
    st.metric(
        "Давление после дросселя, МПа(изб)",
        f"{(P2 - CONSTANTS['atm_pressure']) / 10**6:.3f}",
    )
with out_col3:
    st.metric("Расход газа нм³/ч", f"{flow:.3f}")
with out_col4:
    st.metric("Температура газа до дюзы, C", f"{(T1 - 273.15):.1f}")
with out_col5:
    st.metric("Скорость критического истечения, м/с", f"{sp_cr:.1f}")
with out_col6:
    st.metric("Диаметр дюзы, мм", f"{d:.2f}")
