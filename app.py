import streamlit as st
import pandas as pd
import joblib

# ── Load trained model ───────────────────────────────────────────────────────
rf_model = joblib.load("rf_model.pkl")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="3D Print Failure Predictor", page_icon="🖨️")
st.title("🖨️ 3D Print Failure Predictor")
st.markdown("**Bambu Lab A1 Mini** — Enter your slicer settings to predict print outcome")
st.divider()

# ── Sidebar inputs ───────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Slicer Settings")

material = st.sidebar.selectbox("Material", ["PLA", "PETG", "TPU"])
orientation = st.sidebar.selectbox("Orientation", ["flat", "angled", "vertical"])
supports = st.sidebar.selectbox("Supports", ["yes", "no"])
model_complexity = st.sidebar.selectbox("Model Complexity", ["simple", "moderate", "complex"])
infill_pct = st.sidebar.slider("Infill %", 10, 100, 20)
layer_height = st.sidebar.selectbox("Layer Height (mm)", [0.08, 0.12, 0.16, 0.20, 0.24, 0.28])
print_speed = st.sidebar.slider("Print Speed (mm/s)", 15, 300, 150)
nozzle_temp = st.sidebar.slider("Nozzle Temp (°C)", 190, 300, 210)
bed_temp = st.sidebar.slider("Bed Temp (°C)", 25, 100, 55)

# ── Recommender function ─────────────────────────────────────────────────────
def recommend(orientation, supports, print_speed, material,
              layer_height, model_complexity):
    recommendations = []

    if orientation in ["vertical", "angled"] and supports == "no":
        recommendations.append("⚠️ Enable supports — vertical/angled prints without supports have 70-79% failure rate")

    if print_speed > 200:
        recommendations.append("⚠️ Reduce print speed below 200mm/s — high speed reduces interlayer bonding")

    if model_complexity == "complex" and supports == "no":
        recommendations.append("⚠️ Enable supports — complex models have high overhang risk")

    if material == "TPU" and print_speed > 50:
        recommendations.append("⚠️ Reduce print speed below 50mm/s — TPU is flexible and jams at high speeds")

    if layer_height <= 0.12 and print_speed > 180:
        recommendations.append("⚠️ Reduce print speed below 180mm/s or increase layer height — thin layers at high speed causes poor bonding")

    if len(recommendations) == 0:
        recommendations.append("✅ Settings look good — safe to print!")

    return recommendations

# ── Predict button ───────────────────────────────────────────────────────────
st.subheader("🔍 Prediction")

if st.button("Predict Print Outcome", use_container_width=True):

    # Build one-hot encoded input
    input_dict = {
        "infill_pct": [infill_pct],
        "layer_height_mm": [layer_height],
        "print_speed_mms": [print_speed],
        "nozzle_temp_c": [nozzle_temp],
        "bed_temp_c": [bed_temp],
        "material_PLA": [1 if material == "PLA" else 0],
        "material_TPU": [1 if material == "TPU" else 0],
        "orientation_flat": [1 if orientation == "flat" else 0],
        "orientation_vertical": [1 if orientation == "vertical" else 0],
        "supports_yes": [1 if supports == "yes" else 0],
        "model_complexity_moderate": [1 if model_complexity == "moderate" else 0],
        "model_complexity_simple": [1 if model_complexity == "simple" else 0]
    }

    input_df = pd.DataFrame(input_dict)

    # Get prediction and probability
    prediction = rf_model.predict(input_df)[0]
    probability = rf_model.predict_proba(input_df)[0][1]

    # Display result
    if prediction == 1:
        st.error(f"❌ FAILURE — {probability:.1%} failure probability")
    else:
        st.success(f"✅ SUCCESS — {probability:.1%} failure probability")

    # Progress bar for failure probability
    st.progress(float(probability))

    st.divider()

    # Display recommendations
    st.subheader("💡 Recommendations")
    recs = recommend(orientation, supports, print_speed,
                     material, layer_height, model_complexity)
    for r in recs:
        st.markdown(r)

    st.divider()

    # Display input summary
    st.subheader("📋 Input Summary")
    summary = {
        "Material": material,
        "Orientation": orientation,
        "Supports": supports,
        "Model Complexity": model_complexity,
        "Infill %": infill_pct,
        "Layer Height (mm)": layer_height,
        "Print Speed (mm/s)": print_speed,
        "Nozzle Temp (°C)": nozzle_temp,
        "Bed Temp (°C)": bed_temp
    }
    st.dataframe(pd.DataFrame(summary, index=["Value"]).T, use_container_width=True)
