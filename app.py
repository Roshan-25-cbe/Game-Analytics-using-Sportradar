import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px # Import Plotly Express

# --- Database Configuration ---
DB_HOST = "localhost"
DB_NAME = "game_analytics_db"
DB_USER = "postgres"
DB_PASSWORD = "Roshan@2025" # !! MAKE SURE THIS IS YOUR CORRECT POSTGRES PASSWORD !!

# --- Database Connection & Data Fetching ---
@st.cache_resource
def get_db_connection():
    """Establishes and caches a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    except psycopg2.Error as e:
        st.error(f"DB Connection Error: {e}. Please check your DB credentials and ensure PostgreSQL is running.")
        return None

@st.cache_data(ttl=3600)
def fetch_data(query, params=None):
    """Fetches data from the database using a given SQL query."""
    conn = get_db_connection()
    if conn:
        try:
            return pd.read_sql(query, conn, params=params)
        except Exception as e:
            st.error(f"Query Error: {e}")
            return pd.DataFrame() # Return empty DataFrame on error
    return pd.DataFrame()

# --- Utility Functions for Filter Options ---
@st.cache_data(ttl=3600)
def get_unique_values(table, column):
    """Fetches unique values from a specified column in a table."""
    query = f"SELECT DISTINCT {column} FROM {table} ORDER BY {column};"
    df = fetch_data(query)
    return df[column].tolist() if not df.empty else []

@st.cache_data(ttl=3600)
def get_all_competition_category_names():
    """
    Fetches all distinct human-readable category names from the public.categories table.
    """
    query = """
    SELECT DISTINCT category_name
    FROM public.categories
    ORDER BY category_name;
    """
    df = fetch_data(query)
    return df['category_name'].tolist() if not df.empty else []

@st.cache_data(ttl=3600)
def get_competitor_names_with_country():
    """Fetches competitor names along with their countries for the filter dropdown."""
    query = "SELECT name, country FROM Competitors ORDER BY name, country;"
    df = fetch_data(query)
    if not df.empty:
        # Format as "Name (Country)" for display
        return [f"{row['name']} ({row['country']})" for index, row in df.iterrows()]
    return []


# --- Streamlit Application Layout ---
st.set_page_config(layout="wide", page_title="Tennis Rankings Explorer")
st.title("🎾 Tennis Rankings Explorer")
st.markdown("Unlock insights from Sportradar Tennis Data.")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Rank Range Slider
min_rank_slider_val = 1
max_rank_slider_val = 500
competitor_rank_range = st.sidebar.slider(
    "Rank Range",
    min_rank_slider_val, max_rank_slider_val, (min_rank_slider_val, 100 if max_rank_slider_val >= 100 else max_rank_slider_val)
)
min_rank, max_rank = competitor_rank_range[0], competitor_rank_range[1]

# --- Combined Competitor Filter (Now with Country) ---
competitor_options_with_country = ["All Competitors"] + get_competitor_names_with_country()
selected_competitor_filter = st.sidebar.selectbox("Competitor Filter", competitor_options_with_country)

# Extract just the name from the selected string for the query
actual_selected_competitor_name = None
if selected_competitor_filter != "All Competitors":
    # Assumes format "Name (Country)"
    actual_selected_competitor_name = selected_competitor_filter.split(' (')[0].strip()


all_categories = ["Choose an option"] + get_all_competition_category_names()
selected_category = st.sidebar.selectbox("Select Category", all_categories)

all_countries = ["Choose an option"] + get_unique_values("Competitors", "country")
selected_country = st.sidebar.selectbox("Select a Country", all_countries)

min_points, max_points = st.sidebar.slider("Competitor Rank Points", 0, 10000, (0, 10000))


# --- Main Content Area - Tabs ---
tab_leaderboard, tab_venues, tab_all_comps, tab_details = st.tabs([
    "Leaderboard", "Venues and Complexes", "All Competitions", "Competitor Details Viewer"
])


with tab_leaderboard:
    st.header("Leaderboard")
    
    lb_query = """
    SELECT
        c.name AS "Competitor Name",
        c.country AS "Country",
        cr.rank AS "Rank",
        cr.points AS "Points",
        cr.movement AS "Movement",
        cr.competitions_played AS "Played"
    FROM
        Competitor_Rankings cr
    JOIN
        Competitors c ON cr.competitor_id = c.competitor_id
    WHERE
        cr.rank BETWEEN %(min_rank)s AND %(max_rank)s
        AND cr.points BETWEEN %(min_points)s AND %(max_points)s
    """
    lb_params = {
        'min_rank': min_rank,
        'max_rank': max_rank,
        'min_points': min_points,
        'max_points': max_points
    }

    # Apply combined competitor filter to query using the extracted name
    if actual_selected_competitor_name:
        lb_query += " AND LOWER(c.name) = LOWER(%(comp_name)s)"
        lb_params['comp_name'] = actual_selected_competitor_name
    
    if selected_country != "Choose an option":
        lb_query += " AND c.country = %(country)s"
        lb_params['country'] = selected_country

    lb_query += """
    ORDER BY
        cr.rank ASC
    LIMIT 500;
    """
    df_leaderboard = fetch_data(lb_query, params=lb_params)

    if not df_leaderboard.empty:
        st.dataframe(df_leaderboard, use_container_width=True)
    else:
        st.info("No leaderboard data found with current filters.")

with tab_venues:
    st.header("Venues and Complexes")
    st.info("This section will display information about venues and complexes.")
    venues_query = """
    SELECT
        complex_name AS "Complex Name",
        venue_name AS "Venue Name",
        city_name AS "City",
        country_name AS "Country"
    FROM
        Complexes cmpl
    JOIN
        Venues vn ON cmpl.complex_id = vn.complex_id
    ORDER BY complex_name LIMIT 500;
    """
    df_venues = fetch_data(venues_query)
    if not df_venues.empty:
        st.dataframe(df_venues, use_container_width=True, hide_index=True)
    else:
        st.info("No venue or complex data available.")


with tab_all_comps:
    st.header("All Competitions")

    # --- New: Fetch data for Pie Chart - Competitions by Category ---
    @st.cache_data(ttl=3600)
    def get_competitions_by_category():
        query = """
        SELECT
            cat.category_name,
            COUNT(comp.competition_id) AS competition_count
        FROM
            Competitions comp
        JOIN
            public.categories cat ON comp.category_id = cat.category_id
        GROUP BY
            cat.category_name
        ORDER BY
            competition_count DESC;
        """
        return fetch_data(query)

    df_category_counts = get_competitions_by_category()

    if not df_category_counts.empty:
        st.subheader("Distribution of Competitions by Category")
        fig = px.pie(df_category_counts, values='competition_count', names='category_name',
                     title='Competitions by Category',
                     hole=0.3) # Add a hole for donut effect
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category distribution data available for the pie chart.")


    st.subheader("All Competitions Table") # Subheader for clarity when both chart and table are present
    comp_query = """
    SELECT
        comp.competition_name AS "Competition Name",
        cat.category_name AS "Category",
        comp.gender AS "Gender",
        comp.type AS "Type"
    FROM
        Competitions comp
    JOIN
        public.categories cat ON comp.category_id = cat.category_id
    """
    params = {}
    if selected_category != "Choose an option":
        comp_query += " WHERE cat.category_name = %(category_name)s"
        params['category_name'] = selected_category
    
    comp_query += " ORDER BY comp.competition_name LIMIT 500;"
    df_comps = fetch_data(comp_query, params=params)
    if not df_comps.empty:
        st.dataframe(df_comps, use_container_width=True, hide_index=True)
    else:
        st.info("No competitions found.")

with tab_details:
    st.header("Competitor Details Viewer")
    # Use the extracted competitor name for details
    comp_to_display = actual_selected_competitor_name

    if comp_to_display:
        st.write(f"Showing details for: {comp_to_display}")
        detail_query = """
        SELECT c.name, c.country, cr.rank, cr.movement, cr.points, cr.competitions_played
        FROM Competitors c JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE LOWER(c.name) = LOWER(%(name)s) LIMIT 1;
        """
        df_details = fetch_data(detail_query, params={'name': comp_to_display})
        if not df_details.empty:
            st.dataframe(df_details, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No details found for '{comp_to_display}'.")
    else:
        st.info("Please select a competitor from the sidebar filter to view details.")

st.caption("Note: Data is from Sportradar API, potentially limited by trial key access. Ensure PostgreSQL is running.")
