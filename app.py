"""Company Atlas — run with: streamlit run app.py"""
from pathlib import Path
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analytics import (REVENUE, GROWTH, PRIOR, CHANGE, RPE, GROUP,
                       load_data, totals, add_shares, sector_summary, filter_data)

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Company Atlas", page_icon="◈", layout="wide")
TEAL, BLUE, RED, TEXT = "#53ddbd", "#76a9ff", "#ff7e91", "#e7edf5"
PALETTE = [TEAL, BLUE, "#ae9cfa", "#f5c577", "#fd9fa8", "#6ed2f4", "#b6d67c",
           "#e7b3ed", "#f5a26c", "#9bc4ce", "#cad7f2", "#d0bc8d", "#929ff0"]
st.markdown("""<style>
.stApp {background: #0b1120;}
.block-container {padding-top: 4.5rem; padding-bottom: 2rem; max-width: 1580px;}
[data-testid="stSidebar"] {background: #101a2c; border-right: 1px solid #243149;}
[data-testid="stMetric"] {background: #121e32; border: 1px solid #283650;
 border-radius: 12px; padding: 18px 18px 15px; min-height: 125px;}
[data-testid="stMetricLabel"] {color: #a9b9ce;}
[data-testid="stMetricValue"] {font-size: clamp(1.3rem, 2.1vw, 2.1rem); color: #f1f5fa;}
h1 {font-weight: 760; letter-spacing: -1.6px; font-size: 2.9rem;}
h3 {font-size: 1.18rem; letter-spacing: -.3px;}
.eyebrow {color: #53ddbd; font-size: .76rem; letter-spacing: .19em; font-weight: 700;}
.subtitle {color: #aab9cf; margin: -.3rem 0 1.4rem; font-size: 1.02rem;}
.rule {border-top: 1px solid #283650; margin: 1.6rem 0;}
button[role="tab"] {font-size: 1rem;}
@media (max-width: 700px) {.block-container {padding: 4.5rem 1rem 1.5rem;} h1 {font-size: 2rem;}}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def parse(content):
    return load_data(content)


def money(millions, signed=False):
    if not math.isfinite(millions):
        return "N/A"
    prefix = "+" if signed and millions > 0 else "−" if millions < 0 else ""
    n = abs(millions)
    if n >= 1_000_000:
        return f"{prefix}${n / 1_000_000:,.2f}T"
    if n >= 1_000:
        return f"{prefix}${n / 1_000:,.2f}B"
    return f"{prefix}${n:,.1f}M"


def rate(value):
    return f"{value:+.1f}%" if math.isfinite(value) else "N/A"


def polish(fig, height=440):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", height=height,
                      margin=dict(l=4, r=24, t=15, b=12), font=dict(color=TEXT, size=12),
                      colorway=PALETTE, legend_title_text="",
                      hoverlabel=dict(bgcolor="#1c2d46", font_size=13),
                      xaxis=dict(gridcolor="#243149", zerolinecolor="#53647d"),
                      yaxis=dict(gridcolor="#243149", zerolinecolor="#53647d"))
    return fig


def show(fig, key):
    st.plotly_chart(fig, width="stretch", key=key,
                    config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


def bars(frame, metric, labels, key, color=TEAL, diverging=False, suffix="", limit=None):
    data = frame.sort_values(metric, ascending=False)
    if limit:
        data = data.head(limit)
    fig = go.Figure(go.Bar(
        x=data[metric], y=data[labels], orientation="h",
        marker_color=[RED if v < 0 else color for v in data[metric]] if diverging else color,
        text=[f"{v:,.1f}{suffix}" if suffix or abs(v) < 100 else f"{v:,.0f}" for v in data[metric]],
        textposition="auto", cliponaxis=False,
        hovertemplate="%{y}<br>%{x:,.2f}" + suffix + "<extra></extra>"))
    fig.update_yaxes(autorange="reversed", title=None, automargin=True)
    if labels == GROUP:
        short = {"Healthcare and Pharmaceuticals": "Healthcare & pharma",
                 "Transportation and Logistics": "Transport & logistics",
                 "Media and Entertainment": "Media & entertainment",
                 "Food and Beverages": "Food & beverages"}
        fig.update_yaxes(tickmode="array", tickvals=data[labels],
                         ticktext=[short.get(v, v) for v in data[labels]])
    fig.update_xaxes(title=metric, ticksuffix=suffix)
    show(polish(fig, max(340, min(760, len(data) * 32 + 75))), key)


def table(frame, key):
    config = {
        REVENUE: st.column_config.NumberColumn("Revenue · USD M", format="localized"),
        GROWTH: st.column_config.NumberColumn("Revenue growth · %", format="%.1f"),
        PRIOR: st.column_config.NumberColumn("Prior revenue · est. USD M", format="%.1f"),
        CHANGE: st.column_config.NumberColumn("Revenue change · est. USD M", format="%.1f"),
        RPE: st.column_config.NumberColumn("Revenue / employee · USD", format="$%.0f"),
        "Revenue share (%)": st.column_config.NumberColumn("Revenue share · %", format="%.2f"),
        "Employee share (%)": st.column_config.NumberColumn("Employee share · %", format="%.2f"),
        "Company share (%)": st.column_config.NumberColumn("Company share · %", format="%.2f"),
        "Employees": st.column_config.NumberColumn("Employees", format="localized")}
    st.dataframe(frame, column_config=config, hide_index=True, width="stretch", key=key)


with st.sidebar:
    st.markdown("### ◈ Company Atlas")
    st.caption("A clear view of company scale and growth.")
    uploaded = st.file_uploader("Replace snapshot (optional)", type=["csv"],
                                 help="Use the same English headers and numeric formats as the bundled CSV.")
try:
    content = uploaded.getvalue() if uploaded is not None else (ROOT / "data" / "companies.csv").read_bytes()
    df = parse(content)
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()

groups = sorted(df[GROUP].unique())
colors = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(groups)}
with st.sidebar:
    with st.form("filters"):
        st.markdown("#### Refine the view")
        sectors = st.multiselect("Industry groups", groups, default=groups, key="sectors")
        query = st.text_input("Find a company", placeholder="Name contains…", key="query")
        direction = st.selectbox("Revenue direction", ["All companies", "Growing revenue", "Declining revenue", "Unchanged revenue"], key="direction")
        st.form_submit_button("Apply filters", width="stretch")
    st.divider()
    basis = st.radio("Share denominator", ["Current selection", "Full dataset"], key="share_basis",
                     help="Defines the denominator of every revenue, employee and company share.")
    unit = st.selectbox("Chart revenue unit", ["USD billions", "USD millions"], key="revenue_unit")
    top_n = st.slider("Companies in rankings", 5, 30, 10, step=5, key="top_n")
    st.caption("Filters affect all views. Top N only limits company charts; totals and percentage denominators use all selected companies.")
    st.caption("Source: bundled CSV snapshot. Reporting dates are not provided. No live feed or API required.")

selected = filter_data(df, sectors, query, direction)
st.markdown('<div class="eyebrow">BUSINESS INTELLIGENCE / COMPANY SNAPSHOT</div>', unsafe_allow_html=True)
st.title("Company Atlas")
st.markdown('<div class="subtitle">See the scale. Compare the pace. Understand the people behind the numbers.</div>', unsafe_allow_html=True)
st.caption(f"{len(selected):,} of {len(df):,} companies selected · {selected[GROUP].nunique()} of {len(groups)} industry groups · All values in USD · Interface in English")
if selected.empty:
    st.info("No companies match these filters. Select an industry group or broaden the company search and apply filters.")
    st.stop()

overall, current = totals(df), totals(selected)
denom = current if basis == "Current selection" else overall
companies = add_shares(selected, denom)
sectors_df = sector_summary(selected, denom)
divisor = 1000 if unit == "USD billions" else 1
unit_short = "USD B" if divisor == 1000 else "USD M"
rev_label, delta_label = f"Revenue ({unit_short})", f"Revenue change · estimated ({unit_short})"
companies[rev_label], companies[delta_label] = companies[REVENUE] / divisor, companies[CHANGE] / divisor
sectors_df[rev_label], sectors_df[delta_label] = sectors_df[REVENUE] / divisor, sectors_df[CHANGE] / divisor

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total revenue", money(current["revenue"]), help="Revenue is sales/income reported by the source, not profit. Source monetary values are USD millions.")
c2.metric("Total employees", f'{current["employees"]:,}', help="Sum of the selected headcounts. This is a snapshot, not jobs created.")
c3.metric("Companies", f'{current["companies"]:,}', help="All selected rows are included in totals, regardless of Top N.")
c4.metric("Est. aggregate growth", rate(current["growth"]),
          help="Calculated from total current revenue and reconstructed prior revenue; not an average of company growth rates.")
st.caption(f"Share basis: {basis.lower()} — {denom['companies']:,} companies, {money(denom['revenue'])} revenue, {denom['employees']:,} employees. Growth and dollar changes use reported rates; reconstructed amounts are approximate.")

overview, growth, workforce, explorer, method = st.tabs(["Overview", "Growth & scale", "Workforce", "Company explorer", "Data & methodology"])

with overview:
    st.markdown("### The sector landscape")
    st.caption("Sector totals include only companies in this snapshot and your active selection.")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("#### Revenue by industry group")
        bars(sectors_df, rev_label, GROUP, "sector_revenue")
    with right:
        st.markdown("#### Where the workforce is concentrated")
        bars(sectors_df, "Employee share (%)", GROUP, "sector_employee_share", color=BLUE, suffix="%")
    a, b, c = st.columns(3)
    leader = selected.loc[selected[REVENUE].idxmax()]
    fastest = selected.loc[selected[GROWTH].idxmax()]
    employer = selected.loc[selected["Employees"].idxmax()]
    a.info(f"**Revenue leader**\n\n{leader['Name']} · {money(leader[REVENUE])}")
    b.info(f"**Fastest reported revenue growth**\n\n{fastest['Name']} · {rate(fastest[GROWTH])}")
    c.info(f"**Largest employer**\n\n{employer['Name']} · {employer['Employees']:,} employees")
    st.markdown("#### Sector scorecard")
    table(sectors_df[[GROUP, "Companies", REVENUE, "Revenue share (%)", GROWTH, CHANGE, "Employees", "Employee share (%)"]].sort_values(REVENUE, ascending=False), "sector_scorecard")

with growth:
    st.markdown("### Percentage growth and dollar impact answer different questions")
    st.caption("Percentages show pace; estimated dollar change shows financial scale. These are reported comparisons, not a historical time series.")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Aggregate growth by sector · estimated")
        bars(sectors_df, GROWTH, GROUP, "sector_growth", diverging=True, suffix="%")
    with right:
        st.markdown("#### Revenue change by sector · estimated")
        bars(sectors_df, delta_label, GROUP, "sector_change", diverging=True)
    st.markdown("#### Which companies combine pace and financial impact?")
    scatter = px.scatter(companies, x=GROWTH, y=delta_label, size=REVENUE,
                         color=GROUP, color_discrete_map=colors, hover_name="Name",
                         hover_data={GROUP: True, REVENUE: ":,.0f", "Employees": ":,", GROWTH: ":.1f", delta_label: ":,.2f"},
                         size_max=52, labels={GROWTH: "Reported revenue growth (%)"})
    scatter.add_hline(y=0, line_color="#53647d", line_width=1)
    scatter.add_vline(x=0, line_color="#53647d", line_width=1)
    scatter.update_layout(legend=dict(orientation="h", yanchor="top", y=-.2))
    show(polish(scatter, 590), "growth_scatter")
    st.caption("Each bubble is a company. Bubble area represents current revenue. The vertical axis is reconstructed dollar change.")
    metric = st.radio("Company ranking", ["Reported growth (%)", "Estimated revenue change"], horizontal=True, key="rank_metric")
    ranking_metric = GROWTH if metric == "Reported growth (%)" else delta_label
    left, right = st.columns(2)
    with left:
        st.markdown(f"#### Top {min(top_n, len(companies))} · highest values")
        bars(companies, ranking_metric, "Name", "company_growth_top", diverging=True, suffix="%" if ranking_metric == GROWTH else "", limit=top_n)
    with right:
        st.markdown(f"#### Bottom {min(top_n, len(companies))} · lowest values")
        bottom = companies.nsmallest(top_n, ranking_metric)
        bars(bottom, ranking_metric, "Name", "company_growth_bottom", diverging=True, suffix="%" if ranking_metric == GROWTH else "")

with workforce:
    st.markdown("### Headcount, concentration and revenue per employee")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Employees by sector · absolute")
        bars(sectors_df, "Employees", GROUP, "employees_sector", color=BLUE)
    with right:
        st.markdown("#### Employee share by company")
        bars(companies, "Employee share (%)", "Name", "employees_company_share", color=BLUE, suffix="%", limit=top_n)
    st.markdown("#### Largest employers")
    workforce_cols = ["Name", GROUP, "Employees", "Employee share (%)", REVENUE, RPE]
    table(companies[workforce_cols].sort_values("Employees", ascending=False), "workforce_table")
    with st.expander("How should I interpret revenue per employee?"):
        st.write("Revenue per employee = revenue in USD ÷ reported employees. It is a descriptive ratio, not profit per employee or a direct measure of worker productivity. Business models, outsourcing, fiscal periods and headcount definitions can differ. There is no prior employee count, so employee growth cannot be calculated.")

with explorer:
    st.markdown("### Explore a company")
    name = st.selectbox("Company", sorted(companies["Name"].tolist()), key="company")
    row = companies.loc[companies["Name"].eq(name)].iloc[0]
    st.markdown(f"#### {name}")
    st.caption(f"{row[GROUP]} · Original industry: {row['Industry']} · Headquarters: {row['Headquarters']} · Source rank: {row['Rank']}")
    a, b, c = st.columns(3)
    a.metric("Revenue", money(row[REVENUE]))
    b.metric("Reported revenue growth", rate(row[GROWTH]))
    c.metric("Revenue change · estimated", money(row[CHANGE], signed=True))
    a, b, c = st.columns(3)
    a.metric("Employees", f"{row['Employees']:,}")
    b.metric("Revenue share", f"{row['Revenue share (%)']:.2f}%")
    c.metric("Employee share", f"{row['Employee share (%)']:.2f}%")
    st.caption(f"Percentage denominator: {basis.lower()}. No employee growth is available.")
    st.markdown("#### All selected companies")
    table(companies[["Rank", "Name", GROUP, REVENUE, GROWTH, CHANGE, "Employees", "Revenue share (%)", "Employee share (%)", RPE]].sort_values(REVENUE, ascending=False), "company_table")

with method:
    st.markdown("### Transparent calculations, reusable data")
    st.write("This app reads a bundled CSV snapshot. It makes no external data or AI calls. The dataset contains company revenue, reported revenue growth, employee headcount and a curated industry group. Original source columns are preserved in the bundled CSV.")
    st.markdown("""
| Measure | Definition |
|---|---|
| Revenue | Source value in USD millions; not profit |
| Reported growth | The Revenue growth percentage supplied by the CSV |
| Prior revenue · estimated | Current revenue ÷ (1 + reported growth / 100) |
| Revenue change · estimated | Current revenue − reconstructed prior revenue |
| Sector / selection growth · estimated | (Sum of current revenue ÷ sum of reconstructed prior revenue − 1) × 100 |
| Revenue / employee shares | Company or sector total ÷ the chosen denominator × 100 |
| Revenue per employee | Revenue × 1,000,000 ÷ employee count |
""")
    st.warning("The file does not identify fiscal dates or the original source URL. Growth rates are rounded, so prior revenue and dollar changes are estimates. Aggregated growth assumes each supplied rate describes a comparable prior period; it is not a verified calendar-year sector statistic. No multi-year trend can be inferred.")
    st.write("Industry groups are broad, curated categories. A company belongs to one group, even when it operates across several industries. Sector results describe only the companies included here, not the entire market. Reported revenues can include transactions between companies; their sum is not GDP, market value or profit.")
    st.write("Original ranks are retained as supplied. All visual revenue rankings sort by the actual revenue column; source ranks may not follow that order exactly.")
    downloads = companies.drop(columns=[rev_label, delta_label])
    a, b = st.columns(2)
    a.download_button("Download selected companies · CSV", downloads.to_csv(index=False).encode("utf-8-sig"), "selected_companies.csv", "text/csv", width="stretch")
    b.download_button("Download sector summary · CSV", sectors_df.drop(columns=[rev_label, delta_label]).to_csv(index=False).encode("utf-8-sig"), "sector_summary.csv", "text/csv", width="stretch")
    st.caption(f"Both downloads use the current filters and the '{basis.lower()}' share denominator. Monetary column headers specify USD millions. Growth/share columns store percentage points (6.0 means 6%).")
    st.markdown("#### Original snapshot")
    st.download_button("Download original data · CSV", content, "companies.csv", "text/csv")

st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
st.caption("COMPANY ATLAS · Static source, interactive perspective · Estimates are labelled throughout.")
