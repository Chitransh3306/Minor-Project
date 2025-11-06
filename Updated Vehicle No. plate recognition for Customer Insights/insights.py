import plotly.express as px
from database.db_handler import fetch_state_counts, fetch_recommendations

def plot_state_charts():
    df = fetch_state_counts()
    if df.empty:
        return None, None
    pie = px.pie(df, names='state_name', values='count', title='Vehicles by State')
    bar = px.bar(df, x='state_name', y='count', title='Vehicle Counts by State', color='state_name')
    return pie, bar

def show_recommendations():
    df = fetch_state_counts()
    if df.empty:
        return None
    top_codes = df.head(3)['state_name'].tolist()
    recs = fetch_recommendations([c[:2].upper() for c in top_codes])
    return recs
