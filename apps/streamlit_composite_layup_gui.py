"""
Phase 12A: Interactive Composite Layup Visualization GUI

Run from project root:
    streamlit run apps/streamlit_composite_layup_gui.py
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# -----------------------------
# Utility functions
# -----------------------------

def read_csv_safe(relative_path: str):
    path = PROJECT_ROOT / relative_path
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def parse_layup_string(layup_text: str):
    """
    Accepts:
        [0/45/-45/90/90/-45/45/0]
        0,45,-45,90,90,-45,45,0
        0 / 45 / -45 / 90
    """
    nums = re.findall(r"[-+]?\d*\.?\d+", str(layup_text))
    return [float(x) for x in nums]


def format_angle(angle):
    if abs(angle - int(angle)) < 1e-9:
        return f"{int(angle)}°"
    return f"{angle:.1f}°"


def is_symmetric_layup(angles):
    if len(angles) == 0:
        return False
    return angles == list(reversed(angles))


def is_balanced_layup(angles):
    """
    A simplified balance check:
    for every +theta ply, there should be a -theta ply.
    0 and 90 plies are ignored.
    """
    rounded = [round(a, 6) for a in angles]
    non_special = [a for a in rounded if abs(a) not in [0, 90]]

    for a in non_special:
        if non_special.count(a) != non_special.count(-a):
            return False

    return True


def orientation_color(angle):
    """
    Fixed colors for common ply angles.
    """
    a = round(angle)
    color_map = {
        0: "#4C78A8",
        90: "#E45756",
        45: "#54A24B",
        -45: "#F58518",
        30: "#72B7B2",
        -30: "#B279A2",
        20: "#9D755D",
        -20: "#BAB0AC",
    }
    return color_map.get(a, "#8E8E8E")


def create_layup_figure(angles, ply_thickness_mm=0.125, title="Composite Layup Stack"):
    """
    Creates a stacked laminate schematic with fiber direction arrows.
    Top ply is shown at the top.
    """
    n = len(angles)
    if n == 0:
        fig, ax = plt.subplots(figsize=(8, 2))
        ax.text(0.5, 0.5, "No layup entered", ha="center", va="center")
        ax.axis("off")
        return fig

    fig_height = max(4, 0.55 * n + 1.5)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    block_width = 10.0
    ply_height = 1.0

    for idx, angle in enumerate(angles):
        # Display ply 1 at top
        y = n - idx - 1
        color = orientation_color(angle)

        rect = Rectangle(
            (0, y),
            block_width,
            ply_height,
            facecolor=color,
            edgecolor="black",
            linewidth=1.0,
            alpha=0.85,
        )
        ax.add_patch(rect)

        # Text label
        ax.text(
            0.35,
            y + 0.5 * ply_height,
            f"Ply {idx + 1}",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color="black",
        )

        ax.text(
            block_width - 0.35,
            y + 0.5 * ply_height,
            format_angle(angle),
            va="center",
            ha="right",
            fontsize=11,
            fontweight="bold",
            color="black",
        )

        # Fiber direction arrow
        theta = np.deg2rad(angle)
        cx = block_width / 2.0
        cy = y + 0.5 * ply_height

        # Scale dy smaller so arrows fit inside ply rectangles
        dx = 1.35 * np.cos(theta)
        dy = 0.38 * np.sin(theta)

        arrow = FancyArrowPatch(
            (cx - dx, cy - dy),
            (cx + dx, cy + dy),
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=2.0,
            color="black",
        )
        ax.add_patch(arrow)

    # Mid-plane line
    mid_y = n / 2.0
    ax.axhline(mid_y, color="black", linestyle="--", linewidth=1.2)
    ax.text(
        block_width + 0.25,
        mid_y,
        "mid-plane",
        va="center",
        ha="left",
        fontsize=10,
    )

    total_thickness = n * ply_thickness_mm

    ax.set_xlim(0, block_width + 2.0)
    ax.set_ylim(0, n)
    ax.set_aspect("auto")
    ax.set_title(f"{title}\nTotal thickness = {total_thickness:.3f} mm", fontsize=14, fontweight="bold")
    ax.set_xlabel("Laminate schematic width")
    ax.set_ylabel("Through-thickness stack")
    ax.set_yticks([])
    ax.grid(False)

    return fig


def clean_numeric_columns(df):
    """
    Convert columns to numeric only when conversion is meaningful.
    Keeps text columns like Name and Layup unchanged.
    """
    if df is None:
        return None

    out = df.copy()

    for c in out.columns:
        converted = pd.to_numeric(out[c], errors="coerce")

        # Only replace the column if at least one value converted successfully.
        # This avoids turning text columns like layup strings into all-NaN columns.
        if converted.notna().sum() > 0:
            out[c] = converted

    return out


def find_row_by_name(df, name_column, selected_name):
    if df is None or name_column not in df.columns:
        return None
    rows = df[df[name_column].astype(str) == str(selected_name)]
    if len(rows) == 0:
        return None
    return rows.iloc[0]


def plot_bar(df, x_col, y_col, title, ylabel):
    fig, ax = plt.subplots(figsize=(9, 4))
    plot_df = df[[x_col, y_col]].copy()
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna()

    ax.bar(plot_df[x_col].astype(str), plot_df[y_col])
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(plot_df[x_col].astype(str), rotation=30, ha="right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


# -----------------------------
# Load project outputs
# -----------------------------

clt_df = clean_numeric_columns(read_csv_safe("outputs/matlab/clt_layup_summary.csv"))
wingbox_df = clean_numeric_columns(read_csv_safe("outputs/matlab/wingbox/wingbox_stiffness_summary.csv"))
static_df = clean_numeric_columns(read_csv_safe("outputs/matlab/static_aeroelastic/static_aeroelastic_summary.csv"))
divergence_df = clean_numeric_columns(read_csv_safe("outputs/matlab/divergence/divergence_summary.csv"))
flutter_df = clean_numeric_columns(read_csv_safe("outputs/matlab/flutter/flutter_screening_summary.csv"))
avl_static_df = clean_numeric_columns(read_csv_safe("outputs/matlab/static_aeroelastic_avl/avl_static_aeroelastic_summary.csv"))
avl_validation_df = clean_numeric_columns(read_csv_safe("outputs/avl_validation/avl_spanload_validation_summary.csv"))
oas_aero_df = clean_numeric_columns(read_csv_safe("outputs/oas_baseline/oas_aero_baseline_summary.csv"))
oas_as_df = clean_numeric_columns(read_csv_safe("outputs/oas_aerostruct_baseline/oas_aerostruct_baseline_summary.csv"))


# -----------------------------
# Streamlit page setup
# -----------------------------

st.set_page_config(
    page_title="Composite Aeroelastic Tailoring GUI",
    layout="wide",
)

st.title("Composite Aeroelastic Tailoring GUI")
st.caption("Phase 12A — Interactive layup visualization and results dashboard")


# -----------------------------
# Sidebar controls
# -----------------------------

st.sidebar.header("Layup input")

preset_names = []
if clt_df is not None and "Name" in clt_df.columns:
    preset_names = clt_df["Name"].astype(str).tolist()

use_preset = st.sidebar.checkbox("Use preset layup from CLT results", value=True)

if use_preset and preset_names:
    selected_name = st.sidebar.selectbox("Select layup", preset_names, index=0)

    selected_row = find_row_by_name(clt_df, "Name", selected_name)
    if selected_row is not None and "Layup" in selected_row.index:
        layup_text_default = str(selected_row["Layup"])
    else:
        layup_text_default = "[0/45/-45/90/90/-45/45/0]"
else:
    selected_name = "custom_layup"
    layup_text_default = "[0/45/-45/90/90/-45/45/0]"

layup_text = st.sidebar.text_input("Layup sequence", value=layup_text_default)

ply_thickness_mm = st.sidebar.number_input(
    "Ply thickness [mm]",
    min_value=0.01,
    max_value=2.0,
    value=0.125,
    step=0.005,
)

angles = parse_layup_string(layup_text)

st.sidebar.markdown("---")
st.sidebar.write(f"Number of plies: **{len(angles)}**")
st.sidebar.write(f"Total thickness: **{len(angles) * ply_thickness_mm:.3f} mm**")
st.sidebar.write(f"Symmetric: **{is_symmetric_layup(angles)}**")
st.sidebar.write(f"Balanced: **{is_balanced_layup(angles)}**")


# -----------------------------
# Main tabs
# -----------------------------

tab_layup, tab_clt, tab_wingbox, tab_aeroelastic, tab_validation, tab_summary = st.tabs(
    [
        "Layup visualizer",
        "CLT properties",
        "Wingbox stiffness",
        "Aeroelastic results",
        "AVL / OAS validation",
        "Project summary",
    ]
)


# -----------------------------
# Tab 1: Layup visualizer
# -----------------------------

with tab_layup:
    st.subheader("Composite layup stack and fiber orientation")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = create_layup_figure(
            angles,
            ply_thickness_mm=ply_thickness_mm,
            title=f"{selected_name}: {layup_text}",
        )
        st.pyplot(fig)

        save_dir = PROJECT_ROOT / "outputs" / "gui"
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"{selected_name}_layup_visualization.png"

        if st.button("Save current layup schematic as PNG"):
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            st.success(f"Saved: {save_path}")

    with col2:
        st.markdown("### Layup checks")
        st.write(f"**Layup:** `{layup_text}`")
        st.write(f"**Number of plies:** {len(angles)}")
        st.write(f"**Ply thickness:** {ply_thickness_mm:.3f} mm")
        st.write(f"**Total thickness:** {len(angles) * ply_thickness_mm:.3f} mm")
        st.write(f"**Symmetric:** {is_symmetric_layup(angles)}")
        st.write(f"**Balanced:** {is_balanced_layup(angles)}")

        ply_table = pd.DataFrame(
            {
                "Ply number": np.arange(1, len(angles) + 1),
                "Angle_deg": angles,
                "Thickness_mm": [ply_thickness_mm] * len(angles),
                "Role": [
                    "0° axial/bending"
                    if abs(a) == 0
                    else "90° transverse"
                    if abs(a) == 90
                    else "±angle shear/torsion/coupling"
                    for a in angles
                ],
            }
        )
        st.dataframe(ply_table, use_container_width=True)


# -----------------------------
# Tab 2: CLT properties
# -----------------------------

with tab_clt:
    st.subheader("Classical Laminate Theory output")

    if clt_df is None:
        st.warning("CLT summary CSV not found.")
    else:
        st.dataframe(clt_df, use_container_width=True)

        chart_cols = st.columns(3)

        with chart_cols[0]:
            if "Name" in clt_df.columns and "Ex_GPa" in clt_df.columns:
                st.pyplot(plot_bar(clt_df, "Name", "Ex_GPa", "Effective Ex", "Ex [GPa]"))

        with chart_cols[1]:
            if "Name" in clt_df.columns and "Ey_GPa" in clt_df.columns:
                st.pyplot(plot_bar(clt_df, "Name", "Ey_GPa", "Effective Ey", "Ey [GPa]"))

        with chart_cols[2]:
            if "Name" in clt_df.columns and "Gxy_GPa" in clt_df.columns:
                st.pyplot(plot_bar(clt_df, "Name", "Gxy_GPa", "Effective Gxy", "Gxy [GPa]"))


# -----------------------------
# Tab 3: Wingbox stiffness
# -----------------------------

with tab_wingbox:
    st.subheader("Equivalent wingbox stiffness")

    if wingbox_df is None:
        st.warning("Wingbox stiffness summary CSV not found.")
    else:
        st.dataframe(wingbox_df, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            if "Name" in wingbox_df.columns and "EI_avg_Nm2" in wingbox_df.columns:
                st.pyplot(plot_bar(wingbox_df, "Name", "EI_avg_Nm2", "Average bending stiffness", "EI avg [N m²]"))

        with col2:
            if "Name" in wingbox_df.columns and "GJ_avg_Nm2" in wingbox_df.columns:
                st.pyplot(plot_bar(wingbox_df, "Name", "GJ_avg_Nm2", "Average torsional stiffness", "GJ avg [N m²]"))


# -----------------------------
# Tab 4: Aeroelastic results
# -----------------------------

with tab_aeroelastic:
    st.subheader("Static aeroelastic, divergence, and flutter results")

    subtab_static, subtab_div, subtab_flutter, subtab_avl_static = st.tabs(
        ["Static elliptic", "Divergence", "Flutter screening", "AVL static aeroelastic"]
    )

    with subtab_static:
        if static_df is None:
            st.warning("Static aeroelastic summary CSV not found.")
        else:
            st.dataframe(static_df, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if "Name" in static_df.columns and "TipDeflection_mm" in static_df.columns:
                    st.pyplot(plot_bar(static_df, "Name", "TipDeflection_mm", "Tip deflection under elliptic load", "Tip deflection [mm]"))
            with col2:
                if "Name" in static_df.columns and "TipTwistTotal_deg" in static_df.columns:
                    st.pyplot(plot_bar(static_df, "Name", "TipTwistTotal_deg", "Tip twist under elliptic load", "Tip twist [deg]"))

    with subtab_div:
        if divergence_df is None:
            st.warning("Divergence summary CSV not found.")
        else:
            st.dataframe(divergence_df, use_container_width=True)

            if "Name" in divergence_df.columns and "V_div_over_Vcruise" in divergence_df.columns:
                st.pyplot(plot_bar(divergence_df, "Name", "V_div_over_Vcruise", "Divergence speed margin", "Vdiv / Vcruise"))

    with subtab_flutter:
        if flutter_df is None:
            st.warning("Flutter screening summary CSV not found.")
        else:
            st.dataframe(flutter_df, use_container_width=True)

            possible_cols = [c for c in flutter_df.columns if "margin" in c.lower() or "Vf" in c or "flutter" in c.lower()]
            st.write("Detected flutter-related columns:", possible_cols)

    with subtab_avl_static:
        if avl_static_df is None:
            st.warning("AVL static aeroelastic summary CSV not found.")
        else:
            st.dataframe(avl_static_df, use_container_width=True)

            if "layup_name" in avl_static_df.columns and "TipDeflection_mm" in avl_static_df.columns:
                st.pyplot(plot_bar(avl_static_df, "layup_name", "TipDeflection_mm", "Tip deflection using AVL spanload", "Tip deflection [mm]"))


# -----------------------------
# Tab 5: AVL / OAS validation
# -----------------------------

with tab_validation:
    st.subheader("AVL and OpenAeroStruct validation")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### AVL spanload validation")
        if avl_validation_df is None:
            st.warning("AVL validation summary CSV not found.")
        else:
            st.dataframe(avl_validation_df, use_container_width=True)

    with col2:
        st.markdown("### OAS aerodynamic baseline")
        if oas_aero_df is None:
            st.warning("OAS aerodynamic summary CSV not found.")
        else:
            st.dataframe(oas_aero_df, use_container_width=True)

    st.markdown("### OAS aerostructural smoke test")
    if oas_as_df is None:
        st.warning("OAS aerostructural summary CSV not found.")
    else:
        st.dataframe(oas_as_df, use_container_width=True)


# -----------------------------
# Tab 6: Project summary
# -----------------------------

with tab_summary:
    st.subheader("Engineering interpretation")

    st.markdown(
        """
        ### Current conclusion

        The strongest balanced aeroelastic tailoring candidate is **tailored_30**.

        **Why tailored_30 is strong:**
        - Good bending stiffness compared with the baseline.
        - Produces useful passive washout.
        - Avoids the excessive deflection of the 45° torsion-stiff laminate.
        - Maintains acceptable divergence and flutter screening margins.

        **Important tradeoff:**
        - **tailored_20** gives the lowest deflection, but has weaker torsional/divergence margin.
        - **torsion_stiff** gives strong torsional behavior, but bends too much.
        - **axial_stiff** has good bending stiffness, but its twist behavior is less useful for aeroelastic tailoring.

        ### Current model status

        The workflow now includes:

        1. CLT laminate property calculation  
        2. Equivalent wingbox stiffness estimation  
        3. Static aeroelastic response  
        4. Divergence speed estimation  
        5. Flutter screening  
        6. AVL aerodynamic validation  
        7. AVL spanload-based static aeroelasticity  
        8. OAS aerodynamic baseline  
        9. OAS aerostructural smoke test  

        ### Next technical milestone

        **Phase 12B** should connect laminate-derived stiffness/mass into the OAS aerostructural workflow.
        """
    )