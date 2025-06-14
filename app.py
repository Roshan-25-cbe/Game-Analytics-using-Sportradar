import streamlit as st
import psycopg2
import pandas as pd

# --- Database Configuration ---
DB_HOST = "localhost"
DB_NAME = "game_analytics_db"
DB_USER = "postgres"
DB_PASSWORD = "Roshan@2025" # !! MAKE SURE THIS IS YOUR CORRECT POSTGRES PASSWORD !!

# --- Database Connection Function ---
@st.cache_resource # Caches the connection for efficiency
def get_db_connection():
    """Establishes and caches a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"Error connecting to database: {e}. Please check your DB credentials and ensure PostgreSQL is running.")
        return None

# --- Data Fetching Functions ---
@st.cache_data(ttl=3600) # Caches data for 1 hour
def fetch_data(query, params=None): # Added params argument for parameterized queries
    """Fetches data from the database using a given SQL query."""
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn, params=params)
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame() # Return empty DataFrame on error
    return pd.DataFrame()

# --- Utility Functions (for dynamic filter options) ---
@st.cache_data(ttl=3600)
def get_all_competitor_names():
    query = "SELECT DISTINCT name FROM Competitors ORDER BY name;"
    df = fetch_data(query)
    return df['name'].tolist() if not df.empty else []

@st.cache_data(ttl=3600)
def get_all_countries():
    query = "SELECT DISTINCT country FROM Competitors ORDER BY country;"
    df = fetch_data(query)
    return df['country'].tolist() if not df.empty else []

@st.cache_data(ttl=3600)
def get_max_rank_points():
    query = "SELECT MAX(points) FROM Competitor_Rankings;"
    df = fetch_data(query)
    return int(df.iloc[0,0]) if not df.empty and df.iloc[0,0] is not None else 10000 # Default if no data

@st.cache_data(ttl=3600)
def get_max_competitions_played():
    query = "SELECT MAX(competitions_played) FROM Competitor_Rankings;"
    df = fetch_data(query)
    return int(df.iloc[0,0]) if not df.empty and df.iloc[0,0] is not None else 50 # Default if no data


# --- Streamlit Application Layout ---

st.set_page_config(layout="wide", page_title="Tennis Rankings Explorer") # Matches sample title

st.title("🎾 Tennis Rankings Explorer") # Matches sample title
st.markdown("Unlock insights from Sportradar Tennis Data.") #

# --- Sidebar Filters (Matching sample UI) ---
st.sidebar.header("Filters") # Matches sample UI

# Select a Competitor
all_competitor_names = ["Choose an option"] + get_all_competitor_names()
selected_competitor = st.sidebar.selectbox("Select a Competitor", all_competitor_names) # Matches sample UI

# Gender (from previous step, but re-positioned)
# Note: Gender is not directly in Competitors table. If needed, this filter
# would require more complex logic involving Competition data or a different ranking source.
# For now, it will act as a visual placeholder matching the sample.
gender_options = ["Choose an option", "men", "women"] # Updated to match sample dropdown style
selected_gender = st.sidebar.selectbox("Gender", gender_options) # Matches sample UI

# Select a Country
all_countries = ["Choose an option"] + get_all_countries()
selected_country = st.sidebar.selectbox("Select a Country", all_countries) # Matches sample UI

# Competitor Rank (Slider)
max_rank_val = 500 # Adjust based on actual data range if needed
competitor_rank_range = st.sidebar.slider(
    "Competitor Rank", # Matches sample UI
    1, max_rank_val, (1, max_rank_val) # Default range
)
min_rank, max_rank = competitor_rank_range[0], competitor_rank_range[1]

# Competitor Rank Points (Slider)
max_points_val = get_max_rank_points() # Dynamic max points
competitor_points_range = st.sidebar.slider(
    "Competitor Rank Points", # Matches sample UI
    0, max_points_val, (0, max_points_val) # Default range from 0
)
min_points, max_points = competitor_points_range[0], competitor_points_range[1]

# No. Of Competitions Played (Slider)
max_competitions_played_val = get_max_competitions_played() # Dynamic max competitions played
competitions_played_range = st.sidebar.slider(
    "No. Of Competitions Played", # Matches sample UI
    0, max_competitions_played_val, (0, max_competitions_played_val) # Default range from 0
)
min_played, max_played = competitions_played_range[0], competitions_played_range[1]

# --- Main Content Area - Tabbed Interface ---
tab_summary, tab_details, tab_country, tab_leaderboard = st.tabs([
    "Summary Statistics", "Competitor Details Viewer",
    "Country-Wise Analysis", "Leader Board"
]) # Matches sample UI tabs

with tab_summary:
    st.header("Dashboard Overview") # Re-using previous header for consistency

    col1, col2 = st.columns(2) # Two columns as per sample UI layout

    with col1:
        st.subheader("Total Competitors") # Matches sample UI
        total_competitors_query = "SELECT COUNT(competitor_id) FROM Competitors;"
        total_competitors_df = fetch_data(total_competitors_query)
        total_competitors = total_competitors_df.iloc[0,0] if not total_competitors_df.empty else 0
        st.metric("", total_competitors) # Simplified display for metric

    with col2:
        st.subheader("Countries Represented") # Matches sample UI
        countries_represented_query = "SELECT COUNT(DISTINCT country) FROM Competitors WHERE country IS NOT NULL AND country != '';"
        countries_represented_df = fetch_data(countries_represented_query)
        countries_represented = countries_represented_df.iloc[0,0] if not countries_represented_df.empty else 0
        st.metric("", countries_represented) # Simplified display for metric

    st.markdown("---") # Separator as in sample UI

    st.subheader("Highest Points scored by a Competitor") # Matches sample UI
    highest_points_query = """
    SELECT
        c.name AS "Competitor Name",
        MAX(cr.points) AS "Rank Points"
    FROM
        Competitors c
    JOIN
        Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    GROUP BY
        c.name
    ORDER BY
        "Rank Points" DESC
    LIMIT 1;
    """
    highest_points_df = fetch_data(highest_points_query)
    if not highest_points_df.empty:
        st.dataframe(highest_points_df, hide_index=True) # Hide index as in sample
    else:
        st.info("No data for highest points.")

    st.subheader("Highest Competitions played by a Competitor") # Matches sample UI
    highest_played_query = """
    SELECT
        c.name AS "Competitor Name",
        MAX(cr.competitions_played) AS "Competitions Played"
    FROM
        Competitors c
    JOIN
        Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    GROUP BY
        c.name
    ORDER BY
        "Competitions Played" DESC
    LIMIT 1;
    """
    highest_played_df = fetch_data(highest_played_query)
    if not highest_played_df.empty:
        st.dataframe(highest_played_df, hide_index=True) # Hide index as in sample
    else:
        st.info("No data for highest competitions played.")


with tab_details:
    st.header("Competitor Details Viewer")
    st.info("This section will display detailed information for a selected competitor.")
    # Implement search and display logic here using selected_competitor filter
    if selected_competitor != "Choose an option":
        st.write(f"Showing details for: {selected_competitor}")
        competitor_details_query = f"""
        SELECT
            c.name,
            c.country,
            c.country_code,
            cr.rank,
            cr.movement,
            cr.points,
            cr.competitions_played
        FROM
            Competitors c
        JOIN
            Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE
            c.name = %(competitor_name)s
        ORDER BY cr.rank ASC LIMIT 1;
        """
        details_df = fetch_data(competitor_details_query, params={'competitor_name': selected_competitor})
        if not details_df.empty:
            st.dataframe(details_df, use_container_width=True, hide_index=True)
        else:
            st.warning("No details found for this competitor.")
    else:
        st.info("Please select a competitor from the sidebar to view details.")


with tab_country:
    st.header("Country-Wise Analysis")
    st.info("This section will display country-wise analysis, including total competitors and average points.")
    # You can implement queries here, e.g.,
    country_analysis_query = """
    SELECT
        c.country AS "Country",
        COUNT(DISTINCT c.competitor_id) AS "Total Competitors",
        AVG(cr.points) AS "Average Points"
    FROM
        Competitors c
    JOIN
        Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
    GROUP BY
        c.country
    ORDER BY
        "Total Competitors" DESC;
    """
    country_analysis_df = fetch_data(country_analysis_query)
    if not country_analysis_df.empty:
        st.dataframe(country_analysis_df, use_container_width=True)
    else:
        st.info("No country-wise analysis data available.")


with tab_leaderboard:
    st.header("Leader Board")
    st.info("This section will display leaderboards based on rank and points.")

    st.subheader("Top Ranked Competitors")
    # Build the dynamic query for filtered rankings
    leaderboard_query = """
    SELECT
        c.name AS "Competitor Name",
        c.country AS "Country",
        cr.rank AS "Rank",
        cr.points AS "Points",
        cr.movement AS "Movement",
        cr.competitions_played AS "Competitions Played"
    FROM
        Competitor_Rankings cr
    JOIN
        Competitors c ON cr.competitor_id = c.competitor_id
    WHERE cr.rank BETWEEN %(min_rank)s AND %(max_rank)s
    """
    leaderboard_params = {
        'min_rank': min_rank,
        'max_rank': max_rank
    }

    # Apply search filter from sidebar to leaderboard
    if selected_competitor != "Choose an option":
        leaderboard_query += " AND LOWER(c.name) = LOWER(%(selected_competitor_name)s)"
        leaderboard_params['selected_competitor_name'] = selected_competitor
    elif search_competitor_name: # Use the general search input if no specific competitor selected
        leaderboard_query += " AND LOWER(c.name) LIKE LOWER(%(search_name)s)"
        leaderboard_params['search_name'] = f"%{search_competitor_name}%"

    # Apply points filter
    leaderboard_query += " AND cr.points BETWEEN %(min_points)s AND %(max_points)s"
    leaderboard_params['min_points'] = min_points
    leaderboard_params['max_points'] = max_points

    # Apply competitions played filter
    leaderboard_query += " AND cr.competitions_played BETWEEN %(min_played)s AND %(max_played)s"
    leaderboard_params['min_played'] = min_played
    leaderboard_params['max_played'] = max_played


    leaderboard_query += """
    ORDER BY
        cr.rank ASC
    LIMIT 500;
    """ # Limit for display performance

    leaderboard_df = fetch_data(leaderboard_query, params=leaderboard_params)

    if not leaderboard_df.empty:
        st.dataframe(leaderboard_df, use_container_width=True)
    else:
        st.info("No data found for the leaderboard with current filters.")

st.caption("Note: All data displayed is based on available data from the Sportradar API, which may be limited by trial key access. Gender filter is a placeholder as competitor gender is not directly available in current data structure.")