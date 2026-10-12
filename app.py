import streamlit as st

# 1. Define the pages pointing to your separate files
main_page = st.Page("gas_mixture.py", title="Состав газа", icon=":material/database:")

calc_page = st.Page(
    "flow_through_speed.py",
    title="Расход через скорость газа в щели",
    icon=":material/calculate:",
)

# 2. Create the sidebar navigation
pg = st.navigation([main_page, calc_page])

# 3. Run the selected page application
pg.run()
