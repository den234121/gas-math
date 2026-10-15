import math
import streamlit as st
from config import CONSTANTS

st.header("Расчет критического истечения газа через дюзу")
R = CONSTANTS["universal_gas_constant"]

# 1. Check session state dependencies
required_keys = ["density", "gas_constant", "adiabat", "molar_mass"]
if not all(el in st.session_state for el in required_keys):
    st.error("Заполните состав газа на первой вкладке")
else:
    po = st.session_state["density"]
    Rgas = st.session_state["gas_constant"]
    k = st.session_state["adiabat"]
    M = st.session_state["molar_mass"]

    # 2. Display Gas Mixture Characteristics
    st.subheader("Характеристики газовой смеси")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Плотность смеси, кг/м³", f"{po:.4f}")
    with col2:
        st.metric("Показатель адиабаты", f"{k:.4f}")
    with col3:
        st.metric("Индивидуальная газовая постоянная, Дж/(кг·К)", f"{Rgas:.1f}")

    # 3. Flow Rate Input
    if "flow" in st.session_state:
        flow = st.session_state["flow"]
    else:
        flow = st.number_input(
            "Проведите расчет в закладке Расход через скорость газа в щели\nЛибо вручную введите расход газа в нм³/ч",
            min_value=0.0,
            value=0.0,
            key="crit_manual_flow",
        )

    # 4. Process Pressures and Temperature (Added explicit keys to prevent ID clashes)
    P1 = (
        st.number_input(
            "Введите давление газ до дюзы в МПа(изб.)",
            min_value=0.0,
            value=0.1,
            key="crit_p1",
        )
        * 10**6
        + CONSTANTS["atm_pressure"]
    )
    P2 = (
        st.number_input(
            "Введите давление газ после дюзы в МПа(изб.)",
            min_value=0.0,
            value=0.0,
            key="crit_p2",
        )
        * 10**6
        + CONSTANTS["atm_pressure"]
    )
    T1 = (
        st.number_input(
            "Введите температуру газа до дюзы в °C", value=20.0, key="crit_t1"
        )
        + 273.15
    )

    # 5. Calculations
    b_critical = (2 / (k + 1)) ** (k / (k - 1))
    st.write(f"Критическое отношение давлений: {b_critical:.4f}")

    po1 = P1 / (Rgas * T1)
    Qm = flow * po / 3600

    orifice_type = st.radio(
        "Тип дюзы:", ["плоская диафрагма", "скругленное сопло"], key="crit_orifice_type"
    )
    mu = 0.61 if orifice_type == "плоская диафрагма" else 0.96

    # 6. Flow Regime Logic Block
    if P2 / P1 <= b_critical:
        st.success(
            f"Критическое истечение газа через дюзу. P2/P1 <= b_critical ({P2 / P1:.4f} <= {b_critical:.4f})"
        )
        sp_cr = ((2 * k) / (k + 1) * (P1 / po1)) ** 0.5
        # Area calculation for critical flow
        f = Qm / (
            (mu * P1)
            * ((k / (Rgas * T1)) * (2 / (k + 1)) ** ((k + 1) / (k - 1))) ** 0.5
        )

    else:
        # Fixed stray trailing parenthesis error here
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

    # 7. Convert area to diameter (in mm)
    d = math.sqrt(4 * f / math.pi) * 1000  # Convert to mm

    # 8. Output Results (Using distinct layout variables to keep blocks clean)
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
