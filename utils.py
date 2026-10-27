import streamlit as st
from config import CONSTANTS


def get_shared_gas_inputs(page_prefix: str):
    """
    Handles session checking, metric renders, flow inputs, and P/T inputs.
    Returns: po, Rgas, k, M, flow, P1, T1
    """
    # 1. Check session state dependencies
    required_keys = ["density", "gas_constant", "adiabat", "molar_mass"]
    if not all(el in st.session_state for el in required_keys):
        st.error("Заполните состав газа на первой вкладке")
        st.stop()  # Halt execution if gas composition is missing

    po = st.session_state["density"]
    Rgas = st.session_state["gas_constant"]
    k = st.session_state["adiabat"]
    M = st.session_state["molar_mass"]
    mu = st.session_state["viscosity"]

    # 2. Display Gas Mixture Characteristics
    st.subheader("Характеристики газовой смеси")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Плотность смеси, кг/м³", f"{po:.4f}")
    with col2:
        st.metric("Показатель адиабаты", f"{k:.4f}")
    with col3:
        st.metric("Индивидуальная газовая постоянная, Дж/(кг·К)", f"{Rgas:.1f}")

    # omitted

    # 4. Process Pressures and Temperature
    P1 = (
        st.number_input(
            "Введите давление газ до дросселя в МПа(изб.)",
            min_value=0.0,
            value=0.1,
            key=f"{page_prefix}_p1",
        )
        * 10**6
        + CONSTANTS["atm_pressure"]
    )

    T1 = (
        st.number_input(
            "Введите температуру газа до дросселя в °C",
            value=20.0,
            key=f"{page_prefix}_t1",
        )
        + 273.15
    )

    return po, Rgas, k, M, mu, P1, T1
