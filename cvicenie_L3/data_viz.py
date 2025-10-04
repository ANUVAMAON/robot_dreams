import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os

st.set_page_config(layout="wide")

# get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load data
data = pd.read_csv(os.path.join(current_dir, "data/defects.csv"))

# ========== SIDEBAR ==========
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")

# Sidebar - Dataset info
st.sidebar.subheader("Dataset Information")
st.sidebar.info(f"""
**Total Records:** {len(data)}  
**Days:** {data['Day'].nunique()}  
**Time Samples:** {data['Sample'].nunique()}  
**Defects Range:** {data['Defects'].min()} - {data['Defects'].max()}
""")

# Sidebar - Visualization options
st.sidebar.subheader("Visualization Options")
show_seaborn = st.sidebar.checkbox("Show Seaborn Heatmap", value=True)
show_plotly = st.sidebar.checkbox("Show Plotly Heatmap", value=True)
show_timeline = st.sidebar.checkbox("Show Animated Timeline", value=True)

# Sidebar - Filter options
st.sidebar.subheader("Filters")
selected_days = st.sidebar.multiselect(
    "Select Days to Display:",
    options=sorted(data['Day'].unique()),
    default=sorted(data['Day'].unique())
)

# Sidebar - Color scheme
color_scheme = st.sidebar.selectbox(
    "Color Scheme:",
    options=['YlGnBu', 'viridis', 'plasma', 'inferno', 'magma', 'Blues', 'Reds'],
    index=0
)

def aggregate_data(data):
    # create empty dataframe for aggregated data
    agg_data = pd.DataFrame()
    # create new column hour
    agg_data['Hour'] = data['Sample'].unique()
    # create aggregation for each day
    for day in data['Day'].unique():
        agg_data['defects_day_' + str(day)] = ""
        for hour in data['Sample'].unique():
            agg_data.loc[agg_data['Hour'] == hour, 'defects_day_' + str(day)] = data[(data['Day'] == day) & (data['Sample'] == hour)]['Defects'].values
    return agg_data

# ========== MAIN CONTENT ==========
st.title('🏭 Manufacturing Defects Dashboard')
st.write("Data Source: [Kaggle Manufacturing Defects Dataset](https://www.kaggle.com/datasets/gabrielsantello/manufacturing-defects-industry-dataset)")

# Filter data based on sidebar selection
if selected_days:
    filtered_data = data[data['Day'].isin(selected_days)]
else:
    filtered_data = data

agg_data = aggregate_data(filtered_data)

# Show visualizations based on sidebar checkboxes
if show_seaborn:
    st.subheader("📈 Seaborn Heatmap")
    fig, ax = plt.subplots(figsize=(16, 6))
    sns.heatmap(agg_data.iloc[:, 1:].astype(float).T, 
                cmap=color_scheme, 
                annot=True, 
                fmt=".1f", 
                xticklabels=agg_data['Hour'], 
                yticklabels=[f'Day {day}' for day in filtered_data['Day'].unique()], 
                ax=ax)
    ax.set_title('Manufacturing Defects Heatmap')
    ax.set_xlabel('Time (Hours)')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_ylabel('Days')
    plt.tight_layout()
    st.pyplot(fig)
    
if show_plotly:
    st.subheader("📊 Interactive Plotly Heatmap")
    fig = px.imshow(agg_data.iloc[:, 1:].astype(float).T, 
                    labels=dict(x="Time (Hours)", y="Days", color="Defects"),
                    x=agg_data['Hour'],
                    y=[f'Day {day}' for day in filtered_data['Day'].unique()],
                    color_continuous_scale=color_scheme,
                    text_auto=".1f")
    fig.update_layout(
        title='Manufacturing Defects Heatmap - Interactive',
        xaxis_title='Time (Hours)',
        yaxis_title='Days',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

if show_timeline:
    st.subheader("🎬 Animated Timeline - Defects Over Time")
    
    # Prepare data for animated timeline
    timeline_data = filtered_data.copy()
    
    # Create DateTime column for proper timeline
    timeline_data['DateTime'] = pd.to_datetime('2025-09-' + timeline_data['Day'].astype(str).str.zfill(2) + ' ' + timeline_data['Sample'])
    timeline_data['DayLabel'] = 'Day ' + timeline_data['Day'].astype(str)
    timeline_data['HourMinute'] = pd.to_datetime(timeline_data['Sample'], format='%H:%M').dt.hour + pd.to_datetime(timeline_data['Sample'], format='%H:%M').dt.minute / 60.0
    
    # Create animated scatter plot
    fig_timeline = px.scatter(
        timeline_data,
        x='HourMinute',
        y='Defects',
        animation_frame='Day',
        animation_group='Sample',
        size='Defects',
        color='Defects',
        hover_name='Sample',
        size_max=30,
        color_continuous_scale=color_scheme,
        range_y=[0, timeline_data['Defects'].max() + 2],
        labels={
            'HourMinute': 'Time of Day (Hours)',
            'Defects': 'Number of Defects',
            'Day': 'Day'
        },
        title='Manufacturing Defects Timeline Animation'
    )
    
    # Update layout for better animation
    fig_timeline.update_layout(
        height=600,
        xaxis_title='Time of Day (Hours)',
        yaxis_title='Number of Defects',
        showlegend=False,
        xaxis=dict(range=[8, 16.5]),  # Focus on working hours
    )
    
    # Customize animation settings
    fig_timeline.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000  # 1 second per frame
    fig_timeline.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500  # 0.5 second transition
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Add line chart showing trend over days
    st.subheader("📈 Defects Trend by Day")
    
    # Calculate daily statistics
    daily_stats = timeline_data.groupby('Day')['Defects'].agg(['mean', 'max', 'min', 'std']).reset_index()
    daily_stats['DayLabel'] = 'Day ' + daily_stats['Day'].astype(str)
    
    fig_trend = px.line(
        daily_stats,
        x='Day',
        y=['mean', 'max', 'min'],
        title='Daily Defects Statistics Trend',
        labels={
            'value': 'Number of Defects',
            'variable': 'Statistic',
            'Day': 'Day'
        },
        color_discrete_map={
            'mean': 'blue',
            'max': 'red', 
            'min': 'green'
        }
    )
    
    fig_trend.update_layout(
        height=400,
        xaxis_title='Day',
        yaxis_title='Number of Defects',
        legend_title='Statistics'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)