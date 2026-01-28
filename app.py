
import streamlit as st
import numpy as np
from datetime import date

from solar_math import *
from geometry import create_figure

st.set_page_config(layout="wide")
st.title("☀️ Solar Geometry & PV Visualization")

st.sidebar.header("Inputs")

latitude = st.sidebar.number_input(
    "Latitude (°)", value=49.44, help="Amberg ≈ 49.44°N"
)

selected_date = st.sidebar.date_input("Date", value=date.today())

local_time = st.sidebar.slider(
    "Local solar time (hours)", 0.0, 24.0, 12.0, step=0.25
)

beta = 22.3
a = 180

phi = np.deg2rad(latitude)
n = day_of_year(selected_date)
delta = declination(n)
omega = hour_angle(local_time)
h = sun_elevation(phi, delta, omega)
a_s = sun_azimuth(phi, delta, omega, h)

col1, col2 = st.columns([0.65, 0.35])

with col1:
    fig = create_figure(h, a_s, np.deg2rad(beta), np.deg2rad(a))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Computed Solar Angles")
    st.table({
        "Quantity": [
            "Day of year",
            "Declination δ (°)",
            "Hour angle ω (°)",
            "Sun elevation h (°)",
            "Sun zenith ψz (°)",
            "Sun azimuth a_s (°)",
            "PV tilt β (°)",
        ],
        "Value": [
            n,
            np.rad2deg(delta),
            np.rad2deg(omega),
            np.rad2deg(h),
            90 - np.rad2deg(h),
            np.rad2deg(a_s),
            beta
        ]
    })

    st.info(
        "PV is fixed south-facing."
        "Sun moves east → south → west (Germany)."
        "3D model is visualization only."
    )
