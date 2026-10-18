"""Company Atlas — run with: streamlit run app.py"""
from pathlib import Path
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from analytics import REVENUE, GROWTH, PRIOR, CHANGE, RPE, GROUP, load_data, totals, add_shares, sector_summary, filter_data
ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Company Atlas', page_icon='◈', layout='wide')

# UI localization only: source columns and analytical filter values stay unchanged.
import re
with st.sidebar:
    language = st.selectbox("Idioma / Language", ["Português", "English"], key="language")
_PT = {'A clear view of company scale and growth.': 'Uma visão clara do porte e crescimento das empresas.', 'Replace snapshot (optional)': 'Substituir base (opcional)', 'Use the same English headers and numeric formats as the bundled CSV.': 'Use os mesmos cabeçalhos em inglês e formatos numéricos do CSV original.', 'Refine the view': 'Refine a visualização', 'Industry groups': 'Setores', 'Find a company': 'Buscar empresa', 'Name contains…': 'Nome contém…', 'Revenue direction': 'Variação da receita', 'All companies': 'Todas as empresas', 'Growing revenue': 'Receita em crescimento', 'Declining revenue': 'Receita em queda', 'Unchanged revenue': 'Receita estável', 'Apply filters': 'Aplicar filtros', 'Share denominator': 'Base dos percentuais', 'Current selection': 'Seleção atual', 'Full dataset': 'Base completa', 'current selection': 'seleção atual', 'full dataset': 'base completa', 'Defines the denominator of every revenue, employee and company share.': 'Define a base dos percentuais de receita, funcionários e empresas.', 'Chart revenue unit': 'Unidade de receita nos gráficos', 'USD billions': 'Bilhões de USD', 'USD millions': 'Milhões de USD', 'Companies in rankings': 'Empresas nos rankings', 'Filters affect all views. Top N only limits company charts; totals and percentage denominators use all selected companies.': 'Os filtros afetam todas as abas. O limite do ranking se aplica aos gráficos de empresas; os totais e percentuais consideram toda a seleção.', 'Source: bundled CSV snapshot. Reporting dates are not provided. No live feed or API required.': 'Fonte: arquivo CSV incluído. Datas de referência não informadas. Não requer API nem atualização em tempo real.', 'BUSINESS INTELLIGENCE / COMPANY SNAPSHOT': 'INTELIGÊNCIA DE NEGÓCIOS / PANORAMA EMPRESARIAL', 'See the scale. Compare the pace. Understand the people behind the numbers.': 'Veja o porte. Compare o crescimento. Conheça as pessoas por trás dos números.', ' companies selected': ' empresas selecionadas', ' industry groups': ' setores', 'All values in USD · Interface in English': 'Valores em USD · Interface em português', ' of ': ' de ', 'No companies match these filters. Select an industry group or broaden the company search and apply filters.': 'Nenhuma empresa corresponde aos filtros. Selecione um setor ou amplie a busca e aplique os filtros.', 'Total revenue': 'Receita total', 'Total employees': 'Total de funcionários', 'Est. aggregate growth': 'Crescimento agregado estimado', 'Revenue is sales/income reported by the source, not profit. Source monetary values are USD millions.': 'Receita é o faturamento informado pela fonte, não o lucro. Valores originais em milhões de USD.', 'Sum of the selected headcounts. This is a snapshot, not jobs created.': 'Soma dos funcionários das empresas selecionadas. Não representa empregos criados.', 'All selected rows are included in totals, regardless of Top N.': 'Todas as empresas selecionadas entram nos totais, independentemente do limite do ranking.', 'Calculated from total current revenue and reconstructed prior revenue; not an average of company growth rates.': 'Calculado a partir da receita atual total e da receita anterior reconstruída; não é uma média simples das taxas.', 'Share basis:': 'Base dos percentuais:', 'Growth and dollar changes use reported rates; reconstructed amounts are approximate.': 'Crescimento e variações em dólares usam as taxas informadas; os valores reconstruídos são aproximados.', 'Overview': 'Visão geral', 'Growth & scale': 'Crescimento e porte', 'Workforce': 'Funcionários', 'Company explorer': 'Explorar empresas', 'Data & methodology': 'Dados e metodologia', 'The sector landscape': 'Panorama dos setores', 'Sector totals include only companies in this snapshot and your active selection.': 'Os totais por setor incluem apenas as empresas desta base e da seleção ativa.', 'Revenue by industry group': 'Receita por setor', 'Where the workforce is concentrated': 'Onde os funcionários estão concentrados', 'Revenue leader': 'Líder em receita', 'Fastest reported revenue growth': 'Maior crescimento de receita informado', 'Largest employer': 'Maior empregador', 'Sector scorecard': 'Indicadores por setor', 'Percentage growth and dollar impact answer different questions': 'Crescimento percentual e impacto em dólares respondem a perguntas diferentes', 'Percentages show pace; estimated dollar change shows financial scale. These are reported comparisons, not a historical time series.': 'Os percentuais mostram o ritmo; a variação estimada em dólares mostra o porte financeiro. São comparações informadas, não uma série histórica.', 'Aggregate growth by sector · estimated': 'Crescimento agregado por setor · estimado', 'Revenue change by sector · estimated': 'Variação da receita por setor · estimada', 'Which companies combine pace and financial impact?': 'Quais empresas combinam crescimento e impacto financeiro?', 'Reported revenue growth (%)': 'Crescimento da receita informado (%)', 'Each bubble is a company. Bubble area represents current revenue. The vertical axis is reconstructed dollar change.': 'Cada bolha representa uma empresa. A área indica a receita atual; o eixo vertical mostra a variação reconstruída em dólares.', 'Company ranking': 'Ranking de empresas', 'Reported growth (%)': 'Crescimento informado (%)', 'Estimated revenue change': 'Variação estimada da receita', 'highest values': 'maiores valores', 'lowest values': 'menores valores', 'Bottom ': 'Últimas ', 'Headcount, concentration and revenue per employee': 'Funcionários, concentração e receita por funcionário', 'Employees by sector · absolute': 'Funcionários por setor · total absoluto', 'Employee share by company': 'Participação de funcionários por empresa', 'Largest employers': 'Maiores empregadores', 'How should I interpret revenue per employee?': 'Como interpretar a receita por funcionário?', 'Revenue per employee = revenue in USD ÷ reported employees. It is a descriptive ratio, not profit per employee or a direct measure of worker productivity. Business models, outsourcing, fiscal periods and headcount definitions can differ. There is no prior employee count, so employee growth cannot be calculated.': 'Receita por funcionário = receita em USD ÷ funcionários informados. É uma razão descritiva, não lucro por funcionário nem medida direta de produtividade. Modelos de negócio, terceirização, períodos e definições de pessoal podem variar. Sem o quadro anterior, não é possível calcular crescimento de funcionários.', 'Explore a company': 'Explore uma empresa', 'Original industry:': 'Setor original:', 'Headquarters:': 'Sede:', 'Source rank:': 'Posição na fonte:', 'Reported revenue growth': 'Crescimento da receita informado', 'Revenue change · estimated': 'Variação da receita · estimada', 'Revenue share': 'Participação na receita', 'Employee share': 'Participação nos funcionários', 'Company share': 'Participação das empresas', 'Percentage denominator:': 'Base do percentual:', 'No employee growth is available.': 'Crescimento de funcionários indisponível.', 'All selected companies': 'Todas as empresas selecionadas', 'Transparent calculations, reusable data': 'Cálculos transparentes, dados reutilizáveis', 'This app reads a bundled CSV snapshot. It makes no external data or AI calls. The dataset contains company revenue, reported revenue growth, employee headcount and a curated industry group. Original source columns are preserved in the bundled CSV.': 'Este app lê o arquivo CSV incluído, sem consultas externas nem chamadas de IA. A base contém receita, crescimento informado, funcionários e setores agrupados. As colunas originais são preservadas no CSV.', 'The file does not identify fiscal dates or the original source URL. Growth rates are rounded, so prior revenue and dollar changes are estimates. Aggregated growth assumes each supplied rate describes a comparable prior period; it is not a verified calendar-year sector statistic. No multi-year trend can be inferred.': 'O arquivo não informa datas fiscais nem a URL da fonte original. As taxas são arredondadas; receita anterior e variações monetárias são estimativas. O crescimento agregado pressupõe períodos comparáveis. Não é uma estatística setorial anual verificada e não permite inferir tendências de vários anos.', 'Industry groups are broad, curated categories. A company belongs to one group, even when it operates across several industries. Sector results describe only the companies included here, not the entire market. Reported revenues can include transactions between companies; their sum is not GDP, market value or profit.': 'Os setores são categorias amplas definidas para esta análise. Cada empresa pertence a um grupo, mesmo atuando em vários segmentos. Os resultados descrevem apenas as empresas incluídas, não todo o mercado. A receita pode incluir transações entre empresas; sua soma não é PIB, valor de mercado nem lucro.', 'Original ranks are retained as supplied. All visual revenue rankings sort by the actual revenue column; source ranks may not follow that order exactly.': 'As posições originais são preservadas. Os rankings visuais ordenam a receita real; a ordem da fonte pode diferir.', 'Download selected companies · CSV': 'Baixar empresas selecionadas · CSV', 'Download sector summary · CSV': 'Baixar resumo por setor · CSV', "Both downloads use the current filters and the '": "Os dois arquivos usam os filtros atuais e a base '", "' share denominator. Monetary column headers specify USD millions. Growth/share columns store percentage points (6.0 means 6%).": "' nos percentuais. Cabeçalhos monetários indicam milhões de USD. Nas colunas percentuais, 6.0 significa 6%.", 'Original snapshot': 'Base original', 'Download original data · CSV': 'Baixar dados originais · CSV', 'COMPANY ATLAS · Static source, interactive perspective · Estimates are labelled throughout.': 'COMPANY ATLAS · Base estática, visão interativa · Estimativas identificadas.', 'Revenue growth': 'Crescimento da receita', 'Prior revenue': 'Receita anterior', 'Revenue change': 'Variação da receita', 'Revenue / employee': 'Receita / funcionário', 'Revenue per employee': 'Receita por funcionário', 'Employee share (%)': 'Participação nos funcionários (%)', 'Revenue share (%)': 'Participação na receita (%)', 'Company share (%)': 'Participação das empresas (%)', 'Industry Group': 'Setor agrupado', 'Companies': 'Empresas', 'Company': 'Empresa', 'Employees': 'Funcionários', 'employees': 'funcionários', 'Revenue': 'Receita', 'revenue': 'receita', 'Name': 'Nome', 'Rank': 'Posição', 'Headquarters': 'Sede', 'Industry': 'Setor', 'estimated': 'estimada', 'Agribusiness': 'Agronegócio', 'Automotive': 'Automotivo', 'Conglomerates': 'Conglomerados', 'Energy': 'Energia', 'Financial Services': 'Serviços financeiros', 'Food and Beverages': 'Alimentos e bebidas', 'Healthcare and Pharmaceuticals': 'Saúde e farmacêutico', 'Industrials': 'Indústria', 'Media and Entertainment': 'Mídia e entretenimento', 'Retail': 'Varejo', 'Technology': 'Tecnologia', 'Telecommunications': 'Telecomunicações', 'Transportation and Logistics': 'Transporte e logística', 'Healthcare & pharma': 'Saúde e farmacêutico', 'Transport & logistics': 'Transporte e logística', 'Media & entertainment': 'Mídia e entretenimento', 'Food & beverages': 'Alimentos e bebidas', 'N/A': 'N/D', '\n| Measure | Definition |\n|---|---|\n| Revenue | Source value in USD millions; not profit |\n| Reported growth | The Revenue growth percentage supplied by the CSV |\n| Prior revenue · estimated | Current revenue ÷ (1 + reported growth / 100) |\n| Revenue change · estimated | Current revenue − reconstructed prior revenue |\n| Sector / selection growth · estimated | (Sum of current revenue ÷ sum of reconstructed prior revenue − 1) × 100 |\n| Revenue / employee shares | Company or sector total ÷ the chosen denominator × 100 |\n| Revenue per employee | Revenue × 1,000,000 ÷ employee count |\n': '\n| Indicador | Definição |\n|---|---|\n| Receita | Valor da fonte em milhões de USD; não é lucro |\n| Crescimento informado | Percentual de crescimento fornecido pelo CSV |\n| Receita anterior · estimada | Receita atual ÷ (1 + crescimento informado / 100) |\n| Variação da receita · estimada | Receita atual − receita anterior reconstruída |\n| Crescimento do setor / seleção · estimado | (Receita atual total ÷ receita anterior reconstruída total − 1) × 100 |\n| Participação na receita / funcionários | Total da empresa ou setor ÷ base escolhida × 100 |\n| Receita por funcionário | Receita × 1.000.000 ÷ quantidade de funcionários |\n'}
_PATTERN = re.compile("|".join(re.escape(k) for k in sorted(_PT, key=len, reverse=True)))
def t(value):
    if language != "Português" or not isinstance(value, str):
        return value
    return _PATTERN.sub(lambda match: _PT[match.group(0)], value)

TEAL, BLUE, RED, TEXT = ('#53ddbd', '#76a9ff', '#ff7e91', '#e7edf5')
PALETTE = [TEAL, BLUE, '#ae9cfa', '#f5c577', '#fd9fa8', '#6ed2f4', '#b6d67c', '#e7b3ed', '#f5a26c', '#9bc4ce', '#cad7f2', '#d0bc8d', '#929ff0']
st.markdown(t('<style>\n.stApp {background: #0b1120;}\n.block-container {padding-top: 4.5rem; padding-bottom: 2rem; max-width: 1580px;}\n[data-testid="stSidebar"] {background: #101a2c; border-right: 1px solid #243149;}\n[data-testid="stMetric"] {background: #121e32; border: 1px solid #283650;\n border-radius: 12px; padding: 18px 18px 15px; min-height: 125px;}\n[data-testid="stMetricLabel"] {color: #a9b9ce;}\n[data-testid="stMetricValue"] {font-size: clamp(1.3rem, 2.1vw, 2.1rem); color: #f1f5fa;}\nh1 {font-weight: 760; letter-spacing: -1.6px; font-size: 2.9rem;}\nh3 {font-size: 1.18rem; letter-spacing: -.3px;}\n.eyebrow {color: #53ddbd; font-size: .76rem; letter-spacing: .19em; font-weight: 700;}\n.subtitle {color: #aab9cf; margin: -.3rem 0 1.4rem; font-size: 1.02rem;}\n.rule {border-top: 1px solid #283650; margin: 1.6rem 0;}\nbutton[role="tab"] {font-size: 1rem;}\n@media (max-width: 700px) {.block-container {padding: 4.5rem 1rem 1.5rem;} h1 {font-size: 2rem;}}\n</style>'), unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def parse(content):
    return load_data(content)

def money(millions, signed=False):
    if not math.isfinite(millions):
        return 'N/A'
    prefix = '+' if signed and millions > 0 else '−' if millions < 0 else ''
    n = abs(millions)
    if n >= 1000000:
        return f'{prefix}${n / 1000000:,.2f}T'
    if n >= 1000:
        return f'{prefix}${n / 1000:,.2f}B'
    return f'{prefix}${n:,.1f}M'

def rate(value):
    return f'{value:+.1f}%' if math.isfinite(value) else 'N/A'

def polish(fig, height=440):
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=height, margin=dict(l=4, r=24, t=15, b=12), font=dict(color=TEXT, size=12), colorway=PALETTE, legend_title_text='', hoverlabel=dict(bgcolor='#1c2d46', font_size=13), xaxis=dict(gridcolor='#243149', zerolinecolor='#53647d'), yaxis=dict(gridcolor='#243149', zerolinecolor='#53647d'))
    return fig

def show(fig, key):
    if language == "Português":
        fig.update_layout(separators=",.")
        fig.for_each_xaxis(lambda axis: axis.update(title_text=t(axis.title.text)))
        fig.for_each_yaxis(lambda axis: axis.update(title_text=t(axis.title.text), ticktext=[t(v) for v in axis.ticktext] if axis.ticktext is not None else None, tickvals=[t(v) for v in axis.tickvals] if axis.tickvals is not None else None))
        for trace in fig.data:
            trace.name = t(trace.name)
            if trace.type == "bar" and trace.y is not None:
                trace.y = [t(v) for v in trace.y]
            if trace.hovertemplate:
                trace.hovertemplate = t(trace.hovertemplate)
            if trace.customdata is not None:
                trace.customdata = [[t(v) if isinstance(v, str) else v for v in row] for row in trace.customdata]
    st.plotly_chart(fig, width='stretch', key=key, config={'displaylogo': False, 'modeBarButtonsToRemove': ['lasso2d', 'select2d']})

def bars(frame, metric, labels, key, color=TEAL, diverging=False, suffix='', limit=None):
    data = frame.sort_values(metric, ascending=False)
    if limit:
        data = data.head(limit)
    fig = go.Figure(go.Bar(x=data[metric], y=data[labels], orientation='h', marker_color=[RED if v < 0 else color for v in data[metric]] if diverging else color, text=[f'{v:,.1f}{suffix}' if suffix or abs(v) < 100 else f'{v:,.0f}' for v in data[metric]], textposition='auto', cliponaxis=False, hovertemplate='%{y}<br>%{x:,.2f}' + suffix + '<extra></extra>'))
    fig.update_yaxes(autorange='reversed', title=None, automargin=True)
    if labels == GROUP:
        short = {'Healthcare and Pharmaceuticals': 'Healthcare & pharma', 'Transportation and Logistics': 'Transport & logistics', 'Media and Entertainment': 'Media & entertainment', 'Food and Beverages': 'Food & beverages'}
        fig.update_yaxes(tickmode='array', tickvals=data[labels], ticktext=[short.get(v, v) for v in data[labels]])
    fig.update_xaxes(title=metric, ticksuffix=suffix)
    show(polish(fig, max(340, min(760, len(data) * 32 + 75))), key)

def table(frame, key):
    config = {REVENUE: st.column_config.NumberColumn(t('Revenue · USD M'), format='localized'), GROWTH: st.column_config.NumberColumn(t('Revenue growth · %'), format='%.1f'), PRIOR: st.column_config.NumberColumn(t('Prior revenue · est. USD M'), format='%.1f'), CHANGE: st.column_config.NumberColumn(t('Revenue change · est. USD M'), format='%.1f'), RPE: st.column_config.NumberColumn(t('Revenue / employee · USD'), format='$%.0f'), 'Revenue share (%)': st.column_config.NumberColumn(t('Revenue share · %'), format='%.2f'), 'Employee share (%)': st.column_config.NumberColumn(t('Employee share · %'), format='%.2f'), 'Company share (%)': st.column_config.NumberColumn(t('Company share · %'), format='%.2f'), 'Employees': st.column_config.NumberColumn(t('Employees'), format='localized')}
    frame = frame.copy()
    if GROUP in frame:
        frame[GROUP] = frame[GROUP].map(t)
    for column in frame.columns:
        if column not in config:
            config[column] = st.column_config.Column(t(column))
    st.dataframe(frame, column_config=config, hide_index=True, width='stretch', key=key)
with st.sidebar:
    st.markdown(t('### ◈ Company Atlas'))
    st.caption(t('A clear view of company scale and growth.'))
    uploaded = st.file_uploader(t('Replace snapshot (optional)'), type=['csv'], help=t('Use the same English headers and numeric formats as the bundled CSV.'))
try:
    content = uploaded.getvalue() if uploaded is not None else (ROOT / 'data' / 'companies.csv').read_bytes()
    df = parse(content)
except (ValueError, OSError) as exc:
    st.error(t(str(exc)))
    st.stop()
groups = sorted(df[GROUP].unique())
colors = {g: PALETTE[i % len(PALETTE)] for i, g in enumerate(groups)}
with st.sidebar:
    with st.form('filters'):
        st.markdown(t('#### Refine the view'))
        sectors = st.multiselect(t('Industry groups'), groups, default=groups, key='sectors', format_func=t)
        query = st.text_input(t('Find a company'), placeholder=t('Name contains…'), key='query')
        direction = st.selectbox(t('Revenue direction'), ['All companies', 'Growing revenue', 'Declining revenue', 'Unchanged revenue'], key='direction', format_func=t)
        st.form_submit_button(t('Apply filters'), width='stretch')
    st.divider()
    basis = st.radio(t('Share denominator'), ['Current selection', 'Full dataset'], key='share_basis', help=t('Defines the denominator of every revenue, employee and company share.'), format_func=t)
    unit = st.selectbox(t('Chart revenue unit'), ['USD billions', 'USD millions'], key='revenue_unit', format_func=t)
    top_n = st.slider(t('Companies in rankings'), 5, 30, 10, step=5, key='top_n')
    st.caption(t('Filters affect all views. Top N only limits company charts; totals and percentage denominators use all selected companies.'))
    st.caption(t('Source: bundled CSV snapshot. Reporting dates are not provided. No live feed or API required.'))
selected = filter_data(df, sectors, query, direction)
st.markdown(t('<div class="eyebrow">BUSINESS INTELLIGENCE / COMPANY SNAPSHOT</div>'), unsafe_allow_html=True)
st.title(t('Company Atlas'))
st.markdown(t('<div class="subtitle">See the scale. Compare the pace. Understand the people behind the numbers.</div>'), unsafe_allow_html=True)
st.caption(t(f'{len(selected):,} of {len(df):,} companies selected · {selected[GROUP].nunique()} of {len(groups)} industry groups · All values in USD · Interface in English'))
if selected.empty:
    st.info(t('No companies match these filters. Select an industry group or broaden the company search and apply filters.'))
    st.stop()
overall, current = (totals(df), totals(selected))
denom = current if basis == 'Current selection' else overall
companies = add_shares(selected, denom)
sectors_df = sector_summary(selected, denom)
divisor = 1000 if unit == 'USD billions' else 1
unit_short = 'USD B' if divisor == 1000 else 'USD M'
rev_label, delta_label = (f'Revenue ({unit_short})', f'Revenue change · estimated ({unit_short})')
companies[rev_label], companies[delta_label] = (companies[REVENUE] / divisor, companies[CHANGE] / divisor)
sectors_df[rev_label], sectors_df[delta_label] = (sectors_df[REVENUE] / divisor, sectors_df[CHANGE] / divisor)
c1, c2, c3, c4 = st.columns(4)
c1.metric(t('Total revenue'), money(current['revenue']), help=t('Revenue is sales/income reported by the source, not profit. Source monetary values are USD millions.'))
c2.metric(t('Total employees'), f"{current['employees']:,}", help=t('Sum of the selected headcounts. This is a snapshot, not jobs created.'))
c3.metric(t('Companies'), f"{current['companies']:,}", help=t('All selected rows are included in totals, regardless of Top N.'))
c4.metric(t('Est. aggregate growth'), rate(current['growth']), help=t('Calculated from total current revenue and reconstructed prior revenue; not an average of company growth rates.'))
st.caption(t(f"Share basis: {basis.lower()} — {denom['companies']:,} companies, {money(denom['revenue'])} revenue, {denom['employees']:,} employees. Growth and dollar changes use reported rates; reconstructed amounts are approximate."))
overview, growth, workforce, explorer, method = st.tabs([t('Overview'), t('Growth & scale'), t('Workforce'), t('Company explorer'), t('Data & methodology')])
with overview:
    st.markdown(t('### The sector landscape'))
    st.caption(t('Sector totals include only companies in this snapshot and your active selection.'))
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown(t('#### Revenue by industry group'))
        bars(sectors_df, rev_label, GROUP, 'sector_revenue')
    with right:
        st.markdown(t('#### Where the workforce is concentrated'))
        bars(sectors_df, 'Employee share (%)', GROUP, 'sector_employee_share', color=BLUE, suffix='%')
    a, b, c = st.columns(3)
    leader = selected.loc[selected[REVENUE].idxmax()]
    fastest = selected.loc[selected[GROWTH].idxmax()]
    employer = selected.loc[selected['Employees'].idxmax()]
    a.info(t(f"**Revenue leader**\n\n{leader['Name']} · {money(leader[REVENUE])}"))
    b.info(t(f"**Fastest reported revenue growth**\n\n{fastest['Name']} · {rate(fastest[GROWTH])}"))
    c.info(t(f"**Largest employer**\n\n{employer['Name']} · {employer['Employees']:,} employees"))
    st.markdown(t('#### Sector scorecard'))
    table(sectors_df[[GROUP, 'Companies', REVENUE, 'Revenue share (%)', GROWTH, CHANGE, 'Employees', 'Employee share (%)']].sort_values(REVENUE, ascending=False), 'sector_scorecard')
with growth:
    st.markdown(t('### Percentage growth and dollar impact answer different questions'))
    st.caption(t('Percentages show pace; estimated dollar change shows financial scale. These are reported comparisons, not a historical time series.'))
    left, right = st.columns(2)
    with left:
        st.markdown(t('#### Aggregate growth by sector · estimated'))
        bars(sectors_df, GROWTH, GROUP, 'sector_growth', diverging=True, suffix='%')
    with right:
        st.markdown(t('#### Revenue change by sector · estimated'))
        bars(sectors_df, delta_label, GROUP, 'sector_change', diverging=True)
    st.markdown(t('#### Which companies combine pace and financial impact?'))
    scatter = px.scatter(companies, x=GROWTH, y=delta_label, size=REVENUE, color=GROUP, color_discrete_map=colors, hover_name='Name', hover_data={GROUP: True, REVENUE: ':,.0f', 'Employees': ':,', GROWTH: ':.1f', delta_label: ':,.2f'}, size_max=52, labels={GROWTH: 'Reported revenue growth (%)'})
    scatter.add_hline(y=0, line_color='#53647d', line_width=1)
    scatter.add_vline(x=0, line_color='#53647d', line_width=1)
    scatter.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2))
    show(polish(scatter, 590), 'growth_scatter')
    st.caption(t('Each bubble is a company. Bubble area represents current revenue. The vertical axis is reconstructed dollar change.'))
    metric = st.radio(t('Company ranking'), ['Reported growth (%)', 'Estimated revenue change'], horizontal=True, key='rank_metric', format_func=t)
    ranking_metric = GROWTH if metric == 'Reported growth (%)' else delta_label
    left, right = st.columns(2)
    with left:
        st.markdown(t(f'#### Top {min(top_n, len(companies))} · highest values'))
        bars(companies, ranking_metric, 'Name', 'company_growth_top', diverging=True, suffix='%' if ranking_metric == GROWTH else '', limit=top_n)
    with right:
        st.markdown(t(f'#### Bottom {min(top_n, len(companies))} · lowest values'))
        bottom = companies.nsmallest(top_n, ranking_metric)
        bars(bottom, ranking_metric, 'Name', 'company_growth_bottom', diverging=True, suffix='%' if ranking_metric == GROWTH else '')
with workforce:
    st.markdown(t('### Headcount, concentration and revenue per employee'))
    left, right = st.columns(2)
    with left:
        st.markdown(t('#### Employees by sector · absolute'))
        bars(sectors_df, 'Employees', GROUP, 'employees_sector', color=BLUE)
    with right:
        st.markdown(t('#### Employee share by company'))
        bars(companies, 'Employee share (%)', 'Name', 'employees_company_share', color=BLUE, suffix='%', limit=top_n)
    st.markdown(t('#### Largest employers'))
    workforce_cols = ['Name', GROUP, 'Employees', 'Employee share (%)', REVENUE, RPE]
    table(companies[workforce_cols].sort_values('Employees', ascending=False), 'workforce_table')
    with st.expander(t('How should I interpret revenue per employee?')):
        st.write(t('Revenue per employee = revenue in USD ÷ reported employees. It is a descriptive ratio, not profit per employee or a direct measure of worker productivity. Business models, outsourcing, fiscal periods and headcount definitions can differ. There is no prior employee count, so employee growth cannot be calculated.'))
with explorer:
    st.markdown(t('### Explore a company'))
    name = st.selectbox(t('Company'), sorted(companies['Name'].tolist()), key='company', format_func=t)
    row = companies.loc[companies['Name'].eq(name)].iloc[0]
    st.markdown(t(f'#### {name}'))
    st.caption(t(f"{row[GROUP]} · Original industry: {row['Industry']} · Headquarters: {row['Headquarters']} · Source rank: {row['Rank']}"))
    a, b, c = st.columns(3)
    a.metric(t('Revenue'), money(row[REVENUE]))
    b.metric(t('Reported revenue growth'), rate(row[GROWTH]))
    c.metric(t('Revenue change · estimated'), money(row[CHANGE], signed=True))
    a, b, c = st.columns(3)
    a.metric(t('Employees'), f"{row['Employees']:,}")
    b.metric(t('Revenue share'), f"{row['Revenue share (%)']:.2f}%")
    c.metric(t('Employee share'), f"{row['Employee share (%)']:.2f}%")
    st.caption(t(f'Percentage denominator: {basis.lower()}. No employee growth is available.'))
    st.markdown(t('#### All selected companies'))
    table(companies[['Rank', 'Name', GROUP, REVENUE, GROWTH, CHANGE, 'Employees', 'Revenue share (%)', 'Employee share (%)', RPE]].sort_values(REVENUE, ascending=False), 'company_table')
with method:
    st.markdown(t('### Transparent calculations, reusable data'))
    st.write(t('This app reads a bundled CSV snapshot. It makes no external data or AI calls. The dataset contains company revenue, reported revenue growth, employee headcount and a curated industry group. Original source columns are preserved in the bundled CSV.'))
    st.markdown(t('\n| Measure | Definition |\n|---|---|\n| Revenue | Source value in USD millions; not profit |\n| Reported growth | The Revenue growth percentage supplied by the CSV |\n| Prior revenue · estimated | Current revenue ÷ (1 + reported growth / 100) |\n| Revenue change · estimated | Current revenue − reconstructed prior revenue |\n| Sector / selection growth · estimated | (Sum of current revenue ÷ sum of reconstructed prior revenue − 1) × 100 |\n| Revenue / employee shares | Company or sector total ÷ the chosen denominator × 100 |\n| Revenue per employee | Revenue × 1,000,000 ÷ employee count |\n'))
    st.warning(t('The file does not identify fiscal dates or the original source URL. Growth rates are rounded, so prior revenue and dollar changes are estimates. Aggregated growth assumes each supplied rate describes a comparable prior period; it is not a verified calendar-year sector statistic. No multi-year trend can be inferred.'))
    st.write(t('Industry groups are broad, curated categories. A company belongs to one group, even when it operates across several industries. Sector results describe only the companies included here, not the entire market. Reported revenues can include transactions between companies; their sum is not GDP, market value or profit.'))
    st.write(t('Original ranks are retained as supplied. All visual revenue rankings sort by the actual revenue column; source ranks may not follow that order exactly.'))
    downloads = companies.drop(columns=[rev_label, delta_label])
    a, b = st.columns(2)
    a.download_button(t('Download selected companies · CSV'), downloads.to_csv(index=False).encode('utf-8-sig'), 'selected_companies.csv', 'text/csv', width='stretch')
    b.download_button(t('Download sector summary · CSV'), sectors_df.drop(columns=[rev_label, delta_label]).to_csv(index=False).encode('utf-8-sig'), 'sector_summary.csv', 'text/csv', width='stretch')
    st.caption(t(f"Both downloads use the current filters and the '{basis.lower()}' share denominator. Monetary column headers specify USD millions. Growth/share columns store percentage points (6.0 means 6%)."))
    st.markdown(t('#### Original snapshot'))
    st.download_button(t('Download original data · CSV'), content, 'companies.csv', 'text/csv')
st.markdown(t('<div class="rule"></div>'), unsafe_allow_html=True)
st.caption(t('COMPANY ATLAS · Static source, interactive perspective · Estimates are labelled throughout.'))
