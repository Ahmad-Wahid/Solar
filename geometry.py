import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------
# Helper functions
# -----------------------------
def unit(v):
    n = np.linalg.norm(v)
    return v if n == 0 else v / n

def angle_arc(v1, v2, radius=0.5, n=40):
    v1 = unit(v1)
    v2 = unit(v2)

    axis = np.cross(v1, v2)
    if np.linalg.norm(axis) < 1e-9:
        return np.vstack([radius*v1, radius*v2])
    axis = unit(axis)

    theta = np.arccos(np.clip(np.dot(v1, v2), -1, 1))
    t = np.linspace(0, theta, n)

    arc = []
    for ti in t:
        arc.append(
            radius * (
                v1*np.cos(ti)
                + np.cross(axis, v1)*np.sin(ti)
                + axis*np.dot(axis, v1)*(1-np.cos(ti))
            )
        )
    return np.array(arc)

def vector(v, label, color):
    return go.Scatter3d(
        x=[0, v[0]], y=[0, v[1]], z=[0, v[2]],
        mode="lines+text",
        text=["", label],
        name=label,
        line=dict(color=color, width=6)
    )

# =====================================================
# MAIN FIGURE FUNCTION
# =====================================================
def create_figure(h=None, a_s=None, beta=None, a=None):
    """
    3D solar geometry model (visualization only).

    NOTE:
    - Input parameters are intentionally ignored
    - Geometry is fixed and illustrative
    - UI inputs must NOT affect this model
    """

    # -----------------------------
    # Fixed illustrative angles
    # -----------------------------
    h = np.deg2rad(35)          # Sun elevation
    a_s = np.deg2rad(150)       # Sun azimuth (SE → S → SW)
    beta = np.deg2rad(30)       # PV tilt
    a = np.deg2rad(180)         # PV azimuth (south-facing)

    # -----------------------------
    # Reference vectors
    # -----------------------------
    zenith = np.array([0, 0, 1])

    sun = np.array([
        np.cos(h) * np.sin(a_s),
        np.cos(h) * np.cos(a_s),
        np.sin(h)
    ])

    sun_horiz = np.array([sun[0], sun[1], 0])

    # -----------------------------
    # Sun shape
    # -----------------------------
    sun_dir = unit(sun)
    sun_distance = 3.0
    sun_radius = 0.3
    sun_center = sun_distance * sun_dir

    # -----------------------------
    # PV normal (south-facing)
    # -----------------------------
    pv_normal = np.array([
        np.sin(beta) * np.sin(a),
        np.sin(beta) * np.cos(a),
        np.cos(beta)
    ])

    if np.dot(pv_normal, sun) < 0:
        pv_normal = -pv_normal

    # -----------------------------
    # PV surface direction
    # -----------------------------
    pv_surface_dir = unit(sun - np.dot(sun, pv_normal) * pv_normal)
    if pv_surface_dir[2] < 0:
        pv_surface_dir = -pv_surface_dir

    ground_dir = unit(np.array([sun[0], sun[1], 0]))

    # -----------------------------
    # PV module geometry
    # -----------------------------
    width, height = 0.8, 1.6
    u = unit(np.cross(zenith, pv_normal))
    v = unit(np.cross(pv_normal, u))

    bottom_left = np.array([0.0, 0.0, 0.0])

    corners = np.array([
        bottom_left,
        bottom_left + width * u,
        bottom_left + width * u + height * v,
        bottom_left + height * v
    ])

    # -----------------------------
    # Angle arcs
    # -----------------------------
    arc_h = angle_arc(sun_horiz, sun, 0.45)
    arc_psi_z = angle_arc(sun, zenith, 0.55)
    arc_psi = angle_arc(sun, pv_normal, 0.65)

    # -----------------------------
    # Create layout
    # -----------------------------
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.62, 0.38],
        specs=[[{"type": "scene"}, {"type": "domain"}]],
        horizontal_spacing=0.05
    )

    # -----------------------------
    # 3D model (left)
    # -----------------------------
    fig.add_trace(vector(sun, "Sun direction", "orange"), row=1, col=1)
    fig.add_trace(vector(zenith, "Zenith", "blue"), row=1, col=1)
    fig.add_trace(vector(pv_normal, "PV normal (south-facing)", "green"), row=1, col=1)
    fig.add_trace(vector(ground_dir, "Ground reference", "gray"), row=1, col=1)

    fig.add_trace(go.Mesh3d(
        x=corners[:,0], y=corners[:,1], z=corners[:,2],
        color="darkblue", opacity=0.6, name="PV module"
    ), row=1, col=1)

    fig.add_trace(go.Scatter3d(
        x=arc_h[:,0], y=arc_h[:,1], z=arc_h[:,2],
        mode="lines", name="h – Sun elevation",
        line=dict(color="red", width=4)
    ), row=1, col=1)

    fig.add_trace(go.Scatter3d(
        x=arc_psi_z[:,0], y=arc_psi_z[:,1], z=arc_psi_z[:,2],
        mode="lines", name="ψz – Sun zenith",
        line=dict(color="purple", width=4)
    ), row=1, col=1)

    fig.add_trace(go.Scatter3d(
        x=arc_psi[:,0], y=arc_psi[:,1], z=arc_psi[:,2],
        mode="lines", name="ψ – Incidence angle",
        line=dict(color="black", width=4)
    ), row=1, col=1)

    # Sun sphere
    phi, theta = np.mgrid[0:np.pi:25j, 0:2*np.pi:25j]
    sun_x = sun_center[0] + sun_radius * np.sin(phi) * np.cos(theta)
    sun_y = sun_center[1] + sun_radius * np.sin(phi) * np.sin(theta)
    sun_z = sun_center[2] + sun_radius * np.cos(phi)

    fig.add_trace(go.Surface(
        x=sun_x, y=sun_y, z=sun_z,
        colorscale=[[0, "yellow"], [1, "orange"]],
        showscale=False, name="Sun"
    ), row=1, col=1)

    fig.add_trace(go.Scatter3d(
        x=[sun_center[0], 0],
        y=[sun_center[1], 0],
        z=[sun_center[2], 0],
        mode="lines",
        line=dict(color="orange", width=2, dash="dot"),
        name="Sun rays"
    ), row=1, col=1)

    # Ground plane
    xx, yy = np.meshgrid(np.linspace(-1,1,10), np.linspace(-1,1,10))
    zz = np.zeros_like(xx)
    fig.add_trace(go.Surface(
        x=xx, y=yy, z=zz,
        opacity=0.4, showscale=False, name="Ground"
    ), row=1, col=1)


    # -----------------------------
    # Layout styling
    # -----------------------------
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data"
        )
    )

    return fig
