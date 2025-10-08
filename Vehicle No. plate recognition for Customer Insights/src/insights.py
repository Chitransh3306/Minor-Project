import pandas as pd
import plotly.express as px
from database import Session, Vehicle_Record
from sqlalchemy import select, func

def aggregate_state_counts(limit=10):
    sess = Session()
    s = select([Vehicle_Record.c.state_name, func.count().label("cnt")]).group_by(Vehicle_Record.c.state_name).order_by(func.count().desc()).limit(limit)
    rows = sess.execute(s).fetchall()
    sess.close()
    df = pd.DataFrame(rows, columns=["state_name","count"])
    return df

def plot_state_pie(df):
    fig = px.pie(df, names='state_name', values='count', title='Vehicles by State')
    return fig

def plot_state_bar(df):
    fig = px.bar(df, x='state_name', y='count', title='Vehicle Counts by State')
    return fig