"""
===============================================================================
AI DEVELOPMENT DOCUMENTATION (Project 8)
===============================================================================
AI Tools Used: ChatGPT & Gemini

Key Prompts Used:
1. "Generate a Streamlit dashboard that models 1D steady-state heat conduction 
   through a plane wall with thermal resistance and heat flux metrics."
2. "Add an interactive Plotly temperature distribution profile across the wall 
   thickness that updates with material selection and boundary temperatures."
3. "Include robust error handling using st.warning for non-physical inputs 
   (e.g., negative wall thickness, zero area, or identical boundary temperatures)."

Manual Fixes & Verification Required:
- Verified Fourier's 1D conduction formula q = k*A*(T1 - T2)/L against textbook heat transfer solutions.
- Corrected division-by-zero handling when user sets wall thickness to 0.
- Implemented preset thermal conductivity lookup for standard engineering materials (Carbon Steel, Copper, Insulation).
===============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Heat Transfer Analyser", page_icon="📈", layout="wide")

# --- TITLE & USER INSTRUCTIONS ---
st.title("1D Steady-State Heat Transfer Analyser")
st.subheader("Interactive Thermal Conduction & Resistance Assessment Tool")
st.markdown("""
**Instructions:** Use the sidebar controls on the left to specify the wall geometry, material thermal properties, and boundary temperatures. The dashboard dynamically computes heat rate, heat flux, thermal resistance, and plots the temperature gradient across the wall.
""")

# --- SIDEBAR INPUT CONTROLS ---
st.sidebar.header("Thermal & Geometric Inputs")

# Control 1: Material Presets / Custom Selector
material = st.sidebar.selectbox(
    "Select Material Preset:",
    ["Carbon Steel (k = 45 W/m·K)", "Copper (k = 385 W/m·K)", "Stainless Steel (k = 15 W/m·K)", "Fiberglass Insulation (k = 0.04 W/m·K)", "Custom"]
)

# Preset conductivity mappings
k_presets = {
    "Carbon Steel (k = 45 W/m·K)": 45.0,
    "Copper (k = 385 W/m·K)": 385.0,
    "Stainless Steel (k = 15 W/m·K)": 15.0,
    "Fiberglass Insulation (k = 0.04 W/m·K)": 0.04
}

if material == "Custom":
    k = st.sidebar.number_input("Thermal Conductivity, k (W/m·K):", min_value=0.001, max_value=5000.0, value=25.0, step=1.0)
else:
    k = k_presets[material]

# Control 2: Sliders for Geometry
thickness = st.sidebar.slider("Wall Thickness, L (m):", min_value=-0.05, max_value=1.0, value=0.10, step=0.01)
area = st.sidebar.slider("Surface Area, A (m²):", min_value=-1.0, max_value=20.0, value=4.0, step=0.5)

# Control 3: Number Inputs for Boundary Temperatures
st.sidebar.subheader("Boundary Temperatures")
T1 = st.sidebar.number_input("Hot Surface Temperature, T₁ (°C):", value=120.0, step=5.0)
T2 = st.sidebar.number_input("Cold Surface Temperature, T₂ (°C):", value=25.0, step=5.0)

# --- ERROR HANDLING & VALIDATION ---
has_error = False

if thickness <= 0:
    st.error("⚠️ **Invalid Input:** Wall thickness (L) must be strictly greater than 0 meters.")
    has_error = True

if area <= 0:
    st.error("⚠️ **Invalid Input:** Surface area (A) must be strictly greater than 0 m².")
    has_error = True

if T1 == T2:
    st.warning("⚠️ **Thermal Equilibrium:** T₁ is equal to T₂. No temperature gradient exists, so heat transfer rate is zero.")

# --- MAIN ANALYSIS & VISUALIZATION ---
if not has_error:
    delta_T = T1 - T2
    # Fourier's Law calculations
    R_th = thickness / (k * area)          # Thermal resistance (K/W)
    q = delta_T / R_th                     # Heat transfer rate (Watts)
    q_flux = q / area                      # Heat flux (W/m^2)

    # Key Metrics Display
    st.markdown("---")
    st.subheader("Heat Transfer Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Heat Flow Rate (q)", f"{q/1000.0:.3f} kW")
    m2.metric("Heat Flux (q/A)", f"{q_flux:.2f} W/m²")
    m3.metric("Thermal Resistance (R_th)", f"{R_th:.5f} K/W")
    m4.metric("Temperature Drop (ΔT)", f"{delta_T:.1f} °C")

    # Pandas Results Summary Table
    st.markdown("### Results Summary Table")
    results_df = pd.DataFrame({
        "Parameter": [
            "Material", 
            "Thermal Conductivity (k)", 
            "Wall Thickness (L)", 
            "Surface Area (A)", 
            "Hot Face Temp (T1)", 
            "Cold Face Temp (T2)", 
            "Total Heat Flow Rate (q)", 
            "Heat Flux (q/A)", 
            "Thermal Resistance (R_th)"
        ],
        "Value": [
            material.split(" (")[0], 
            f"{k:.3f}", 
            f"{thickness:.3f}", 
            f"{area:.2f}", 
            f"{T1:.2f}", 
            f"{T2:.2f}", 
            f"{q:.2f}", 
            f"{q_flux:.2f}", 
            f"{R_th:.6f}"
        ],
        "Unit": ["Category", "W/m·K", "m", "m²", "°C", "°C", "W", "W/m²", "K/W"]
    })
    st.dataframe(results_df, use_container_width=True)

    # Interactive Plotly Chart: Temperature Gradient Profile
    st.markdown("### Temperature Distribution Across Wall Thickness")
    x_profile = np.linspace(0, thickness, 100)
    T_profile = T1 - (delta_T / thickness) * x_profile

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_profile, 
        y=T_profile, 
        mode='lines', 
        name='Temperature Profile',
        line=dict(color='crimson', width=3)
    ))
    fig.add_trace(go.Scatter(x=[0], y=[T1], mode='markers', marker=dict(size=10, color='red'), name='T₁ (Hot Side)'))
    fig.add_trace(go.Scatter(x=[thickness], y=[T2], mode='markers', marker=dict(size=10, color='blue'), name='T₂ (Cold Side)'))

    fig.update_layout(
        xaxis_title="Position across wall thickness (m)",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
