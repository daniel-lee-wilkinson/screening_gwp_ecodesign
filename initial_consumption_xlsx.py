import streamlit as st
import pandas as pd

THRESHOLD = 1000
EF_FILE = "emissions_factors_ipcc2021.xlsx"

st.title("📊 GHG Emissions Calculator (Controlled Material Input)")

# === Load Emission Factors and Material List ===
@st.cache_data
def load_efs_and_materials():
    try:
        input_efs = pd.read_excel(EF_FILE, sheet_name='Input_EFs')
        waste_efs = pd.read_excel(EF_FILE, sheet_name='Waste_EFs')
        materials = pd.read_excel(EF_FILE, sheet_name='Materials')

        input_efs = input_efs[['Material', 'GWP IPCC 2021, 20 years per kg']].rename(
            columns={'GWP IPCC 2021, 20 years per kg': 'EF'})
        waste_efs = waste_efs[['Material', 'GWP IPCC 2021, 20 years per kg']].rename(
            columns={'GWP IPCC 2021, 20 years per kg': 'EF'})
        waste_efs['Material'] = waste_efs['Material'].astype(str) + '_waste'

        # Clean and normalize
        input_efs['Material'] = input_efs['Material'].str.strip().str.lower()
        waste_efs['Material'] = waste_efs['Material'].str.strip().str.lower()

        ef_table = pd.concat([input_efs, waste_efs])
        ef_table = ef_table.groupby('Material', as_index=True).mean(numeric_only=True)

        materials['Material'] = materials['Material'].str.strip().str.lower()
        base_materials = materials['Material'].dropna().unique().tolist()

        all_options = sorted(base_materials + [m + '_waste' for m in base_materials])

        return ef_table, all_options
    except Exception as e:
        st.error(f"Failed to load emission factor data: {e}")
        return pd.DataFrame(), []

efs, allowed_materials = load_efs_and_materials()

if efs.empty:
    st.stop()

# === Editable Table-Style Input ===
st.subheader("✍️ Enter Materials and Quantities")

num_rows = st.number_input("Number of rows", min_value=1, max_value=50, value=5, step=1)

# Initialize empty input table
default_data = [{"Material": "", "Quantity": 0.0} for _ in range(num_rows)]
df_input = pd.DataFrame(default_data)

# Editable UI table with dropdowns and number inputs
edited_df = st.data_editor(
    df_input,
    column_config={
        "Material": st.column_config.SelectboxColumn("Material", options=allowed_materials),
        "Quantity": st.column_config.NumberColumn("Quantity (kg)", min_value=0.0, step=0.1)
    },
    use_container_width=True,
    hide_index=True,
    key="editable_table"
)

# === Calculate Emissions ===
if st.button("✅ Calculate Emissions"):
    df = edited_df.copy()
    df['Material'] = df['Material'].str.strip().str.lower()
    df = df.dropna(subset=['Material', 'Quantity'])

    df['EF'] = df['Material'].map(efs['EF'])

    missing = df[df['EF'].isnull()]
    if not missing.empty:
        st.warning("⚠️ These materials were not matched with an emission factor:")
        st.dataframe(missing[['Material']].drop_duplicates())
        st.stop()

    df['Emission'] = df['Quantity'] * df['EF']

    st.subheader("📋 Emission Breakdown")
    st.dataframe(df)

    total_emission = df['Emission'].sum()

    st.subheader("🌡️ Total Emissions")
    st.metric("Total Emissions (kg CO₂-eq)", f"{total_emission:.2f}")

    if total_emission < THRESHOLD:
        st.success(f"✅ BELOW THRESHOLD ({THRESHOLD})")
    elif total_emission == THRESHOLD:
        st.info(f"⚠️ AT THRESHOLD ({THRESHOLD})")
    else:
        st.error(f"❌ ABOVE THRESHOLD ({THRESHOLD})")
