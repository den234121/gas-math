import streamlit as st
import pandas as pd
import plotly.express as px

# Загрузка данных
df = pd.read_excel("assets/gas_parameters.xlsx", sheet_name="Sheet1")
st.subheader("Оределите состав смеси газов в %")

# 1. Создание таблицы исходных данных по составу газа
# 1.1. Ограничение представления таблицы в приложении (все свойства газов в колонках [3:] скрыты)
df_4_columns = df.iloc[:, :4]

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
)

# 2.--- MATH INJECTION FOR MIXTURE PARAMETERS ---
# 2.1 Extract the user input composition array
total_mole = edited_df.iloc[:, 3].copy().sum()
if total_mole > 100:
    st.error("Сумма долей смеси превышает 100%")
elif total_mole < 95:
    st.warning("Сумма долей смеси менее 95%, это может привести к неточности расчетов")

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

    # Получаем имена колонок по индексам 4, 5 и 6
    col_density = df.columns[4]
    col_r = df.columns[5]
    col_adiab = df.columns[6]

    # Конвертируем значения колонок в числовой формат (ошибки преобразуем в NaN)
    # и заполняем пустые ячейки нулями
    density_values = (
        pd.to_numeric(
            df[col_density].astype(str).str.replace(",", "."), errors="coerce"
        )
        .fillna(0)
        .values
    )
    r_values = (
        pd.to_numeric(df[col_r].astype(str).str.replace(",", "."), errors="coerce")
        .fillna(0)
        .values
    )
    adiab_values = (
        pd.to_numeric(df[col_adiab].astype(str).str.replace(",", "."), errors="coerce")
        .fillna(0)
        .values
    )

    # Расчет свойств смеси (средневзвешенные значения)
    mix_density = (density_values * w_fracs).sum()
    mix_r = (r_values * w_fracs).sum()
    mix_adiabatic = (adiab_values * w_fracs).sum()

    st.subheader("Характеристики газовой смеси")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Плотность смеси", f"{mix_density:.4f}")
    with col2:
        st.metric("Газовая постоянная (R)", f"{mix_r:.4f}")
    with col3:
        st.metric("Показатель адиабаты", f"{mix_adiabatic:.4f}")
