import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output
from dash.dependencies import State

# Load data
df = pd.read_csv("cleaned_jobs.csv")
df_complete = df[df['avg_salary'].notna() & df['years_exp'].notna()]

# Prepare exploded columns for filters
df_locations = df['clean_location'].dropna().str.split(',').explode().str.strip()
df_skills = df['clean_skills'].dropna().str.split(',').explode().str.strip()


roles = df['role'].dropna().unique()
locations = df_locations.unique()
skills = df_skills.unique()

# Initialize Dash app with dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "AI Job Market Analyzer"
server = app.server

# Layout
app.layout = dbc.Container([
    html.H1("AI Job Market Analyzer", className='text-center my-4'),
# Toggle show_salary_only
html.Div([
    dcc.Checklist(
        id='salary-toggle',
        options=[{'label': ' Show only jobs with salary info', 'value': 'with_salary'}],
        value=[],  # default = unchecked
        inputStyle={'margin-right': '10px'},
        style={'color': 'white', 'fontSize': '16px'}
    )
], style={'textAlign': 'center', 'marginBottom': '20px'}),


    # Insights box at the top
    html.Div(id='insights-box', style={
        'backgroundColor': '#222222', 'color': 'white', 'padding': '15px', 'borderRadius': '8px',
        'marginBottom': '20px', 'fontSize': '18px', 'textAlign': 'center'
    }),

    # Filters Row
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='role-filter',
                options=[{'label': r, 'value': r} for r in sorted(roles)],
                placeholder="Select Role",
                multi=True,
                clearable=True,
                style={'color': 'white', 'backgroundColor': '#121212'},
            )
        ], width=4),

        dbc.Col([
            dcc.Dropdown(
                id='location-filter',
                options=[{'label': loc, 'value': loc} for loc in sorted(locations)],
                placeholder="Select Location",
                multi=True,
                clearable=True,
                style={'color': 'white', 'backgroundColor': '#121212'},
            )
        ], width=4),

        dbc.Col([
            dcc.Dropdown(
                id='skills-filter',
                options=[{'label': skill, 'value': skill} for skill in sorted(skills)],
                placeholder="Select Skills",
                multi=True,
                clearable=True,
                style={'color': 'white', 'backgroundColor': '#121212'},
            )
        ], width=4),
    ], className="mb-4"),
# Insights & Predictions Card (put this in app.layout, after Filters Row, before Graphs)
dbc.Row([
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H4("Future Insights & 2025 Job Market Trends", className="card-title"),
        html.Ul([
            html.Li("AI/ML roles expected to grow by 20-30% in 2025"),
            html.Li("High demand for skills in Generative AI, LLM fine-tuning, and prompt engineering"),
            html.Li("Over 60% of AI jobs in startups are now hybrid or remote-first"),
            html.Li("Top hiring sectors: Fintech, Healthcare AI, EdTech, and Climate AI")
        ], style={"paddingLeft": "20px"})
    ]), color="dark", inverse=True), width=12)
], className="mb-4"),



    html.Div([
        html.Button("Download CSV", id="download-btn", n_clicks=0, className="btn btn-primary m-2"),
        dcc.Download(id="download-component"),

        html.Button("Download PDF", id="download-pdf-btn", n_clicks=0, className="btn btn-secondary m-2"),
        dcc.Download(id="pdf-download")
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Graphs Row 1: Salary and Experience histograms
dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='salary-histogram')),
                 className="mb-4 shadow-sm rounded"),
        md=6, xs=12
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='experience-histogram')),
                 className="mb-4 shadow-sm rounded"),
        md=6, xs=12
    ),
], className="mb-4"),



    # Graph Row 2: Location bar chart
dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='location-bar')),
                 className="mb-4 shadow-sm rounded"),
        width=12
    )
], className="mb-4"),


    # Graph Row 3: Skills bar chart
dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='skills-bar')),
                 className="mb-4 shadow-sm rounded"),
        width=12
    )
], className="mb-4"),



# Graph Row 4: Top Companies and Heatmap
dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='companies-bar')),
                 className="mb-4 shadow-sm rounded"),
        md=6, xs=12
    ),
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='heatmap-role-exp')),
                 className="mb-4 shadow-sm rounded"),
        md=6, xs=12
    ),
], className="mb-4"),

dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='trend-line')),
                 className="mb-4 shadow-sm rounded"),
        width=12
    )
], className="mb-4"),

dbc.Row([
    dbc.Col(
        dbc.Card(dbc.CardBody(dcc.Graph(id='exp-vs-salary-scatter')),
                 className="mb-4 shadow-sm rounded"),
        width=12
    )
], className="mb-4"),



], fluid=True, style={'backgroundColor': '#121212', 'color': 'white', 'minHeight': '100vh'})



@app.callback(
    Output('salary-histogram', 'figure'),
    Output('experience-histogram', 'figure'),
    Output('location-bar', 'figure'),
    Output('skills-bar', 'figure'),
    Output('companies-bar', 'figure'),  # NEW
    Output('heatmap-role-exp', 'figure'),
    Output('trend-line', 'figure'),
    Output('insights-box', 'children'),
    Output('exp-vs-salary-scatter', 'figure'),
    Input('role-filter', 'value'),
    Input('location-filter', 'value'),
    Input('skills-filter', 'value'),
    Input('salary-toggle', 'value'),
)
def update_graphs(selected_roles, selected_locations, selected_skills, salary_toggle):
    if 'with_salary' in salary_toggle:
        # Strict mode → only rows with salary + exp
        filtered_df = df[df['avg_salary'].notna() & df['years_exp'].notna()].copy()
    else:
        # Allow missing salary → only require experience
        filtered_df = df[df['years_exp'].notna()].copy()

    # Filter by roles
    if selected_roles:
        filtered_df = filtered_df[filtered_df['role'].isin(selected_roles)]

    # Filter by locations - explode and strip, drop empty strings
    if selected_locations:
        filtered_df['clean_location'] = filtered_df['clean_location'].fillna('').astype(str)
        exploded_loc = filtered_df.assign(clean_location=filtered_df['clean_location'].str.split(',')).explode(
            'clean_location')
        exploded_loc['clean_location'] = exploded_loc['clean_location'].str.strip()
        exploded_loc = exploded_loc[exploded_loc['clean_location'] != '']
        filtered_df = exploded_loc[exploded_loc['clean_location'].isin(selected_locations)].reset_index(drop=True)

    # Filter by skills - explode and strip, drop empty strings
    if selected_skills:
        filtered_df['clean_skills'] = filtered_df['clean_skills'].fillna('').astype(str)
        exploded_skills = filtered_df.assign(clean_skills=filtered_df['clean_skills'].str.split(',')).explode(
            'clean_skills')
        exploded_skills['clean_skills'] = exploded_skills['clean_skills'].str.strip()
        exploded_skills = exploded_skills[exploded_skills['clean_skills'] != '']  # drop empty strings
        filtered_df = exploded_skills[exploded_skills['clean_skills'].isin(selected_skills)].reset_index(drop=True)


    # Check if filtered dataframe is empty
    if filtered_df.empty:
        no_data_fig = px.histogram(title="No data available for selected filters")
        no_data_fig.update_layout(
            plot_bgcolor='#121212', paper_bgcolor='#121212', font=dict(color='white')
        )
        insight_text = "No job listings match your selected filters."
        # Return empty graphs and insight text
        return (
            no_data_fig, no_data_fig, no_data_fig, no_data_fig,
            no_data_fig, no_data_fig, insight_text, no_data_fig
        )

    # Color sequences for multi-color attractive plots
    salary_colors = px.colors.sequential.Plasma
    exp_colors = px.colors.sequential.Viridis
    loc_colors = px.colors.qualitative.Bold
    skill_colors = px.colors.qualitative.Set3

    # Salary histogram
    # Salary histogram
    salary_df = filtered_df[filtered_df['avg_salary'].notna()].copy()
    salary_df['avg_salary_lpa'] = salary_df['avg_salary'] / 100000  # Convert to LPA

    salary_fig = px.histogram(
        salary_df,
        x='avg_salary_lpa',
        nbins=20,
        title='Salary Distribution (in LPA)',
        color_discrete_sequence=salary_colors,
        hover_data={'avg_salary': True},
    )

    salary_fig.update_traces(
        hovertemplate="₹%{x:.1f} LPA"
    )

    salary_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis_title='Average Salary (LPA)',
        yaxis_title='Job Count',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        bargap=0.1,
    )

    # Experience histogram
    exp_fig = px.histogram(
        filtered_df, x='years_exp', nbins=10, title='Experience Distribution',
        color_discrete_sequence=exp_colors
    )
    exp_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        bargap=0.1,
    )

    # Location bar chart - top 10
    loc_counts = filtered_df['clean_location'].dropna().str.split(',').explode().str.strip().value_counts().head(
        10).reset_index()
    loc_counts.columns = ['Location', 'Count']
    loc_fig = px.bar(
        loc_counts, x='Location', y='Count', title='Top 10 Locations',
        color='Location',
        color_discrete_sequence=loc_colors
    )
    loc_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )

    # Skills bar chart - top 10
    skill_counts = filtered_df['clean_skills'].dropna().str.split(',').explode().str.strip().value_counts().head(
        10).reset_index()

    skill_counts.columns = ['Skill', 'Count']
    skills_fig = px.bar(
        skill_counts, x='Skill', y='Count', title='Top 10 Skills',
        color='Skill',
        color_discrete_sequence=skill_colors
    )
    skills_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )
    # Top Companies bar chart - top 10
    company_counts = filtered_df['company'].dropna().value_counts().head(10).reset_index()
    company_counts.columns = ['Company', 'Count']
    companies_fig = px.bar(
        company_counts, x='Company', y='Count', title='Top 10 Hiring Companies',
        color='Company',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    companies_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=False,
    )

    # Role vs Experience Heatmap
    heatmap_df = filtered_df.copy()
    heatmap_df['exp_bucket'] = pd.cut(
        heatmap_df['years_exp'],
        bins=[0, 2, 5, 8, 100],
        labels=['0-2', '2-5', '5-8', '8+']
    )

    heatmap_pivot = heatmap_df.pivot_table(
        index='role',
        columns='exp_bucket',
        values='avg_salary',

        aggfunc='mean',
        observed = False
    ).fillna(0)

    heatmap_fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Experience Bucket (years)", y="Role", color="Avg Salary"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Role vs Experience Heatmap (Avg Salary)"
    )
    heatmap_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white')
    )
    scatter_fig = px.scatter(
        filtered_df[filtered_df['avg_salary'].notna()],
        x='years_exp', y='avg_salary',
        color='role',
        title='Experience vs Salary Scatter Plot',
        size_max=15,
        opacity=0.7,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    scatter_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis=dict(title='Years of Experience', showgrid=False),
        yaxis=dict(title='Average Salary', showgrid=False),
        showlegend=True
    )
    # Trend Over Time Line Chart
    # Clean date column
    filtered_df['posted_date_cleaned'] = pd.to_datetime(filtered_df['posted_date_cleaned'], errors='coerce')

    trend_df = filtered_df.dropna(subset=['posted_date_cleaned']).copy()
    trend_df['week'] = trend_df['posted_date_cleaned'].dt.to_period('W').dt.start_time

    # Group by week and role
    trend_grouped = trend_df.groupby(['week', 'role']).size().reset_index(name='Job Count')

    trend_fig = px.line(
        trend_grouped,
        x='week',
        y='Job Count',
        color='role',
        markers=True,
        title="Job Postings Trend by Role (Weekly)",
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data = {'role': True, 'Job Count': True}

    )

    trend_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
        xaxis_title="Week",
        yaxis_title="Number of Jobs",
        legend_title="Role",

    )

    # Insights & Predictions Card


    # Generate simple insights text
    avg_salary = filtered_df['avg_salary'].mean()
    avg_exp = filtered_df['years_exp'].mean()
    total_jobs = len(filtered_df)
    top_role = filtered_df['role'].mode().iloc[0] if not filtered_df['role'].mode().empty else "N/A"

    insight_text = (
        f"Filtered Jobs: {total_jobs} | "
        f"Average Salary: ₹{avg_salary / 100000:.1f} LPA | "

        f"Average Experience Required: {avg_exp:.1f} years | "
        f"Most Common Role: {top_role}"
    )

    return salary_fig, exp_fig, loc_fig, skills_fig, companies_fig, heatmap_fig,trend_fig, insight_text, scatter_fig


import io
from xhtml2pdf import pisa
import base64

@app.callback(
    Output("pdf-download", "data"),
    Input("download-pdf-btn", "n_clicks"),
    State('role-filter', 'value'),
    State('location-filter', 'value'),
    State('skills-filter', 'value'),
    State('salary-toggle', 'value'),
    prevent_initial_call=True
)
def download_pdf(n_clicks, selected_roles, selected_locations, selected_skills, salary_toggle):
    if 'with_salary' in salary_toggle:
        filtered_df = df[df['avg_salary'].notna() & df['years_exp'].notna()].copy()
    else:
        filtered_df = df[df['years_exp'].notna()].copy()

    if selected_roles:
        filtered_df = filtered_df[filtered_df['role'].isin(selected_roles)]

    if selected_locations:
        filtered_df['clean_location'] = filtered_df['clean_location'].fillna('').astype(str)
        exploded_loc = filtered_df.assign(clean_location=filtered_df['clean_location'].str.split(',')).explode('clean_location')
        exploded_loc['clean_location'] = exploded_loc['clean_location'].str.strip()
        filtered_df = exploded_loc[exploded_loc['clean_location'].isin(selected_locations)].reset_index(drop=True)

    if selected_skills:
        filtered_df['clean_skills'] = filtered_df['clean_skills'].fillna('').astype(str)
        exploded_skills = filtered_df.assign(clean_skills=filtered_df['clean_skills'].str.split(',')).explode('clean_skills')
        exploded_skills['clean_skills'] = exploded_skills['clean_skills'].str.strip()
        filtered_df = exploded_skills[exploded_skills['clean_skills'].isin(selected_skills)].reset_index(drop=True)

    # Build a simple HTML report
    html_content = f"""
    <h2>AI Job Market Filtered Report</h2>
    <p>Total Records: {len(filtered_df)}</p>
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>{"".join(f"<th>{col}</th>" for col in filtered_df.columns[:6])}</tr>
        {''.join(f"<tr>{''.join(f'<td>{val}</td>' for val in row[:6])}</tr>" for row in filtered_df.values[:20])}
    </table>
    """

    # Convert HTML to PDF
    pdf_stream = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html_content), dest=pdf_stream)
    pdf_stream.seek(0)
    pdf_base64 = base64.b64encode(pdf_stream.read()).decode("utf-8")

    return {
        "content": pdf_base64,
        "filename": "ai_job_market_filtered_report.pdf",
        "base64": True
    }


@app.callback(
    Output("download-component", "data"),
    Input("download-btn", "n_clicks"),
    State('role-filter', 'value'),
    State('location-filter', 'value'),
    State('skills-filter', 'value'),
    State('salary-toggle', 'value'),
    prevent_initial_call=True
)
def download_filtered_data(n_clicks, selected_roles, selected_locations, selected_skills, salary_toggle):
    if 'with_salary' in salary_toggle:
        filtered_df = df[df['avg_salary'].notna() & df['years_exp'].notna()].copy()
    else:
        filtered_df = df[df['years_exp'].notna()].copy()

    if selected_roles:
        filtered_df = filtered_df[filtered_df['role'].isin(selected_roles)]

    if selected_locations:
        filtered_df['clean_location'] = filtered_df['clean_location'].fillna('').astype(str)
        exploded_loc = filtered_df.assign(clean_location=filtered_df['clean_location'].str.split(',')).explode('clean_location')
        exploded_loc['clean_location'] = exploded_loc['clean_location'].str.strip()
        filtered_df = exploded_loc[exploded_loc['clean_location'].isin(selected_locations)].reset_index(drop=True)

    if selected_skills:
        filtered_df['clean_skills'] = filtered_df['clean_skills'].fillna('').astype(str)
        exploded_skills = filtered_df.assign(clean_skills=filtered_df['clean_skills'].str.split(',')).explode('clean_skills')
        exploded_skills['clean_skills'] = exploded_skills['clean_skills'].str.strip()
        filtered_df = exploded_skills[exploded_skills['clean_skills'].isin(selected_skills)].reset_index(drop=True)

    return dcc.send_data_frame(filtered_df.to_csv, "ai_job_market_filtered_report.csv", index=False)

if __name__ == "__main__":
    app.run(debug=True)