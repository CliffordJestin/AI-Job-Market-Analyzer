import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

# Load data
df = pd.read_csv("final_cleaned_jobs.csv")
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
        value=['with_salary'],  # default = checked
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

    # Graphs Row 1: Salary and Experience histograms
    dbc.Row([
        dbc.Col(dcc.Graph(id='salary-histogram'), width=6),
        dbc.Col(dcc.Graph(id='experience-histogram'), width=6),
    ]),

    # Graph Row 2: Location bar chart
    dbc.Row([
        dbc.Col(dcc.Graph(id='location-bar'), width=12)
    ]),

    # Graph Row 3: Skills bar chart
    dbc.Row([
        dbc.Col(dcc.Graph(id='skills-bar'), width=12)
    ]),


# Graph Row 4: Top Companies and Heatmap
    dbc.Row([
        dbc.Col(dcc.Graph(id='companies-bar'), width=6),
        dbc.Col(dcc.Graph(id='heatmap-role-exp'), width=6),
    ]),

], fluid=True, style={'backgroundColor': '#121212', 'color': 'white', 'minHeight': '100vh'})



@app.callback(
    Output('salary-histogram', 'figure'),
    Output('experience-histogram', 'figure'),
    Output('location-bar', 'figure'),
    Output('skills-bar', 'figure'),
    Output('companies-bar', 'figure'),  # NEW
    Output('heatmap-role-exp', 'figure'),
    Output('insights-box', 'children'),
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
        return no_data_fig, no_data_fig, no_data_fig, no_data_fig, insight_text

    # Color sequences for multi-color attractive plots
    salary_colors = px.colors.sequential.Plasma
    exp_colors = px.colors.sequential.Viridis
    loc_colors = px.colors.qualitative.Bold
    skill_colors = px.colors.qualitative.Set3

    # Salary histogram
    salary_fig = px.histogram(
        filtered_df, x='avg_salary', nbins=20, title='Salary Distribution',
        color_discrete_sequence=salary_colors
    )
    salary_fig.update_layout(
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        font=dict(color='white'),
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

    # Generate simple insights text
    avg_salary = filtered_df['avg_salary'].mean()
    avg_exp = filtered_df['years_exp'].mean()
    total_jobs = len(filtered_df)
    top_role = filtered_df['role'].mode().iloc[0] if not filtered_df['role'].mode().empty else "N/A"

    insight_text = (
        f"Filtered Jobs: {total_jobs} | "
        f"Average Salary: ₹{avg_salary:,.0f} | "
        f"Average Experience Required: {avg_exp:.1f} years | "
        f"Most Common Role: {top_role}"
    )

    return salary_fig, exp_fig, loc_fig, skills_fig, companies_fig, heatmap_fig, insight_text


if __name__ == "__main__":
    app.run(debug=True)
