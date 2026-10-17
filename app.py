import streamlit as st

# 1. Define the pages pointing to your separate files
main_page = st.Page("gas_mixture.py", title="Состав газа", icon=":material/database:")

calc_page1 = st.Page(
    "flow_through_speed.py",
    title="Расход через скорость газа в щели",
    icon=":material/calculate:",
)

calc_page2 = st.Page(
    "critical_flow.py",
    title="Критическое истечение газа в дюзе",
    icon=":material/calculate:",
)

calc_page3 = st.Page(
    "throttle.py",
    title="Измерение расхода газа через СУ",
    icon=":material/calculate:",
)

# 2. Create the sidebar navigation
pg = st.navigation([main_page, calc_page1, calc_page2, calc_page3])

# 3. Run the selected page application
pg.run()
