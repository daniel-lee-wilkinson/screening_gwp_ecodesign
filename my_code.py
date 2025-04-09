import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Sample GWP data ---
gwp_data = {
    'Concrete 35MPa (m3) (RoW)': {'unit': 'm3', 'gwp': 358},  # GWP per m3
    'Stainless steel (GLO) (kg)': {'unit': 'kg', 'gwp': 4.95},     # GWP per kg
    'Truck Transport > 32 tonnes (RoW) (t-km)': {'unit': 'tkm', 'gwp': 0.112},  # GWP per tonne-km
    'Wood (RoW) (kg)': {'unit': 'm3', 'gwp': 0.469},
    'Aluminum alloy (RoW) (kg)': {'unit': 'kg', 'gwp': 8.22},
    "Copper (GLO) (kg)":{"unit":"kg","gwp":3.72},
    "Cable (kg) (GLO)":{"unit":"kg","gwp":6.08},
    "Network cable (m) (GLO)":{"unit":"m","gwp":0.546}
}
# --- Density data for volume to mass conversion ---
density_data = {
    'Concrete 35MPa (m3) (RoW)': 2400,
    'Wood (RoW) (kg)': 350,
    "Network cable (m) (GLO)": 0.036
}

# --- Initialize session state ---
if 'current_design' not in st.session_state:
    st.session_state.current_design = {}

if 'alternatives' not in st.session_state:
    st.session_state.alternatives = {}

st.title("🌍 Screening Tool for GWP in Eco-Design")

# --- Add to Current Design ---
st.header("➕ Add to Current Design")

item = st.selectbox("Select Material or Transport", list(gwp_data.keys()))
quantity = st.number_input("Enter Quantity", min_value=0.0, step=0.1)

if st.button("Add to Current Design"):
    if item in st.session_state.current_design:
        st.session_state.current_design[item] += quantity
    else:
        st.session_state.current_design[item] = quantity

st.subheader("📦 Current Design Inputs")

# --- Display current design as a table ---
if st.session_state.current_design:
    current_design_df = pd.DataFrame([
        {'Material/Transport': k, 'Quantity': v, 'Unit': gwp_data[k]['unit']}
        for k, v in st.session_state.current_design.items()
    ])
    st.table(current_design_df)
else:
    st.info("No items added yet.")

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
                effective_qty = qty * density_data[item]
                gwp_per_unit /= density_data[item]
            else:
                effective_qty = qty
        else:
            effective_qty = qty
        total_gwp += effective_qty * gwp_per_unit
    return total_gwp

# --- Calculate current GWP ---
current_gwp = calculate_gwp(st.session_state.current_design)
st.success(f"🌱 Current Design GWP: {current_gwp:.2f} kg CO₂e")

# --- Alternative Design Section ---
st.header("🧪 Create Alternative Designs")

alt_name = st.text_input("Alternative Design Name")
alt_input = {}

for item in gwp_data.keys():
    qty = st.number_input(f"{alt_name or 'Alternative'} - Quantity for {item}", min_value=0.0, step=0.1, key=f"{alt_name}_{item}")
    if qty > 0:
        alt_input[item] = qty

if st.button("💾 Save Alternative"):
    if alt_name:
        st.session_state.alternatives[alt_name] = alt_input.copy()
        st.success(f"Saved alternative design: {alt_name}")
    else:
        st.warning("Please enter a name for the alternative design.")

# --- Visualization ---
st.header("📊 GWP Comparison Chart")

design_names = ['Current'] + list(st.session_state.alternatives.keys())
gwp_values = [current_gwp] + [calculate_gwp(alt) for alt in st.session_state.alternatives.values()]
colors = ['tab:blue'] + ['tab:orange'] * len(st.session_state.alternatives)

comparison_df = pd.DataFrame({'Design': design_names, 'GWP (kg CO₂e)': gwp_values})

fig, ax = plt.subplots()
bars = ax.bar(comparison_df['Design'], comparison_df['GWP (kg CO₂e)'], color=colors)
ax.set_ylabel('GWP (kg CO₂e)')
ax.set_title('Global Warming Potential by Design')
ax.set_xticks(range(len(comparison_df)))
ax.set_xticklabels(comparison_df['Design'], rotation=0)

for bar in bars:
    height = bar.get_height()
    ax.annotate(f'{height:.1f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom')

st.pyplot(fig)