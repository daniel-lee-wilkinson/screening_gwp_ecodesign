import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Sample GWP database
gwp_data = { # ecoinvent 3.11
    'Concrete 35MPa (RoW)': {'unit': 'm3', 'gwp': 358},  # GWP per m3
    'Steel (RER)': {'unit': 'kg', 'gwp': 4.62},
    'Truck Transport (EURO 3) (GLO)': {'unit': 'tkm', 'gwp': 0.405},
    'Flattened bamboo (RoW)': {'unit': 'kg', 'gwp': 0.469},
    'Aluminum alloy (GLO)': {'unit': 'kg', 'gwp': 6.35}
}

# Density data for volume to mass conversion (kg/m3)
density_data = {
    'Concrete 35MPa (RoW)': 2400,
    'Flattened bamboo (RoW)': 600,
}

# Store session state for current design
if 'current_design' not in st.session_state:
    st.session_state.current_design = {}

st.title("Design GWP Dashboard")

# --- Select Input ---
st.header("Add Inputs")

item = st.selectbox("Select Material/Transport", list(gwp_data.keys()))
quantity = st.number_input("Enter Quantity", min_value=0.0, step=0.1)

if st.button("Add to Design"):
    if item in st.session_state.current_design:
        st.session_state.current_design[item] += quantity
    else:
        st.session_state.current_design[item] = quantity

# --- Show Current Design ---
st.subheader("Current Design Inputs")
st.write(st.session_state.current_design)

# --- GWP Calculation Function ---
def calculate_gwp(design):
    total_gwp = 0
    for item, qty in design.items():
        gwp_unit = gwp_data[item]['unit']
        gwp_per_unit = gwp_data[item]['gwp']
        if gwp_unit == 'kg' or gwp_unit == 'tkm':
            effective_qty = qty
        elif gwp_unit == 'm3':
            if item in density_data:
                effective_qty = qty * density_data[item]  # Convert m3 to kg
                gwp_per_unit /= density_data[item]  # Adjust GWP to per m3 again
            else:
                effective_qty = qty
        else:
            effective_qty = qty  # default
        total_gwp += effective_qty * gwp_per_unit
    return total_gwp

# --- Current GWP ---
current_gwp = calculate_gwp(st.session_state.current_design)
st.success(f"Current Design GWP: {current_gwp:.2f} kg CO₂e")

# --- Alternative Design ---
st.header("Test Alternative Design")
alternative_design = {}

for item in gwp_data.keys():
    alt_qty = st.number_input(f"Alt Quantity for {item}", min_value=0.0, step=0.1)
    if alt_qty > 0:
        alternative_design[item] = alt_qty

alt_gwp = calculate_gwp(alternative_design)
st.info(f"Alternative Design GWP: {alt_gwp:.2f} kg CO₂e")

# --- Visualization ---
st.subheader("📊 GWP Comparison")

comparison_df = pd.DataFrame({
    'Design': ['Current', 'Alternative'],
    'GWP (kg CO₂e)': [current_gwp, alt_gwp]
})

st.bar_chart(comparison_df.set_index('Design'))


# --- Comparison ---
if alt_gwp < current_gwp:
    st.success("✅ Alternative design is better for GWP!")
elif alt_gwp == current_gwp:
    st.warning("⚖️ Same GWP as current design.")
else:
    st.error("❌ Alternative design has higher GWP.")
