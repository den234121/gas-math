import streamlit as st

# 1. Define the pages pointing to your separate files
main_page = st.Page("gas_mixture.py", title="Состав газа", icon=":material/science:")

calc_page1 = st.Page(
    "flow_through_speed.py",
    title="Расход через скорость газа в щели",
    icon=":material/calculate:",
)

calc_page2 = st.Page(
    "restrictive_orifice.py",
    title="Расчет лимитирующей дюзы",
    icon=":material/calculate:",
)

calc_page3 = st.Page(
    "throttle.py",
    title="Измерение расхода газа через СУ",
    icon=":material/calculate:",
)

calc_page4 = st.Page("screw.py", title="Расчет крепежа на прочность", icon="🔩")

# 2. Create the sidebar navigation
pg = st.navigation([main_page, calc_page1, calc_page2, calc_page3, calc_page4])

# 3. Run the selected page application
pg.run()
