# 🏆 Game Analytics: Unlocking Tennis Data with SportRadar API
The **Tennis Rankings Explorer** project is a comprehensive data engineering and visualization solution built using the **Sportradar API**. It focuses on extracting, storing, analyzing, and presenting data from professional tennis competitions.

## Domain:	
* Sports/Data Analytics
* 
## 📌 Project Goals
* Parse and transform sports competition data.
* Design and maintain a structured SQL database.
* Provide interactive insights through a Streamlit dashboard.

## 🔍 Approach:
### 1️⃣ Data Extraction
* Fetch JSON responses from Sportradar API.
* Parse and flatten nested structures into tabular format.

### 2️⃣ Data Storage
* Design normalized SQL schema.
* Use PostgreSQL or MySQL for persistent data storage.
* Define appropriate data types and primary keys for each table.

### 3️⃣ Data Collection
**From API Endpoints:**
* **Competition Data:**
  * `Categories` Table
  * `Competitions` Table

* **Complexes Data:**
  * `Complexes` Table
  * `Venues` Table

* **Doubles Competitor Rankings:**
  * `Competitor_Rankings` Table
  * `Competitors` Table
  * 
## Data Analysis & Insights

* **Competitions**: Discuss insights like total competitions (6104), distribution by category, top-level competitions, parent-sub competition relationships.
* **Venues**: Discuss insights like total venues (3451), geographical distribution of venues, complexes with multiple venues.
* **Competitors & Rankings**: Discuss insights like total competitors (1000), basic ranking distribution, and any interesting findings from the highest points/competitions played.

## Challenges Faced
* **PostgreSQL Password Reset**: Initial difficulty accessing PostgreSQL due to forgotten password and strict local authentication. This was overcome by temporarily modifying `pg_hba.conf` to allow 'trust' authentication for local connections.
* **Sportradar API Trial Key Limitations & URL Issues**: Encountered `502 Bad Gateway` and `404 Not Found` errors for specific API endpoints with the trial key. This required careful debugging of URL paths (e.g., `trial` segment, `_` vs `-`, `.json` placement, and initial assumption of `year` parameter for rankings).
* **Nested JSON Parsing & Database Insertion**: Faced Python `UnboundLocalError` when handling deeply nested JSON structures from the API and ensuring all `NOT NULL` columns in the database received valid data (converting `None` to empty strings where appropriate).
* **Git Repository Setup**: Experienced common Git setup issues in the Windows terminal, including `Permission denied` warnings (due to incorrect directory for `git init`) and `remote contains work` conflicts (when pushing to a pre-initialized GitHub repository). These were resolved by performing Git operations within the correct project directory, setting a default editor, and executing a `git pull --allow-unrelated-histories` before the final `git push`.

## Future Enhancements
* Implement more interactive filters and advanced charting in Streamlit (e.g., showing trends over time).
* Add detailed competitor profiles with historical performance.
* Incorporate more sophisticated data quality checks.
* Explore additional Sportradar API endpoints (e.g., match results, player statistics).
* Deploy the Streamlit application to a cloud platform (e.g., Streamlit Cloud, Heroku).
