import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.db_handler import fetch_state_counts, fetch_recommendations

def plot_state_charts():
    """Generate modern interactive Plotly charts for vehicle state distribution."""
    df = fetch_state_counts()
    if df.empty:
        return None, None
    
    # Donut Chart
    pie = px.pie(
        df,
        names="state_name",
        values="count",
        title="<b>Vehicle Distribution by State</b>",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    pie.update_traces(textposition='inside', textinfo='percent+label')
    pie.update_layout(showlegend=True, margin=dict(t=40, b=20, l=20, r=20))

    # Bar Chart
    bar = px.bar(
        df,
        x="state_name",
        y="count",
        title="<b>Total Vehicle Visits by State</b>",
        color="count",
        color_continuous_scale="Viridis",
        labels={"state_name": "State", "count": "Vehicle Count"},
        text="count"
    )
    bar.update_traces(texttemplate='%{text}', textposition='outside')
    bar.update_layout(
        xaxis_title="State / Region",
        yaxis_title="Vehicles Logged",
        margin=dict(t=40, b=20, l=20, r=20)
    )
    
    return pie, bar

def show_recommendations():
    """Fetch item recommendations and demographics for top visiting states."""
    df = fetch_state_counts()
    if df.empty:
        return None
    
    # Use actual State_Code (e.g. 'RJ', 'MH', 'DL') instead of slicing names!
    top_codes = df.head(5)["state_code"].tolist()
    recs = fetch_recommendations(top_codes)
    return recs

def get_summary_metrics():
    """Get high-level summary metrics."""
    df = fetch_state_counts()
    if df.empty:
        return 0, 0, "None"
    total_vehicles = int(df["count"].sum())
    unique_states = len(df)
    top_state = df.iloc[0]["state_name"]
    return total_vehicles, unique_states, top_state
