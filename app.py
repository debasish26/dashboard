import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from plotly.subplots import make_subplots
import random
from io import BytesIO
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import json
import os


# Helper function to safely render Plotly charts
def safe_plotly_chart(fig, use_container_width=True):
    """Safely render a plotly figure by converting to and from JSON"""
    try:
        # Try the normal way first
        st.plotly_chart(fig, use_container_width=use_container_width)
    except AttributeError as e:
        # If orjson error occurs, fallback to manual JSON conversion
        if "orjson" in str(e):
            # Convert to JSON and back to avoid orjson issues
            fig_json = json.dumps(fig.to_dict())
            fig_dict = json.loads(fig_json)
            # Create a new figure from the dictionary
            if isinstance(fig, go.Figure):
                new_fig = go.Figure(fig_dict)
            else:
                # Handle Plotly Express figures
                new_fig = go.Figure(fig_dict)
            # Try again with the new figure
            st.plotly_chart(new_fig, use_container_width=use_container_width)
        else:
            # If it's a different error, raise it
            raise e

# Set page configuration
st.set_page_config(
    page_title="Video Game Sales Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Dashboard title */
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    /* Subtitle */
    .dashboard-subtitle {
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        text-align: center;
        opacity: 0.8;
    }

    /* Metric cards */
    .metric-card {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        border-radius: 5px;
        padding: 1rem;
        text-align: center;
    }

    /* Metric value */
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }

    /* Metric label */
    .metric-label {
        font-size: 1rem;
        opacity: 0.8;
    }

    /* Help tooltip */
    .help-tooltip {
        font-size: 0.8rem;
        color: #9e9e9e;
        font-style: italic;
    }

    /* Filter section title */
    .filter-title {
        font-weight: bold;
        margin-bottom: 0.2rem;
    }

    /* Filter section */
    .filter-section {
        background-color: rgba(28, 131, 225, 0.05);
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'theme' not in st.session_state:
    st.session_state['theme'] = "dark"

if 'preset_publisher' not in st.session_state:
    st.session_state['preset_publisher'] = None

if 'preset_platform' not in st.session_state:
    st.session_state['preset_platform'] = None

if 'preset_years' not in st.session_state:
    st.session_state['preset_years'] = None

if 'preset_genre' not in st.session_state:
    st.session_state['preset_genre'] = None

# Functions for data loading and processing
@st.cache_data
def load_data():
    df = pd.read_csv('vgsales.csv')
    # Handle missing values
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Publisher'] = df['Publisher'].fillna('Unknown')
    return df

# Load data
df = load_data()

# Page styling
def apply_theme(theme):
    if theme == "dark":
        st.markdown("""
        <style>
        .main {background-color: #0E1117; color: white;}
        .sidebar .sidebar-content {background-color: #0E1117; color: white;}
        .streamlit-container {background-color: #0E1117; color: white;}
        .stTabs [data-baseweb="tab-list"] {background-color: #262730; color: white;}
        .stTabs [data-baseweb="tab"] {color: white;}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main {background-color: white; color: #0E1117;}
        .sidebar .sidebar-content {background-color: white; color: #0E1117;}
        .streamlit-container {background-color: white; color: #0E1117;}
        .stTabs [data-baseweb="tab-list"] {background-color: #F0F2F6; color: #0E1117;}
        .stTabs [data-baseweb="tab"] {color: #0E1117;}
        </style>
        """, unsafe_allow_html=True)

# Apply the current theme
apply_theme(st.session_state['theme'])

# Initialize filtered_df to the full dataset at the start
filtered_df = df.copy()

# Sidebar
with st.sidebar:
    # Logo and title section
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("")
    with col2:
        st.markdown("### 🎮 Game Sales Explorer")

    st.markdown("---")

    # Help section for new users
    with st.expander("❓ New to this dashboard?", expanded=False):
        st.markdown("""
        **Welcome to the Video Game Sales Dashboard!**

        This dashboard allows you to explore video game sales data from 1980 to 2020. Here's how to use it:

        1. Use the filters below to narrow down the data
        2. View different analyses in the tabs on the main page
        3. Hover over charts for more details
        4. Try the quick filter presets for popular views

        If you have any questions, click the "❓" icons next to each filter!
        """)

    # Quick filter presets
    st.subheader("🚀 Quick Filter Presets")
    preset_cols = st.columns(2)
    with preset_cols[0]:
        if st.button("Nintendo Games"):
            st.session_state['preset_publisher'] = 'Nintendo'
            st.rerun()
    with preset_cols[1]:
        if st.button("PlayStation Games"):
            st.session_state['preset_platform'] = 'PS3'
            st.rerun()

    preset_cols2 = st.columns(2)
    with preset_cols2[0]:
        if st.button("2010-2015 Games"):
            st.session_state['preset_years'] = (2010, 2015)
            st.rerun()
    with preset_cols2[1]:
        if st.button("Action Games"):
            st.session_state['preset_genre'] = 'Action'
            st.rerun()

    # Clear filters button
    if st.button("🔄 Clear All Filters", use_container_width=True):
        st.session_state['preset_publisher'] = None
        st.session_state['preset_platform'] = None
        st.session_state['preset_years'] = None
        st.session_state['preset_genre'] = None
        # Clear any session state for platforms and genres
        if 'selected_platforms' in st.session_state:
            del st.session_state['selected_platforms']
        if 'selected_genres' in st.session_state:
            del st.session_state['selected_genres']
        st.rerun()

    st.markdown("---")

    # Theme switcher
    st.subheader("🎨 Appearance")
    theme_option = st.radio("Select theme", ["Dark Mode", "Light Mode"], index=0 if st.session_state['theme'] == "dark" else 1)
    if theme_option == "Dark Mode" and st.session_state['theme'] != "dark":
        st.session_state['theme'] = "dark"
        apply_theme("dark")
        st.rerun()
    elif theme_option == "Light Mode" and st.session_state['theme'] != "light":
        st.session_state['theme'] = "light"
        apply_theme("light")
        st.rerun()

    st.markdown("---")

    # Filters
    st.markdown('<div class="filter-title">📊 Data Filters</div>', unsafe_allow_html=True)

    # Year range slider with preset handling
    year_min = int(df['Year'].min())
    year_max = int(df['Year'].max())
    year_help = "Filter games by their release year. Drag both ends to set a range."

    # Handle year preset if set
    if st.session_state['preset_years'] is not None:
        preset_year_min, preset_year_max = st.session_state['preset_years']
        years = st.slider('📅 Year Range', year_min, year_max,
                          (preset_year_min, preset_year_max),
                          help=year_help)
    else:
        years = st.slider('📅 Year Range', year_min, year_max,
                         (year_min, year_max),
                         help=year_help)

    # Platform multiselect with preset handling
    platforms = sorted(df['Platform'].unique())
    platform_help = "Select one or more gaming platforms to filter the data."

    # Handle platform preset if set
    if st.session_state['preset_platform'] is not None:
        selected_platforms = st.multiselect('🎮 Platform',
                                           options=platforms,
                                           default=[st.session_state['preset_platform']],
                                           help=platform_help)
    elif 'selected_platforms' in st.session_state:
        selected_platforms = st.multiselect('🎮 Platform',
                                           options=platforms,
                                           default=st.session_state['selected_platforms'],
                                           help=platform_help)
    else:
        selected_platforms = st.multiselect('🎮 Platform',
                                           options=platforms,
                                           default=platforms[:5],
                                           help=platform_help)

    st.markdown('<div class="help-tooltip">Tip: You can search for platforms by typing</div>', unsafe_allow_html=True)

    # Genre multiselect with preset handling
    genres = sorted(df['Genre'].unique())
    genre_help = "Select one or more game genres to filter the data."

    # Handle genre preset if set
    if st.session_state['preset_genre'] is not None:
        selected_genres = st.multiselect('🏆 Genre',
                                        options=genres,
                                        default=[st.session_state['preset_genre']],
                                        help=genre_help)
    elif 'selected_genres' in st.session_state:
        selected_genres = st.multiselect('🏆 Genre',
                                        options=genres,
                                        default=st.session_state['selected_genres'],
                                        help=genre_help)
    else:
        selected_genres = st.multiselect('🏆 Genre',
                                        options=genres,
                                        default=genres[:5],
                                        help=genre_help)

    # All button to select all publishers and genres - moved here after platforms and genres are defined
    if st.button("All Games", use_container_width=True):
        st.session_state['preset_publisher'] = None
        st.session_state['preset_platform'] = None
        st.session_state['preset_years'] = None
        st.session_state['preset_genre'] = None
        # Set selected_platforms to all platforms
        st.session_state['selected_platforms'] = platforms
        # Set selected_genres to all genres
        st.session_state['selected_genres'] = genres
        st.rerun()

    # Publisher dropdown with preset handling
    top_publishers = ['All'] + sorted(df['Publisher'].value_counts().head(20).index.tolist())
    publisher_help = "Select a publisher to view only their games."

    # Handle publisher preset if set
    if st.session_state['preset_publisher'] is not None:
        publisher_index = top_publishers.index(st.session_state['preset_publisher']) if st.session_state['preset_publisher'] in top_publishers else 0
        selected_publisher = st.selectbox('🏢 Publisher',
                                         options=top_publishers,
                                         index=publisher_index,
                                         help=publisher_help)
    else:
        selected_publisher = st.selectbox('🏢 Publisher',
                                         options=top_publishers,
                                         help=publisher_help)

    # Apply filters to the dataframe
    filtered_df = df.copy()

    # Apply filters
    filtered_df = filtered_df[(filtered_df['Year'] >= years[0]) & (filtered_df['Year'] <= years[1])]

    if selected_platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(selected_platforms)]

    if selected_genres:
        filtered_df = filtered_df[filtered_df['Genre'].isin(selected_genres)]

    if selected_publisher != 'All':
        filtered_df = filtered_df[filtered_df['Publisher'] == selected_publisher]

    # Data summary
    st.markdown("---")

    # Display a summary of current filters
    st.subheader("📋 Current Selection")
    st.info(f"""
    Showing **{len(filtered_df):,}** games from **{years[0]}** to **{years[1]}**

    Platforms: **{len(selected_platforms)}** selected

    Genres: **{len(selected_genres)}** selected

    Publisher: **{selected_publisher}**
    """)

    # Download button
    st.subheader("💾 Export Data")

    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df)
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv,
        file_name='vgsales_filtered.csv',
        mime='text/csv',
    )

# Main page
# Dashboard title with styled markdown
st.markdown('<div class="dashboard-title">🎮 Video Game Sales Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Interactive analytics for global video game sales from 1980 to 2020</div>', unsafe_allow_html=True)

# Display dataset overview metrics in a style similar to the example
st.markdown("## 📈 Overview Metrics")

# Key metrics in columns with styled cards
metric_cols = st.columns(4)

with metric_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{len(filtered_df):,}</div>
        <div class="metric-label">Total Games</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${filtered_df['Global_Sales'].sum():.2f}M</div>
        <div class="metric-label">Global Sales</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{filtered_df['Platform'].nunique()}</div>
        <div class="metric-label">Platforms</div>
    </div>
    """, unsafe_allow_html=True)

with metric_cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{filtered_df['Publisher'].nunique()}</div>
        <div class="metric-label">Publishers</div>
    </div>
    """, unsafe_allow_html=True)

# Main dashboard content
st.markdown("---")

# Add description of current selection
if selected_publisher != 'All' or len(selected_platforms) < len(platforms) or len(selected_genres) < len(genres):
    filter_message = []
    if selected_publisher != 'All':
        filter_message.append(f"Publisher: {selected_publisher}")
    if len(selected_platforms) < len(platforms):
        if len(selected_platforms) <= 3:
            filter_message.append(f"Platforms: {', '.join(selected_platforms)}")
        else:
            filter_message.append(f"Platforms: {len(selected_platforms)} selected")
    if len(selected_genres) < len(genres):
        if len(selected_genres) <= 3:
            filter_message.append(f"Genres: {', '.join(selected_genres)}")
        else:
            filter_message.append(f"Genres: {len(selected_genres)} selected")
    if years[0] > year_min or years[1] < year_max:
        filter_message.append(f"Years: {years[0]} to {years[1]}")

    st.info(f"📊 Current filters: {' | '.join(filter_message)}")

# Create tabs for different sections
tab1, tab2, tab3,  tab5 = st.tabs(["📊 Sales Analysis", "🌍 Geographic Sales", "🎲 Genre Insights",  "📖 Data Storytelling"])

# Tab 1: Sales Analysis
with tab1:
    st.header("📊 Sales Analysis")

    # Add helper text for new users
    st.markdown("""
    <div class="help-tooltip">
    This section shows sales trends and comparisons. Hover over charts for more details, or use the play button on the Publisher Performance chart to view animation.
    </div>
    """, unsafe_allow_html=True)

    # Sales trend over time
    st.subheader("Sales Trend Over Time")

    # Group by Year and calculate sales
    yearly_sales = filtered_df.groupby('Year')['Global_Sales'].sum().reset_index()
    yearly_sales = yearly_sales.dropna()  # Remove rows with NaN years

    # Create interactive line chart with Plotly
    fig_trend = px.line(
        yearly_sales,
        x='Year',
        y='Global_Sales',
        title='Global Game Sales Trend Over Time (in millions)',
        labels={'Global_Sales': 'Global Sales (millions)', 'Year': 'Year'},
        template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
    )

    fig_trend.update_layout(
        xaxis=dict(tickmode='linear', dtick=5),
        hovermode='x unified',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    fig_trend.update_traces(
        line=dict(width=3),
        mode='lines+markers'
    )

    safe_plotly_chart(fig_trend, use_container_width=True)

    # Create two columns for the next charts
    col1, col2 = st.columns(2)

    with col1:
        # Top 10 bestselling games
        st.subheader("Top 10 Bestselling Games")

        top10_games = filtered_df.sort_values('Global_Sales', ascending=False).head(10)

        fig_top10 = px.bar(
            top10_games,
            x='Global_Sales',
            y='Name',
            orientation='h',
            color='Publisher',
            hover_data=['Platform', 'Year', 'Genre'],
            title='Top 10 Best-Selling Games (Global Sales in millions)',
            labels={'Global_Sales': 'Global Sales (millions)', 'Name': 'Game Title', 'Publisher': 'Publisher'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        fig_top10.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        safe_plotly_chart(fig_top10, use_container_width=True)

    with col2:
        # Platform comparison - switched to Plotly for consistency
        st.subheader("Platform Comparison")

        # Group by Platform
        platform_sales = filtered_df.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False).head(10).reset_index()

        fig_platform = px.bar(
            platform_sales,
            x='Global_Sales',
            y='Platform',
            orientation='h',
            color='Global_Sales',
            color_continuous_scale='blues' if st.session_state['theme'] == 'light' else 'Plasma',
            title='Top 10 Platforms by Global Sales',
            labels={'Global_Sales': 'Global Sales (millions)', 'Platform': 'Platform'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        fig_platform.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500,
            margin=dict(l=20, r=20, t=40, b=20)
        )

        safe_plotly_chart(fig_platform, use_container_width=True)

    # Publisher analysis with animated bar chart
    st.subheader("Publisher Performance Over Time")

    # Add helper text for the animation
    st.markdown("""
    <div class="help-tooltip">
    Click the play button below to see how publisher performance changed over time.
    </div>
    """, unsafe_allow_html=True)

    # Get top 5 publishers by global sales
    top_publishers = filtered_df.groupby('Publisher')['Global_Sales'].sum().sort_values(ascending=False).head(5).index.tolist()

    # Filter data for top publishers and create a DataFrame grouped by Year and Publisher
    top_pub_df = filtered_df[filtered_df['Publisher'].isin(top_publishers)]
    pub_yearly = top_pub_df.groupby(['Year', 'Publisher'])['Global_Sales'].sum().reset_index()
    pub_yearly = pub_yearly.dropna()  # Remove rows with NaN years

    # Create an animated bar chart
    fig_pub_animated = px.bar(
        pub_yearly,
        x='Publisher',
        y='Global_Sales',
        color='Publisher',
        animation_frame='Year',
        range_y=[0, pub_yearly['Global_Sales'].max() * 1.1],
        title='Sales by Top Publishers Over Time',
        labels={'Global_Sales': 'Global Sales (millions)', 'Publisher': 'Publisher', 'Year': 'Year'},
        template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
    )

    fig_pub_animated.update_layout(
        xaxis={'categoryorder': 'total descending'},
        height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    safe_plotly_chart(fig_pub_animated, use_container_width=True)

# Tab 2: Geographic Sales
with tab2:
    st.header("🌍 Geographic Sales")

    # Regional sales comparison
    st.subheader("Regional Sales Comparison")

    # Calculate total sales by region
    total_na = filtered_df['NA_Sales'].sum()
    total_eu = filtered_df['EU_Sales'].sum()
    total_jp = filtered_df['JP_Sales'].sum()
    total_other = filtered_df['Other_Sales'].sum()

    # Create a DataFrame for the regional data
    regions_df = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Japan', 'Rest of World'],
        'Sales': [total_na, total_eu, total_jp, total_other]
    })

    # Create a pie chart for regional distribution
    fig_regions = px.pie(
        regions_df,
        values='Sales',
        names='Region',
        hole=0.4,
        title='Global Sales Distribution by Region',
        template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
    )

    safe_plotly_chart(fig_regions, use_container_width=True)

    # Regional preferences analysis
    st.subheader("Regional Gaming Preferences")

    col1, col2 = st.columns(2)

    with col1:
        # Top genres by region
        st.markdown("#### Top Genres by Region")

        # Create a long-format DataFrame for genres by region
        genres_by_region = pd.DataFrame({
            'North America': filtered_df.groupby('Genre')['NA_Sales'].sum().sort_values(ascending=False).head(5),
            'Europe': filtered_df.groupby('Genre')['EU_Sales'].sum().sort_values(ascending=False).head(5),
            'Japan': filtered_df.groupby('Genre')['JP_Sales'].sum().sort_values(ascending=False).head(5)
        }).reset_index()

        genres_long = pd.melt(genres_by_region, id_vars=['Genre'], value_vars=['North America', 'Europe', 'Japan'],
                              var_name='Region', value_name='Sales')

        # Create a grouped bar chart
        fig_genres_region = px.bar(
            genres_long,
            x='Genre',
            y='Sales',
            color='Region',
            barmode='group',
            title='Top Genres by Region',
            labels={'Sales': 'Sales (millions)', 'Genre': 'Genre'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        safe_plotly_chart(fig_genres_region, use_container_width=True)

    with col2:
        # Regional performance over time
        st.markdown("#### Regional Sales Over Time")

        # Group by Year and calculate sales by region
        yearly_regional = filtered_df.groupby('Year')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
        yearly_regional = yearly_regional.dropna()  # Remove rows with NaN years

        # Convert to long format for Plotly
        yearly_regional_long = pd.melt(
            yearly_regional,
            id_vars=['Year'],
            value_vars=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
            var_name='Region',
            value_name='Sales'
        )

        # Clean region names
        yearly_regional_long['Region'] = yearly_regional_long['Region'].map({
            'NA_Sales': 'North America',
            'EU_Sales': 'Europe',
            'JP_Sales': 'Japan',
            'Other_Sales': 'Rest of World'
        })

        # Create the line chart
        fig_region_time = px.line(
            yearly_regional_long,
            x='Year',
            y='Sales',
            color='Region',
            title='Regional Sales Over Time',
            labels={'Sales': 'Sales (millions)', 'Year': 'Year'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        fig_region_time.update_layout(xaxis=dict(tickmode='linear', dtick=5))
        safe_plotly_chart(fig_region_time, use_container_width=True)

    # World map visualization
    st.subheader("Global Sales Distribution")

    # Create a world map data
    map_data = pd.DataFrame({
        'Country': ['United States', 'Canada', 'United Kingdom', 'France', 'Germany', 'Italy', 'Spain',
                   'Japan', 'Australia', 'Brazil', 'Mexico', 'China', 'Russia', 'South Korea'],
        'Sales': [total_na * 0.9, total_na * 0.1, total_eu * 0.3, total_eu * 0.2, total_eu * 0.25,
                 total_eu * 0.15, total_eu * 0.1, total_jp, total_other * 0.15, total_other * 0.15,
                 total_other * 0.1, total_other * 0.3, total_other * 0.15, total_other * 0.15],
        'iso_alpha': ['USA', 'CAN', 'GBR', 'FRA', 'DEU', 'ITA', 'ESP', 'JPN', 'AUS', 'BRA', 'MEX', 'CHN', 'RUS', 'KOR']
    })

    # Create choropleth map
    fig_map = px.choropleth(
        map_data,
        locations='iso_alpha',
        color='Sales',
        hover_name='Country',
        projection='natural earth',
        title='Estimated Video Game Sales Distribution Worldwide (millions)',
        color_continuous_scale=px.colors.sequential.Plasma,
        template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
    )

    safe_plotly_chart(fig_map, use_container_width=True)

    # Add a note about the map data
    st.info("⚠️ Note: This map shows an approximate distribution based on the regional data. Individual country data is estimated for visualization purposes.")

# Tab 3: Genre Insights
with tab3:
    st.header("🎲 Genre Insights")

    # Genre performance analysis
    st.subheader("Genre Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Get sales by genre
        genre_sales = filtered_df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False).reset_index()

        # Create a bar chart for genre sales
        fig_genre_sales = px.bar(
            genre_sales,
            x='Genre',
            y='Global_Sales',
            color='Genre',
            title='Global Sales by Genre',
            labels={'Global_Sales': 'Global Sales (millions)', 'Genre': 'Genre'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        safe_plotly_chart(fig_genre_sales, use_container_width=True)

    with col2:
        # Get number of games by genre
        genre_counts = filtered_df['Genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Count']

        # Create a bar chart for game counts by genre
        fig_genre_counts = px.bar(
            genre_counts,
            x='Genre',
            y='Count',
            color='Genre',
            title='Number of Games by Genre',
            labels={'Count': 'Number of Games', 'Genre': 'Genre'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        safe_plotly_chart(fig_genre_counts, use_container_width=True)

    # Genre popularity over time
    st.subheader("Genre Popularity Over Time")

    # Group data by year and genre
    genre_yearly = filtered_df.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()
    genre_yearly = genre_yearly.dropna()  # Remove rows with NaN years

    # Get top 5 genres for better visualization
    top_genres = filtered_df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False).head(5).index.tolist()
    genre_yearly_filtered = genre_yearly[genre_yearly['Genre'].isin(top_genres)]

    # Create line chart
    fig_genre_time = px.line(
        genre_yearly_filtered,
        x='Year',
        y='Global_Sales',
        color='Genre',
        title='Top 5 Genres Sales Trend Over Time',
        labels={'Global_Sales': 'Global Sales (millions)', 'Year': 'Year', 'Genre': 'Genre'},
        template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
    )

    fig_genre_time.update_layout(xaxis=dict(tickmode='linear', dtick=5))
    safe_plotly_chart(fig_genre_time, use_container_width=True)



# Tab 5: Data Storytelling
with tab5:
    st.header("📖 Data Storytelling")

    # Create an engaging storytelling layout
    st.markdown("""
    <style>
    .story-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .story-text {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
    }
    .highlight {
        background-color: rgba(255, 215, 0, 0.3);
        padding: 2px 5px;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Introduction
    st.markdown('<div class="story-header">🎮 The Evolution of Video Game Industry</div>', unsafe_allow_html=True)
    st.markdown('<div class="story-text">Let\'s explore the fascinating journey of video games through the years, highlighting key trends, shifts in consumer preferences, and the rise and fall of gaming platforms.</div>', unsafe_allow_html=True)

    # Let's create story sections using st.expander for each chapter
    with st.expander("Chapter 1: The Rise and Fall of Gaming Platforms 📈", expanded=True):
        # Platform evolution analysis
        platform_by_year = filtered_df.groupby(['Year', 'Platform'])['Global_Sales'].sum().reset_index()
        platform_by_year = platform_by_year.dropna()  # Remove NaN years

        # Get top platforms over time
        top_platforms_overall = filtered_df.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False).head(6).index.tolist()
        platform_evolution_df = platform_by_year[platform_by_year['Platform'].isin(top_platforms_overall)]

        # Create the line chart for platform evolution
        fig_platform_evolution = px.line(
            platform_evolution_df,
            x='Year',
            y='Global_Sales',
            color='Platform',
            title='Evolution of Top Gaming Platforms',
            labels={'Global_Sales': 'Global Sales (millions)', 'Year': 'Year', 'Platform': 'Platform'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        fig_platform_evolution.update_layout(xaxis=dict(tickmode='linear', dtick=5))
        safe_plotly_chart(fig_platform_evolution, use_container_width=True)

        st.markdown('<div class="story-text">The gaming industry has witnessed dramatic shifts in platform dominance over the decades. From the rise of home consoles like the <span class="highlight">NES and PlayStation</span> to the emergence of handheld gaming with the <span class="highlight">Game Boy and Nintendo DS</span>, each platform has had its moment in the spotlight.</div>', unsafe_allow_html=True)

        st.markdown('<div class="story-text">As technology advanced, we saw a transition from 8-bit and 16-bit consoles to more sophisticated systems capable of 3D rendering and online connectivity. Each generation brought new capabilities and expanded the potential market for video games.</div>', unsafe_allow_html=True)

    with st.expander("Chapter 2: Changing Genre Preferences 🎭", expanded=True):
        # Genre evolution analysis
        genre_by_year = filtered_df.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()
        genre_by_year = genre_by_year.dropna()  # Remove NaN years

        # Get top genres
        top_genres_overall = filtered_df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False).head(5).index.tolist()
        genre_evolution_df = genre_by_year[genre_by_year['Genre'].isin(top_genres_overall)]

        # Create the area chart for genre evolution
        fig_genre_evolution = px.area(
            genre_evolution_df,
            x='Year',
            y='Global_Sales',
            color='Genre',
            title='Evolution of Game Genres',
            labels={'Global_Sales': 'Global Sales (millions)', 'Year': 'Year', 'Genre': 'Genre'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        fig_genre_evolution.update_layout(xaxis=dict(tickmode='linear', dtick=5))
        safe_plotly_chart(fig_genre_evolution, use_container_width=True)

        st.markdown('<div class="story-text">Consumer preferences have evolved substantially over time. In the early days, <span class="highlight">platformers and puzzles</span> dominated the market. As gaming matured, we saw the rise of <span class="highlight">action, sports, and role-playing games</span>.</div>', unsafe_allow_html=True)

        st.markdown('<div class="story-text">Different regions also developed distinct preferences. While North America embraced sports and action titles, Japan showed a stronger affinity for role-playing games and unique gaming experiences.</div>', unsafe_allow_html=True)

    with st.expander("Chapter 3: The Publishers' Battle 🏢", expanded=True):
        # Publishers evolution
        top_publishers_overall = filtered_df.groupby('Publisher')['Global_Sales'].sum().sort_values(ascending=False).head(5).index.tolist()
        publishers_by_year = filtered_df[filtered_df['Publisher'].isin(top_publishers_overall)].groupby(['Year', 'Publisher'])['Global_Sales'].sum().reset_index()
        publishers_by_year = publishers_by_year.dropna()  # Remove NaN years

        # Create stacked bar chart
        fig_publisher_battle = px.bar(
            publishers_by_year,
            x='Year',
            y='Global_Sales',
            color='Publisher',
            title='Battle of the Publishers Over Time',
            labels={'Global_Sales': 'Global Sales (millions)', 'Year': 'Year', 'Publisher': 'Publisher'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white'
        )

        safe_plotly_chart(fig_publisher_battle, use_container_width=True)

        st.markdown('<div class="story-text">Behind every successful game is a publisher with the vision and resources to bring it to market. The industry has seen fierce competition between publishing giants like <span class="highlight">Nintendo, Electronic Arts, and Activision</span>.</div>', unsafe_allow_html=True)

        st.markdown('<div class="story-text">Nintendo has consistently dominated with its first-party titles and iconic franchises. Electronic Arts built its empire on sports titles and licensed games, while Activision found tremendous success with its Call of Duty franchise.</div>', unsafe_allow_html=True)

    with st.expander("Chapter 4: Blockbuster Franchises 🌟", expanded=True):
        # Find game franchises (simplified by looking for common name patterns)
        filtered_df['Franchise'] = filtered_df['Name'].str.split(':').str[0]
        franchise_sales = filtered_df.groupby('Franchise')['Global_Sales'].sum().sort_values(ascending=False).head(10).reset_index()

        # Create bar chart for franchises
        fig_franchises = px.bar(
            franchise_sales,
            x='Franchise',
            y='Global_Sales',
            color='Global_Sales',
            title='Top 10 Game Franchises by Global Sales',
            labels={'Global_Sales': 'Global Sales (millions)', 'Franchise': 'Franchise'},
            template='plotly_dark' if st.session_state['theme'] == 'dark' else 'plotly_white',
            color_continuous_scale=px.colors.sequential.Viridis
        )

        safe_plotly_chart(fig_franchises, use_container_width=True)

        st.markdown('<div class="story-text">Franchises have become the backbone of the gaming industry. Iconic series like <span class="highlight">Mario, Pokémon, and Call of Duty</span> have generated billions in revenue across multiple titles and platforms.</div>', unsafe_allow_html=True)

        st.markdown('<div class="story-text">These successful franchises often leverage nostalgia, established gameplay mechanics, and familiar characters to maintain player interest across generations.</div>', unsafe_allow_html=True)

    # Random Fun Fact Generator
    st.markdown("## 🎲 Random Fun Fact Generator")

    # Define fun facts based on data analysis
    fun_facts = [
        f"The best-selling video game of all time is {filtered_df.sort_values('Global_Sales', ascending=False).iloc[0]['Name']} with {filtered_df.sort_values('Global_Sales', ascending=False).iloc[0]['Global_Sales']:.2f}M copies sold globally!",
        f"Nintendo has published {len(filtered_df[filtered_df['Publisher'] == 'Nintendo'])} games in our dataset, more than any other publisher!",
        f"The most productive year for gaming was {filtered_df.groupby('Year')['Name'].count().idxmax()}, with {filtered_df.groupby('Year')['Name'].count().max()} games released!",
        f"Japan seems to prefer {filtered_df.groupby('Genre')['JP_Sales'].sum().idxmax()} games, while North America prefers {filtered_df.groupby('Genre')['NA_Sales'].sum().idxmax()} games!",
        f"The platform with the highest average sales per game is {filtered_df.groupby('Platform')['Global_Sales'].mean().idxmax()}, with {filtered_df.groupby('Platform')['Global_Sales'].mean().max():.2f}M average sales!",

        f"European gamers spend more on {filtered_df.groupby('Genre')['EU_Sales'].sum().idxmax()} games than any other genre!",
        f"The average lifespan of a gaming platform in the dataset is approximately 7 years!",

        f"Sports games made up {len(filtered_df[filtered_df['Genre'] == 'Sports']) / len(filtered_df) * 100:.1f}% of all video games in our dataset!"
    ]

    # Button to generate a random fact
    if st.button("🎮 Generate Random Fun Fact"):
        st.success(random.choice(fun_facts))
    # Conclusion
    st.markdown('<div class="story-header">The Future of Gaming 🚀</div>', unsafe_allow_html=True)
    st.markdown('<div class="story-text">As we look to the future, the video game industry continues to evolve at a rapid pace. New technologies like cloud gaming, virtual reality, and artificial intelligence are reshaping how games are developed and experienced.</div>', unsafe_allow_html=True)
    st.markdown('<div class="story-text">While this dataset only covers up to recent years, the trends and patterns we\'ve observed provide valuable insights into consumer preferences and market dynamics that will likely influence the industry for years to come.</div>', unsafe_allow_html=True)
