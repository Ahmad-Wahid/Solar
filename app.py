import streamlit as st
import numpy as np
from datetime import date

from solar_math import *
from geometry import create_figure

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("☀️ Solar Geometry & PV Visualization")

# --------------------------------------------------
# Sidebar inputs
# --------------------------------------------------
st.sidebar.header("Inputs")

latitude = st.sidebar.number_input(
    "Latitude (°)",
    value=49.44,
    help="Amberg ≈ 49.44°N"
)

selected_date = st.sidebar.date_input(
    "Date",
    value=date.today()
)

local_time = st.sidebar.slider(
    "Local solar time (hours)",
    0.0, 24.0, 12.0, step=0.25
)

# Fixed PV parameters
beta = 22.3   # degrees
a = 180       # south-facing

# --------------------------------------------------
# Solar calculations (UI only)
# --------------------------------------------------
phi = np.deg2rad(latitude)
n = day_of_year(selected_date)
delta = declination(n)
omega = hour_angle(local_time)
h = sun_elevation(phi, delta, omega)
a_s = sun_azimuth(phi, delta, omega, h)

# --------------------------------------------------
# 1) 3D MODEL (visual only)
# --------------------------------------------------
st.subheader("3D Solar Geometry Model (Visualization Only)")

fig = create_figure(
    h,
    a_s,
    np.deg2rad(beta),
    np.deg2rad(a)
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# 2) THEORY / FORMULAS
# --------------------------------------------------
st.subheader("Solar Geometry – Formulas")

formula_table = {
    "Symbol": [
        "n",
        "δ",
        "ω",
        "h",
        "ψz",
        "aₛ",
        "ψ",
        "β",
        "a"
    ],
    "Formula": [
        "1 … 365",
        "23.45° · sin[360°/365 · (284 + n)]",
        "15° · (LST − 12)",
        "sin⁻¹( sinφ sinδ + cosφ cosδ cosω )",
        "90° − h",
        "atan2( cosδ sinω , sin h sinφ − sinδ )",
        "cos⁻¹( s · n )",
        "22.3° (fixed)",
        "180° (south-facing)"
    ],
    "Meaning": [
        "Day of year",
        "Solar declination",
        "Hour angle",
        "Sun elevation angle",
        "Sun zenith angle",
        "Sun azimuth angle",
        "Angle of incidence on PV",
        "PV tilt angle",
        "PV azimuth angle"
    ]
}

st.table(formula_table)

# --------------------------------------------------
# 3) RESULTS TABLE
# --------------------------------------------------
st.subheader("Computed Solar Angles")

st.table({
    "Quantity": [
        "Day of year (n)",
        "Declination δ (°)",
        "Hour angle ω (°)",
        "Sun elevation h (°)",
        "Sun zenith ψz (°)",
        "Sun azimuth aₛ (°)",
        "PV tilt β (°)",
    ],
    "Value": [
        n,
        f"{np.rad2deg(delta):.2f}",
        f"{np.rad2deg(omega):.2f}",
        f"{np.rad2deg(h):.2f}",
        f"{90 - np.rad2deg(h):.2f}",
        f"{np.rad2deg(a_s):.2f}",
        beta
    ]
})

# --------------------------------------------------
# Info box
# --------------------------------------------------
st.info(
    "ℹ️ **Notes**\n\n"
    "- PV is fixed and south-facing\n"
    "- Sun moves east → south → west (Germany)\n"
    "- 3D model is illustrative and does not change with inputs\n"
    "- Inputs affect calculations only"
)
