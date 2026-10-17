import streamlit as st
import pandas as pd
import plotly.express as px


# 0.1. Use the caching decorator to read the Excel file efficiently
@st.cache_data
def load_base_data():
    return pd.read_excel("assets/gas_parameters.xlsx", sheet_name="Sheet1")


# Load the file (this only runs once; future runs are pulled from cache)
df_raw = load_base_data()

st.header("Определите состав смеси газов в %")

# 0.2. Persist the user's specific EDITS across pages using session state
if "df_4_columns" not in st.session_state:
    st.session_state["df_4_columns"] = df_raw.iloc[:, :4]

st.header("Оределите состав смеси газов в %")

# 1. Создание таблицы исходных данных по составу газа
# 1.1. Ограничение представления таблицы в приложении (все свойства газов в колонках [3:] скрыты)
df_4_columns = st.session_state["df_4_columns"]
fourth_col = df_4_columns.columns[3]

# 1.2. Build the configuration to disable all columns except the 4th one
config = {}
for col in df_4_columns.columns:
    if col == fourth_col:
        # Enforces fractional number input with step and formatting constraints
        config[col] = st.column_config.NumberColumn(
            disabled=False,
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            format="%.2f",
        )
    else:
        # Locks the column from editing
        config[col] = st.column_config.Column(disabled=True)

# 1.3. Pass the configuration dictionary to st.data_editor
edited_df = st.data_editor(
    df_4_columns,
    column_config=config,
    use_container_width=True,
    hide_index=True,  # Optional: hides the index column for a cleaner look
    key="gas_composition_editor",
)

# 1.4. Save any live modifications right back to session state
st.session_state["df_4_columns"] = edited_df

# 2.--- MATH INJECTION FOR MIXTURE PARAMETERS ---
# 2.1 Extract the user input composition array
total_mole = edited_df.iloc[:, 3].copy().sum()
if total_mole > 100:
    st.error("Сумма долей смеси превышает 100%", icon="🚨")
elif total_mole < 95:
    st.warning(
        "Сумма долей смеси менее 95%, это может привести к неточности расчетов",
        icon="⚠️",
    )

# --Showing a circular diagram
# 2.2 Filter out components with zero or negative values for the chart
chart_data = edited_df[edited_df[fourth_col] > 0]

if not chart_data.empty:
    # Create an interactive donut/pie chart
    fig = px.pie(
        chart_data,
        values=fourth_col,
        names=df_4_columns.columns[1],
        title="Состав газовой смеси",
        hole=0.4,  # Creates a clean circular donut chart look
    )

    # Render the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Введите значения больше нуля в таблицу, чтобы увидеть диаграмму состава.")


# 3.--- CALCULATION OF MIXTURE PARAMETERS ---
# Нормализуем доли к долям единицы (предполагаем, что введены проценты от 0 до 100)
fractions = edited_df.iloc[:, 3].values / 100.0
sum_fractions = fractions.sum()

if sum_fractions > 0:
    # Нормализуем доли на случай, если сумма не равна ровно 100%
    w_fracs = fractions / sum_fractions

    # Получаем имена колонок по индексам 4, 5, 6, 7, 8
    col_density = df_raw.columns[4]
    col_r = df_raw.columns[5]
    col_adiab = df_raw.columns[6]
    col_molar_mass = df_raw.columns[7]
    col_viscosity = df_raw.columns[8]

    # Конвертируем значения колонок в числовой формат (ошибки преобразуем в NaN)
    # и заполняем пустые ячейки нулями
    density_values = (
        pd.to_numeric(
            df_raw[col_density].astype(str).str.replace(",", "."), errors="coerce"
        )
        .fillna(0)
        .values
    )
    r_values = (
        pd.to_numeric(df_raw[col_r].astype(str).str.replace(",", "."), errors="coerce")
        .fillna(0)
        .values
    )
    adiab_values = (
        pd.to_numeric(
            df_raw[col_adiab].astype(str).str.replace(",", "."), errors="coerce"
        )
        .fillna(0)
        .values
    )

    molar_mass = (
        pd.to_numeric(
            df_raw[col_molar_mass].astype(str).str.replace(",", "."), errors="coerce"
        )
        .fillna(0)
        .values
    )

    viscosity_values = (
        pd.to_numeric(
            df_raw[col_viscosity].astype(str).str.replace(",", "."), errors="coerce"
        )
        .fillna(0)
        .values
    )

    # Расчет свойств смеси (средневзвешенные значения)
    mix_density = (density_values * w_fracs).sum()
    mix_r = (r_values * w_fracs).sum()
    mix_adiabatic = (adiab_values * w_fracs).sum()
    mix_molar_mass = (molar_mass * w_fracs).sum()
    mix_viscosity = (viscosity_values * w_fracs).sum() / 100000  # Convert to Pa·s

    st.session_state["density"] = mix_density
    st.session_state["gas_constant"] = mix_r
    st.session_state["adiabat"] = mix_adiabatic
    st.session_state["molar_mass"] = mix_molar_mass
    st.session_state["viscosity"] = mix_viscosity

    st.subheader("Характеристики газовой смеси")

    st.metric("Плотность смеси, кг/м³", f"{mix_density:.4f}")
    st.metric("Газовая постоянная, Дж/(кг·К)", f"{mix_r:.4f}")
    st.metric("Показатель адиабаты", f"{mix_adiabatic:.4f}")
    st.metric("Молярная масса, кг/моль", f"{mix_molar_mass:.5f}")
    st.metric("Вязкость смеси, 10⁻⁵ Па·с", f"{mix_viscosity * 100000:.2f}")
