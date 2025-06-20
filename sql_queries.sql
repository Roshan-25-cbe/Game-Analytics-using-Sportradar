---Database : game_analytics_db

---Categories table---

CREATE TABLE Categories (
category_id VARCHAR(50) PRIMARY KEY,
category_name VARCHAR(100) NOT NULL
);

---Competitions table---

CREATE TABLE Competitions (
competition_id VARCHAR(50) PRIMARY KEY,
competition_name VARCHAR(100) NOT NULL,
parent_id VARCHAR(50) NULL, -- Corrected: Use NULL (or simply omit NOT NULL)
type VARCHAR(20) NOT NULL, -- e.g., 'singles', 'doubles'
gender VARCHAR(10) NOT NULL, -- e.g., 'men', 'women'
category_id VARCHAR(50) REFERENCES Categories(category_id) -- Foreign Key linking to Categories table
);

---Complex Table---

CREATE TABLE Complexes (
complex_id VARCHAR(50) PRIMARY KEY,
complex_name VARCHAR(100) NOT NULL
);

---Venues Table---

CREATE TABLE Venues (
venue_id VARCHAR(50) PRIMARY KEY,
venue_name VARCHAR(100) NOT NULL,
city_name VARCHAR(100) NOT NULL,
country_name VARCHAR(100) NOT NULL,
country_code CHAR(3) NOT NULL,
timezone VARCHAR(100) NOT NULL,
complex_id VARCHAR(50) REFERENCES Complexes(complex_id) -- Foreign Key linking to Complexes table
);

---Competitors Rankings Table---

CREATE TABLE Competitor_Rankings (
rank_id SERIAL PRIMARY KEY, -- PostgreSQL uses SERIAL for auto-incrementing primary keys
rank INT NOT NULL,
movement INT NOT NULL,
points INT NOT NULL,
competitions_played INT NOT NULL
);

---Competitors Table---

CREATE TABLE Competitors (
competitor_id VARCHAR(50) PRIMARY KEY,
name VARCHAR(100) NOT NULL,
country VARCHAR(100) NOT NULL,
country_code CHAR(3) NOT NULL,
abbreviation VARCHAR(10) NOT NULL
);


---Data Analysis---

---Section 1: Queries related to Competitions and Categories ----

--Query 1: List all competitions along with their category name 

SELECT
    c.competition_name,
    cat.category_name
FROM
    Competitions c
JOIN
    Categories cat ON c.category_id = cat.category_id;


---Query 2: Count the number of competitions in each category 


SELECT
    cat.category_name,
    COUNT(c.competition_id) AS number_of_competitions
FROM
    Competitions c
JOIN
    Categories cat ON c.category_id = cat.category_id
GROUP BY
    cat.category_name
ORDER BY
    number_of_competitions DESC;


---Query 3: Find all competitions of type 'doubles' 

SELECT
    competition_name,
    type,
    gender
FROM
    Competitions
WHERE
    type = 'doubles';


---Query 4: Get competitions that belong to a specific category (e.g., ITF Men) 

SELECT
    c.competition_name,
    cat.category_name
FROM
    Competitions c
JOIN
    Categories cat ON c.category_id = cat.category_id
WHERE
    cat.category_name = 'ITF Men'; -- You can change 'ITF Men' to any category name present in your database


---Query 5: Identify parent competitions and their sub-competitions 

SELECT
    p.competition_name AS parent_competition,
    s.competition_name AS sub_competition
FROM
    Competitions s
JOIN
    Competitions p ON s.parent_id = p.competition_id
ORDER BY
    parent_competition, sub_competition;


---Query 6: Analyze the distribution of competition types by category 

SELECT
    cat.category_name,
    c.type,
    COUNT(c.competition_id) AS count
FROM
    Competitions c
JOIN
    Categories cat ON c.category_id = cat.category_id
GROUP BY
    cat.category_name, c.type
ORDER BY
    cat.category_name, count DESC;


---Query 7: List all competitions with no parent (top-level competitions) 

SELECT
    competition_name,
    type,
    gender
FROM
    Competitions
WHERE
    parent_id IS NULL
ORDER BY
    competition_name;


---Section 2: Queries related to Complexes and Venues


---Query 1: List all venues along with their associated complex name 

SELECT
    v.venue_name,
    c.complex_name
FROM
    Venues v
JOIN
    Complexes c ON v.complex_id = c.complex_id
ORDER BY
    v.venue_name;


---Query 2: Count the number of venues in each complex 

SELECT
    c.complex_name,
    COUNT(v.venue_id) AS number_of_venues
FROM
    Venues v
JOIN
    Complexes c ON v.complex_id = c.complex_id
GROUP BY
    c.complex_name
ORDER BY
    number_of_venues DESC;


---Query 3: Get details of venues in a specific country (e.g., Chile) (Note: You can change 'Chile' to any country name present in your Venues table.)

SELECT
    venue_name,
    city_name,
    country_name
FROM
    Venues
WHERE
    country_name = 'Chile'; -- You can change 'Chile' to another country in your data


---Query 4: Identify all venues and their timezones 

SELECT
    venue_name,
    timezone
FROM
    Venues
ORDER BY
    venue_name;


---Query 5: Find complexes that have more than one venue 

SELECT
    c.complex_name,
    COUNT(v.venue_id) AS number_of_venues
FROM
    Complexes c
JOIN
    Venues v ON c.complex_id = v.complex_id
GROUP BY
    c.complex_name
HAVING
    COUNT(v.venue_id) > 1
ORDER BY
    number_of_venues DESC;


---Query 6: List venues grouped by country 

SELECT
    country_name,
    COUNT(venue_id) AS number_of_venues
FROM
    Venues
GROUP BY
    country_name
ORDER BY
    number_of_venues DESC;


---Query 7: Find all venues for a specific complex (e.g., Nacional) (Note: You can change 'Nacional' to a complex name found in your Complexes table.)

SELECT
    v.venue_name,
    v.city_name,
    c.complex_name
FROM
    Venues v
JOIN
    Complexes c ON v.complex_id = c.complex_id
WHERE
    c.complex_name = 'Nacional'; -- You can change 'Nacional' to another complex name


---Section 3: Queries related to Competitors and Competitor Rankings


---Query 1: Get all competitors with their rank and points.

SELECT
    c.name,
    cr.rank,
    cr.points
FROM
    Competitors c
JOIN
    Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
ORDER BY
    cr.rank;


---Query 2: Find competitors ranked in the top 5.

SELECT
    c.name,
    cr.rank,
    cr.points
FROM
    Competitors c
JOIN
    Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE
    cr.rank <= 5
ORDER BY
    cr.rank;


---Query 3: List competitors with no rank movement (stable rank).

SELECT
    c.name,
    cr.rank,
    cr.movement
FROM
    Competitors c
JOIN
    Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE
    cr.movement = 0
ORDER BY
    c.name;


---Query 4: Get the total points of competitors from a specific country (e.g., Croatia).
---(Note: You can change 'Croatia' to another country code or name if you find one in your Competitors table, but it's likely empty.)

SELECT
    c.country_name,
    SUM(cr.points) AS total_points
FROM
    Competitors c
JOIN
    Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE
    c.country_name = 'Croatia' -- Or 'CRO' if you use country_code and it's present
GROUP BY
    c.country_name;


---Query 5: Count the number of competitors per country.

SELECT
    country_name,
    COUNT(competitor_id) AS number_of_competitors
FROM
    Competitors
GROUP BY
    country_name
ORDER BY
    number_of_competitors DESC;


---Query 6: Find competitors with the highest points in the current week.
---(Note: This query assumes 'current week' implies looking for the maximum points across all stored rankings. If you had weekly data, you'd filter by week. Given current data, this just finds the max points in the table.)

SELECT
    c.name,
    cr.points
FROM
    Competitors c
JOIN
    Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE
    cr.points = (SELECT MAX(points) FROM Competitor_Rankings);

