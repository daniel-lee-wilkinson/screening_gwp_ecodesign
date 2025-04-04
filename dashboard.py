import streamlit as st
import pandas as pd

DEFAULT_THRESHOLD = 1000.0
EF_FILE = "emissions_factors_ipcc2021.xlsx"

# Densities in kg/m³ for m³ → kg conversion
DENSITY_MAP = {
    "reinforced concrete": 2400,
    "stainless steel": 8000,
    "aluminum": 2700,
    "pvc": 1380,
    "polyethylene": 950,
    "pur": 30,
    "rubber": 1100,
    "copper": 8940
}

st.set_page_config(page_title="GHG Emissions Calculator", layout="wide")
st.title("🌍 GHG Emissions Calculator (with Unit Conversion & What-if Analysis)")

# === Optional: User threshold input ===
user_threshold = st.number_input(
    "🔢 Optional: Enter your own threshold for comparison (kg CO₂-eq)",
    min_value=0.0,
    value=DEFAULT_THRESHOLD,
    step=100.0,
    help="Leave unchanged to use the default threshold of 1000"
)

# === Load EF Data ===
@st.cache_data
def load_emissions_data():
    input_efs = pd.read_excel(EF_FILE, sheet_name='Input_EFs')
    waste_efs = pd.read_excel(EF_FILE, sheet_name='Waste_EFs')
    materials = pd.read_excel(EF_FILE, sheet_name='Materials')

    input_efs = input_efs[['Material', 'Unit', 'GWP IPCC 2021, 20 years per unit']]
    waste_efs = waste_efs[['Material', 'Unit', 'GWP IPCC 2021, 20 years per unit']]
    input_efs = input_efs.rename(columns={'GWP IPCC 2021, 20 years per unit': 'EF'})
    waste_efs = waste_efs.rename(columns={'GWP IPCC 2021, 20 years per unit': 'EF'})

    waste_efs['Material'] = waste_efs['Material'].astype(str) + '_waste'

    input_efs['Material'] = input_efs['Material'].str.strip().str.lower()
    waste_efs['Material'] = waste_efs['Material'].str.strip().str.lower()

    ef_df = pd.concat([input_efs, waste_efs])
    ef_df = ef_df.dropna(subset=['Material', 'EF', 'Unit'])
    ef_df = ef_df.set_index('Material')

    materials['Material'] = materials['Material'].str.strip().str.lower()
    base_materials = materials['Material'].dropna().unique().tolist()
    allowed_materials = sorted(base_materials + [m + '_waste' for m in base_materials])

    return ef_df, allowed_materials

efs, allowed_materials = load_emissions_data()

if efs.empty:
    st.error("❌ Failed to load emission factors.")
    st.stop()

# === User Input Table ===
st.subheader("✍️ Enter Materials and Quantities")

num_rows = st.number_input("Number of rows", min_value=1, max_value=50, value=5, step=1)

default_data = [{"Material": "", "Quantity": 0.0} for _ in range(num_rows)]
df_input = pd.DataFrame(default_data)

edited_df = st.data_editor(
    df_input,
    column_config={
        "Material": st.column_config.SelectboxColumn("Material", options=allowed_materials),
        "Quantity": st.column_config.NumberColumn("Quantity", min_value=0.0, step=0.1)
    },
    use_container_width=True,
    hide_index=True,
    key="editable_table"
)

# === Conversion Helper ===
def convert_quantity_to_kg(row):
    material = row['Material']
    if pd.isna(material):
        return None
    material_clean = material.replace('_waste', '').strip().lower()
    if material not in efs.index:
        return None
    ef_unit = efs.loc[material, 'Unit'].lower()
    quantity = row['Quantity']
    if ef_unit == 'kg':
        return quantity
    elif ef_unit == 'm3':
        density = DENSITY_MAP.get(material_clean)
        if density:
            return quantity * density
        else:
            st.warning(f"⚠️ No density defined for '{material_clean}' — cannot convert m³ to kg.")
            return None
    else:
        st.warning(f"⚠️ Unsupported unit '{ef_unit}' for '{material_clean}'.")
        return None

# === Session State Setup ===
if "calculated" not in st.session_state:
    st.session_state.calculated = False

if st.button("✅ Calculate Emissions"):
    st.session_state.calculated = True

# === Main Calculation Logic ===
if st.session_state.calculated:
    df = edited_df.copy()
    df['Material'] = df['Material'].str.strip().str.lower()
    df = df.dropna(subset=['Material', 'Quantity'])

    df['EF'] = df['Material'].map(efs['EF'])
    df['Unit'] = df['Material'].map(efs['Unit'])
    df['Quantity_kg'] = df.apply(convert_quantity_to_kg, axis=1)
    df['Emission'] = df['Quantity_kg'] * df['EF']

    if df['EF'].isnull().any():
        missing = df[df['EF'].isnull()]
        st.warning("🚫 These materials have no matching emission factor:")
        st.dataframe(missing[['Material']].drop_duplicates())
        st.stop()

    if df['Quantity_kg'].isnull().any():
        st.error("❌ Some quantities could not be converted to kg due to missing density.")
        st.stop()

    # === Display Results ===
    st.subheader("📋 Emission Breakdown")
    st.dataframe(df[['Material', 'Quantity', 'Unit', 'Quantity_kg', 'EF', 'Emission']])
    total_emission = df['Emission'].sum()

    st.subheader("🌡️ Total Emissions")
    st.metric("Total Emissions (kg CO₂-eq)", f"{total_emission:.2f}")
    st.caption(f"📏 Comparing to threshold: {user_threshold} kg CO₂-eq")

    if total_emission < user_threshold:
        st.success(f"✅ BELOW THRESHOLD ({user_threshold})")
    elif total_emission == user_threshold:
        st.info(f"⚠️ AT THRESHOLD ({user_threshold})")
    else:
        st.error(f"❌ ABOVE THRESHOLD ({user_threshold})")

    # === What-if Sliders ===
    st.subheader("🎛️ Adjust Quantities to See Emission Impact")
    adjusted_data = []

    for idx, row in df.iterrows():
        mat = row['Material']
        original_qty = row['Quantity']
        unit = row['Unit']
        ef = row['EF']
        slider_key = f"{mat}_{idx}_slider"

        new_qty = st.slider(
            label=f"{mat} ({unit})",
            min_value=0.0,
            max_value=original_qty * 2,
            value=original_qty,
            step=0.1,
            key=slider_key
        )

        material_clean = mat.replace('_waste', '')
        ef_unit = unit.lower()
        if ef_unit == 'kg':
            new_qty_kg = new_qty
        elif ef_unit == 'm3':
            density = DENSITY_MAP.get(material_clean)
            new_qty_kg = new_qty * density if density else None
        else:
            new_qty_kg = None

        if new_qty_kg is None:
            st.warning(f"⚠️ Could not convert adjusted quantity for {mat}")
            continue

        new_emission = new_qty_kg * ef
        adjusted_data.append({
            'Material': mat,
            'Unit': unit,
            'Adjusted Quantity': new_qty,
            'Adjusted Emission': new_emission
        })

    if adjusted_data:
        adjusted_df = pd.DataFrame(adjusted_data)
        total_adjusted = adjusted_df['Adjusted Emission'].sum()

        st.subheader("📊 Adjusted Emissions Summary")
        st.dataframe(adjusted_df)

        st.metric("🆕 Adjusted Total Emissions", f"{total_adjusted:.2f} kg CO₂-eq")

        diff = total_adjusted - total_emission
        pct_change = (diff / total_emission) * 100 if total_emission > 0 else 0

        if diff < 0:
            st.success(f"⬇️ Emissions reduced by {abs(diff):.2f} kg ({abs(pct_change):.1f}%)")
        elif diff > 0:
            st.error(f"⬆️ Emissions increased by {diff:.2f} kg ({pct_change:.1f}%)")
        else:
            st.info("No change in total emissions.")

# === Optional Reset Button ===
if st.button("🔁 Reset Calculator"):
    st.session_state.calculated = False
    st.experimental_rerun()
