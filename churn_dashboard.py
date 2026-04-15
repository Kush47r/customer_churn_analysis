import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Load data ──────────────────────────────────────────────────────────────
df          = pd.read_csv("telco_churn_cleaned.csv")
contract    = pd.read_csv("churn_by_contract.csv")
tenure      = pd.read_csv("churn_by_tenure.csv")
internet    = pd.read_csv("churn_by_internet.csv")
payment     = pd.read_csv("churn_by_payment.csv")
demo        = pd.read_csv("churn_by_demographics.csv")

# ── KPI values ─────────────────────────────────────────────────────────────
total_customers  = len(df)
total_churned    = int(df["Churn_Binary"].sum())
overall_churn    = round(df["Churn_Binary"].mean() * 100, 2)
avg_charges      = round(df["MonthlyCharges"].mean(), 2)

# ── Colour palette ─────────────────────────────────────────────────────────
BG        = "#1a1a2e"
CARD_BG   = "#16213e"
ACCENT    = "#e94560"
BLUE      = "#0f3460"
GREEN     = "#4caf82"
ORANGE    = "#f5a623"
GRAY_TEXT = "#a0aec0"
WHITE     = "#ffffff"

contract_colors = {
    "Month-to-month": "#e94560",
    "One year":       "#f5a623",
    "Two year":       "#4caf82",
}
payment_colors = {
    "Electronic check":             "#e94560",
    "Mailed check":                 "#f5a623",
    "Bank transfer (automatic)":    "#4caf82",
    "Credit card (automatic)":      "#00b4d8",
}
internet_colors = ["#e94560", "#00b4d8", "#4caf82"]

tenure_avg = round(tenure["churn_rate"].mean(), 2)

# ── Build figure ───────────────────────────────────────────────────────────
fig = make_subplots(
    rows=4, cols=3,
    row_heights=[0.10, 0.38, 0.38, 0.14],
    column_widths=[0.34, 0.34, 0.32],
    specs=[
        [{"colspan": 3}, None, None],            # row 1 – KPI cards (fake)
        [{"type": "xy"},  {"type": "xy"},  {"type": "domain"}],  # row 2
        [{"type": "xy"},  {"type": "xy"},  {"type": "xy"}],      # row 3
        [{"colspan": 3}, None, None],            # row 4 – footer
    ],
    vertical_spacing=0.06,
    horizontal_spacing=0.05,
)

# ── Row 1: KPI cards via annotations (plotly trick) ────────────────────────
kpis = [
    ("Total Customers",   f"{total_customers:,}",   WHITE),
    ("Churned Customers", f"{total_churned:,}",      ACCENT),
    ("Churn Rate",        f"{overall_churn}%",       ORANGE),
    ("Avg Monthly Charges", f"${avg_charges}",       GREEN),
]
for i, (label, value, color) in enumerate(kpis):
    x_center = 0.04 + i * 0.245
    fig.add_annotation(
        x=x_center, y=0.96, xref="paper", yref="paper",
        text=f"<b style='font-size:26px;color:{color}'>{value}</b><br>"
             f"<span style='font-size:12px;color:{GRAY_TEXT}'>{label}</span>",
        showarrow=False, align="center",
        bgcolor=CARD_BG, bordercolor=BLUE, borderwidth=1,
        borderpad=12,
    )

# ── Row 2 Left: Churn by Contract (horizontal bar) ────────────────────────
contract_sorted = contract.sort_values("churn_rate", ascending=True)
bar_colors_c = [contract_colors.get(c, ACCENT) for c in contract_sorted["Contract"]]
fig.add_trace(
    go.Bar(
        y=contract_sorted["Contract"],
        x=contract_sorted["churn_rate"],
        orientation="h",
        marker_color=bar_colors_c,
        text=[f"{v:.1f}%" for v in contract_sorted["churn_rate"]],
        textposition="outside",
        textfont=dict(color=WHITE, size=12),
        hovertemplate="<b>%{y}</b><br>Churn Rate: %{x:.1f}%<extra></extra>",
        name="",
    ),
    row=2, col=1,
)

# ── Row 2 Middle: Churn by Tenure (column chart + avg line) ───────────────
tenure_order = ["0-12 months","13-24 months","25-36 months","37-48 months",
                "49-60 months","61-72 months"]
tenure_plot = tenure.set_index("tenure_group").reindex(tenure_order).reset_index()

t_colors = [ACCENT if r >= tenure_avg else BLUE
            for r in tenure_plot["churn_rate"]]
fig.add_trace(
    go.Bar(
        x=tenure_plot["tenure_group"],
        y=tenure_plot["churn_rate"],
        marker_color=t_colors,
        text=[f"{v:.1f}%" for v in tenure_plot["churn_rate"]],
        textposition="outside",
        textfont=dict(color=WHITE, size=10),
        hovertemplate="<b>%{x}</b><br>Churn Rate: %{y:.1f}%<extra></extra>",
        name="",
    ),
    row=2, col=2,
)
fig.add_hline(
    y=tenure_avg, line_dash="dash", line_color=ORANGE, line_width=2,
    annotation_text=f"Avg {tenure_avg}%",
    annotation_font_color=ORANGE,
    row=2, col=2,
)

# ── Row 2 Right: Internet Service donut ───────────────────────────────────
fig.add_trace(
    go.Pie(
        labels=internet["InternetService"],
        values=internet["churned"],
        hole=0.55,
        marker_colors=internet_colors,
        textinfo="label+percent",
        textfont=dict(color=WHITE, size=11),
        hovertemplate="<b>%{label}</b><br>Churned: %{value:,}<br>%{percent}<extra></extra>",
        name="",
    ),
    row=2, col=3,
)

# ── Row 3 Left: Payment Method bar ────────────────────────────────────────
payment_sorted = payment.sort_values("churn_rate", ascending=True)
bar_colors_p = [payment_colors.get(p, ACCENT) for p in payment_sorted["PaymentMethod"]]
fig.add_trace(
    go.Bar(
        y=payment_sorted["PaymentMethod"],
        x=payment_sorted["churn_rate"],
        orientation="h",
        marker_color=bar_colors_p,
        text=[f"{v:.1f}%" for v in payment_sorted["churn_rate"]],
        textposition="outside",
        textfont=dict(color=WHITE, size=12),
        hovertemplate="<b>%{y}</b><br>Churn Rate: %{x:.1f}%<extra></extra>",
        name="",
    ),
    row=3, col=1,
)
payment_avg = round(payment["churn_rate"].mean(), 2)
fig.add_vline(
    x=payment_avg, line_dash="dash", line_color=ORANGE, line_width=2,
    annotation_text=f"Avg {payment_avg}%",
    annotation_font_color=ORANGE,
    row=3, col=1,
)

# ── Row 3 Middle: Monthly Charges distribution ────────────────────────────
churned     = df[df["Churn"] == "Yes"]["MonthlyCharges"]
retained    = df[df["Churn"] == "No"]["MonthlyCharges"]
fig.add_trace(
    go.Histogram(x=retained, nbinsx=30, name="Retained",
                 marker_color=BLUE, opacity=0.75,
                 hovertemplate="Charges: %{x}<br>Count: %{y}<extra>Retained</extra>"),
    row=3, col=2,
)
fig.add_trace(
    go.Histogram(x=churned, nbinsx=30, name="Churned",
                 marker_color=ACCENT, opacity=0.75,
                 hovertemplate="Charges: %{x}<br>Count: %{y}<extra>Churned</extra>"),
    row=3, col=2,
)

# ── Row 3 Right: Demographics bar ─────────────────────────────────────────
for gender, color in [("Female", "#f06292"), ("Male", "#00b4d8")]:
    d = demo[demo["gender"] == gender]
    fig.add_trace(
        go.Bar(
            x=d["churn_rate"],
            y=d["SeniorCitizen_Label"],
            orientation="h",
            name=gender,
            marker_color=color,
            text=[f"{v:.1f}%" for v in d["churn_rate"]],
            textposition="outside",
            textfont=dict(color=WHITE, size=11),
            hovertemplate=f"<b>%{{y}} ({gender})</b><br>Churn Rate: %{{x:.1f}}%<extra></extra>",
        ),
        row=3, col=3,
    )

# ── Row 4: Footer annotation ───────────────────────────────────────────────
fig.add_annotation(
    x=0.5, y=0.01, xref="paper", yref="paper",
    text="<span style='color:#a0aec0;font-size:11px'>"
         "Source: Telco Customer Churn Dataset  |  "
         "Built with Python + Plotly  |  2024</span>",
    showarrow=False, align="center",
)

# ── Global layout ──────────────────────────────────────────────────────────
axis_style = dict(
    color=GRAY_TEXT, gridcolor="#2d3748", zerolinecolor="#2d3748",
    tickfont=dict(color=GRAY_TEXT, size=10),
)
fig.update_layout(
    title=dict(
        text="<b>Customer Churn Analysis Dashboard</b>  "
             "<span style='font-size:14px;color:#a0aec0'>— Telco 2024</span>",
        font=dict(size=22, color=WHITE),
        x=0.5, xanchor="center", y=0.99,
    ),
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(color=WHITE, family="Segoe UI, Arial"),
    height=950,
    margin=dict(t=70, b=40, l=20, r=20),
    showlegend=True,
    legend=dict(
        bgcolor=CARD_BG, bordercolor=BLUE, borderwidth=1,
        font=dict(color=WHITE, size=11), x=0.77, y=0.15,
    ),
    barmode="overlay",
)

# Apply axis styles to all xy subplots
for axis in ["xaxis", "yaxis", "xaxis2", "yaxis2", "xaxis3", "yaxis3",
             "xaxis4", "yaxis4", "xaxis5", "yaxis5", "xaxis6", "yaxis6"]:
    fig.update_layout(**{axis: axis_style})

# Chart titles via annotations
chart_titles = [
    (0.17,  0.695, "Churn Rate by Contract Type"),
    (0.50,  0.695, "Churn Rate by Tenure Group"),
    (0.84,  0.695, "Churned by Internet Service"),
    (0.17,  0.305, "Churn Rate by Payment Method"),
    (0.50,  0.305, "Monthly Charges Distribution"),
    (0.84,  0.305, "Churn Rate by Demographics"),
]
for cx, cy, title in chart_titles:
    fig.add_annotation(
        x=cx, y=cy, xref="paper", yref="paper",
        text=f"<b style='font-size:13px'>{title}</b>",
        showarrow=False, font=dict(color=WHITE),
    )

# ── Save ───────────────────────────────────────────────────────────────────
output = "churn_dashboard.html"
fig.write_html(output, include_plotlyjs="cdn")
print(f"Dashboard saved → {output}")
print("Open the file in any browser to view it.")
