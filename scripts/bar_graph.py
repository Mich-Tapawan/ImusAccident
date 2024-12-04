import pandas as pd
import plotly.graph_objects as go

def generate_bar_graph(FILE_PATH):
    df_2022 = pd.read_excel(FILE_PATH, sheet_name='OFFENSE 2022', header=2)
    df_2023 = pd.read_excel(FILE_PATH, sheet_name='OFFENSE 2023', header=2)
    df_2024 = pd.read_excel(FILE_PATH, sheet_name='OFFENSE 2024', header=2)

    df_2022['year'] = 2022
    df_2023['year'] = 2023
    df_2024['year'] = 2024

    df_combined = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

    # Filter out the "Grand Total" row
    df_combined = df_combined[df_combined['Offense Type'].str.lower() != 'grand total']

    # Clean and standardize the "Offense Type" column
    df_combined['Offense Type'] = df_combined['Offense Type'].str.strip().str.lower().str.title()

    # Create a mapping of offense type to simplified labels
    unique_offenses = df_combined['Offense Type'].unique()
    offense_mapping = {original: f"Offense {i+1}" for i, original in enumerate(unique_offenses)}

    # Replace offense types with simplified labels
    df_combined['Simplified Offense Type'] = df_combined['Offense Type'].map(offense_mapping)

    # Group by year and offense type, and sum the offense counts
    accidents_by_offense = df_combined.groupby(['year', 'Simplified Offense Type', 'Offense Type']).agg(
        accident_count=('Count of offense', 'sum')
    ).reset_index()

    # Create the bar graph using Plotly Graph Objects
    years = [2022, 2023, 2024]
    colors = ['#CCFF33', '#34A0A4', '#38B000']
    fig = go.Figure()

    # Add bars for each year
    for year, color in zip(years, colors):
        year_data = accidents_by_offense[accidents_by_offense['year'] == year]
        fig.add_trace(go.Bar(
            x=year_data['Simplified Offense Type'],
            y=year_data['accident_count'],
            name=str(year),
            marker_color=color,
            hovertext=year_data['Offense Type'],  # Add the original offense names as hover text
            hoverinfo='text+y+name',  # Customize hover info
        ))

    # Customize layout
    fig.update_layout(
        xaxis=dict(
            title='Offense Type',
            title_font=dict(size=14),
            tickmode='array',
            tickvals=list(offense_mapping.values()),
            ticktext=list(offense_mapping.values()),  # Display simplified labels
        ),
        yaxis=dict(title='Number of Accidents', title_font=dict(size=14)),
        barmode='group',
        plot_bgcolor='#0B2C40',
        paper_bgcolor='#001D3D',
        font=dict(color='white'),
        legend=dict(
            title="Years",
            font=dict(size=12)
        ),
        height=600
    )

    # Adjusts hover templates
    fig.update_traces(hovertemplate='%{hovertext}<br>Accidents: %{y}')

    # Converts the figure to HTML
    graph_html = fig.to_html(full_html=False)

    return graph_html
