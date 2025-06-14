import requests
import psycopg2
import json

# --- Configuration ---
# Your Sportradar API Key
API_KEY = 'wS1JVuz64xZPGUAVKeEBWLtTO6zSIV4AbRnTCo2J'

# PostgreSQL Database Configuration
DB_HOST = "localhost"
DB_NAME = "game_analytics_db"
DB_USER = "postgres"
DB_PASSWORD = "Roshan@2025" # !! MAKE SURE THIS IS YOUR CORRECT POSTGRES PASSWORD !!

# --- Database Connection Functions ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Database connection established successfully.")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()
        print("Database connection closed.")

# --- Data Collection and Insertion Functions ---

def collect_and_store_competition_data():
    """Collects and stores competition and category data."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return

        cur = conn.cursor()

        # Sportradar API Base URL for Tennis Competitions (Updated for trial key compatibility)
        COMPETITIONS_BASE_URL = "https://api.sportradar.com/tennis/trial/v3/en/competitions"

        api_url = f"{COMPETITIONS_BASE_URL}.json?api_key={API_KEY}"
        print(f"Fetching competition data from: {api_url}")

        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()

        if 'competitions' in data and isinstance(data['competitions'], list):
            for competition in data['competitions']:
                # --- Insert into Categories Table ---
                category_id = competition['category']['id']
                category_name = competition['category']['name']
                
                cur.execute(
                    """
                    INSERT INTO Categories (category_id, category_name)
                    VALUES (%s, %s)
                    ON CONFLICT (category_id) DO NOTHING;
                    """,
                    (category_id, category_name)
                )

                # --- Insert into Competitions Table ---
                competition_id = competition['id']
                competition_name = competition['name']
                parent_id = competition.get('parent_id')
                competition_type = competition.get('type')
                gender = competition.get('gender')

                cur.execute(
                    """
                    INSERT INTO Competitions (competition_id, competition_name, parent_id, type, gender, category_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (competition_id) DO NOTHING;
                    """,
                    (competition_id, competition_name, parent_id, competition_type, gender, category_id)
                )
            conn.commit()
            print(f"Successfully inserted {len(data['competitions'])} competitions and their categories.")
        else:
            print("No 'competitions' key found or it's not a list in the API response for competitions.")

    except requests.exceptions.RequestException as e:
        print(f"API request for competitions failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for competitions: {e}")
    except psycopg2.Error as e:
        print(f"Database error during competitions insertion: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred for competitions: {e}")
    finally:
        close_db_connection(conn)

def collect_and_store_complexes_data():
    """Collects and stores complexes and venue data."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return

        cur = conn.cursor()

        # Sportradar API Base URL for Tennis Complexes (Updated for trial key compatibility)
        COMPLEXES_BASE_URL = "https://api.sportradar.com/tennis/trial/v3/en/complexes"

        api_url = f"{COMPLEXES_BASE_URL}.json?api_key={API_KEY}"
        print(f"Fetching complexes data from: {api_url}")

        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'complexes' in data and isinstance(data['complexes'], list):
            for complex_data in data['complexes']:
                # --- Insert into Complexes Table ---
                complex_id = complex_data['id']
                complex_name = complex_data['name']

                cur.execute(
                    """
                    INSERT INTO Complexes (complex_id, complex_name)
                    VALUES (%s, %s)
                    ON CONFLICT (complex_id) DO NOTHING;
                    """,
                    (complex_id, complex_name)
                )

                # --- Insert into Venues Table (if venues exist for this complex) ---
                if 'venues' in complex_data and isinstance(complex_data['venues'], list):
                    for venue_data in complex_data['venues']:
                        venue_id = venue_data['id']
                        venue_name = venue_data['name']
                        city_name = venue_data.get('city_name')
                        country_name = venue_data.get('country_name')
                        country_code = venue_data.get('country_code')
                        timezone = venue_data.get('timezone')
                        venue_complex_id = complex_id 

                        # Ensure NOT NULL columns have values, even if empty string from API
                        city_name = city_name if city_name is not None else ''
                        country_name = country_name if country_name is not None else ''
                        country_code = country_code if country_code is not None else ''
                        timezone = timezone if timezone is not None else ''

                        cur.execute(
                            """
                            INSERT INTO Venues (venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (venue_id) DO NOTHING;
                            """,
                            (venue_id, venue_name, city_name, country_name, country_code, timezone, venue_complex_id)
                        )
            conn.commit()
            print(f"Successfully inserted {len(data['complexes'])} complexes and their associated venues.")
        else:
            print("No 'complexes' key found or it's not a list in the API response for complexes.")

    except requests.exceptions.RequestException as e:
        print(f"API request for complexes failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for complexes: {e}")
    except psycopg2.Error as e:
        print(f"Database error during complexes insertion: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred for complexes: {e}")
    finally:
        close_db_connection(conn)


def collect_and_store_competitor_rankings_data():
    """Collects and stores competitor rankings and competitor details."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return

        cur = conn.cursor()

        # Sportradar API Base URL for Doubles Competitor Rankings (Corrected based on successful curl test)
        RANKINGS_BASE_URL = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings"

        api_url = f"{RANKINGS_BASE_URL}.json?api_key={API_KEY}"
        print(f"Fetching competitor rankings data from: {api_url}")

        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'rankings' in data and isinstance(data['rankings'], list):
            total_rankings_inserted = 0
            for ranking_group in data['rankings']: # Loop through ATP, WTA, etc. ranking groups
                if 'competitor_rankings' in ranking_group and isinstance(ranking_group['competitor_rankings'], list):
                    for ranking_data in ranking_group['competitor_rankings']: # Loop through individual competitor rankings
                        # Initialize competitor_id to None before any conditional assignment
                        competitor_id = None 

                        # --- Extract Competitor Info and Insert into Competitors Table ---
                        competitor_info = ranking_data.get('competitor')
                        if competitor_info:
                            competitor_id = competitor_info.get('id')
                            name = competitor_info.get('name')
                            country = competitor_info.get('country')
                            country_code = competitor_info.get('country_code')
                            abbreviation = competitor_info.get('abbreviation')

                            # Ensure NOT NULL columns have values for Competitors table
                            name = name if name is not None else ''
                            country = country if country is not None else ''
                            country_code = country_code if country_code is not None else ''
                            abbreviation = abbreviation if abbreviation is not None else ''

                            if competitor_id: # Only insert competitor if ID exists
                                cur.execute(
                                    """
                                    INSERT INTO Competitors (competitor_id, name, country, country_code, abbreviation)
                                    VALUES (%s, %s, %s, %s, %s)
                                    ON CONFLICT (competitor_id) DO NOTHING;
                                    """,
                                    (competitor_id, name, country, country_code, abbreviation)
                                )

                        # --- Insert into Competitor_Rankings Table ---
                        # Only insert ranking if we have a valid competitor_id and essential ranking data.
                        rank = ranking_data.get('rank')
                        movement = ranking_data.get('movement')
                        points = ranking_data.get('points')
                        competitions_played = ranking_data.get('competitions_played')

                        if competitor_id and rank is not None and movement is not None and points is not None and competitions_played is not None:
                            cur.execute(
                                """
                                INSERT INTO Competitor_Rankings (rank, movement, points, competitions_played, competitor_id)
                                VALUES (%s, %s, %s, %s, %s);
                                """,
                                (rank, movement, points, competitions_played, competitor_id)
                            )
                            total_rankings_inserted += 1
                        else:
                            # Print a message if a ranking entry is skipped due to missing critical data
                            # Use .get('id', 'N/A') to safely print ID if present, otherwise 'N/A'
                            print(f"Skipping ranking entry due to missing competitor_id or essential ranking data: Competitor ID: {ranking_data.get('competitor', {}).get('id', 'N/A')}, Rank: {ranking_data.get('rank', 'N/A')}")

            conn.commit()
            print(f"Successfully inserted {total_rankings_inserted} competitor rankings and their details.")
        else:
            print("No 'rankings' key found or it's not a list in the API response for rankings.")

    except requests.exceptions.RequestException as e:
        print(f"API request for rankings failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON for rankings: {e}")
    except psycopg2.Error as e:
        print(f"Database error during rankings insertion: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred for rankings: {e}")
    finally:
        close_db_connection(conn)


# --- Main execution ---
if __name__ == "__main__":
    collect_and_store_competition_data()
    collect_and_store_complexes_data()
    collect_and_store_competitor_rankings_data() # Call this function to get rankings data