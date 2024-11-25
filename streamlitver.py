import ast
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="dash", layout="wide")

# Initialize Firestore
if not firebase_admin._apps:  # Check if Firebase is not already initialized
    firebase_creds = st.secrets["firebase"]  # Load credentials from Streamlit Secrets
    cred = credentials.Certificate(firebase_creds)  # Use the credentials
    firebase_admin.initialize_app(cred)  # Initialize Firebase app

db = firestore.client()
# Fetch all movie data
movies_ref = db.collection('movies2')
movies = movies_ref.stream()
movie_data = [movie.to_dict() for movie in movies]

# Convert Firestore data to DataFrame
movies_df = pd.DataFrame(movie_data)

# Ensure relevant columns exist
movies_df['release_year'] = pd.to_numeric(movies_df.get('release_year', pd.Series([])), errors='coerce')
movies_df['popularity'] = pd.to_numeric(movies_df.get('popularity', pd.Series([])), errors='coerce')

# Safely parse genres_list
def safe_parse_genres(value):
    try:
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return ast.literal_eval(value)  # Parse as list if formatted like a list
        elif isinstance(value, str) and len(value) > 0:
            return [value]  # Single genre string into list
        elif isinstance(value, list):
            return value  # Already a list
        else:
            return []
    except Exception:
        return []

# Safely parse production_countries
def safe_parse_countries(value):
    try:
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            return ast.literal_eval(value)  # Parse as list if formatted like a list
        elif isinstance(value, str) and len(value) > 0:
            return [value]  # Single country string into list
        elif isinstance(value, list):
            return value  # Already a list
        else:
            return []
    except Exception:
        return []


movies_df['genres_list'] = movies_df['genres_list'].apply(safe_parse_genres)

movies_df['production_countries'] = movies_df['production_countries'].apply(safe_parse_countries)

# # Debug: Show parsed production_countries
# st.write("Sample of Parsed Production Countries")
# st.dataframe(movies_df[['title', 'production_countries']].head())

# Define country mapping for Plotly
country_mapping = {
    # Mapping for countries needing adjustment
    "United States of America": "United States",
    "South Korea": "Korea, Republic of",
    "Congo": "Democratic Republic of the Congo",
    "Lao People's Democratic Republic": "Laos",
    "Syrian Arab Republic": "Syria",
    "Taiwan": "Taiwan, Province of China",
    "Russian Federation": "Russia",
    "Viet Nam": "Vietnam",
    "Palestinian Territory": "Palestine",
    "Northern Ireland": "United Kingdom",
    "Macedonia": "North Macedonia",
    "Brunei Darussalam": "Brunei",
    "Micronesia": "Federated States of Micronesia",
    "Macao": "Macau",
    "Timor-Leste": "Timor-Leste",
    "St. Helena": "Saint Helena",
    "St. Kitts and Nevis": "Saint Kitts and Nevis",
    "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Svalbard & Jan Mayen Islands": "Svalbard and Jan Mayen",
    "South Georgia and the South Sandwich Islands": "South Georgia and the South Sandwich Islands",
    "Antigua and Barbuda": "Antigua and Barbuda",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "Cabo Verde": "Cape Verde",
    "Czechia": "Czech Republic",
    "Eswatini": "Swaziland",
    "Gambia, The": "Gambia",
    "Guinea-Bissau": "Guinea-Bissau",
    "Burma": "Myanmar",
    "Côte d'Ivoire": "Ivory Coast",
    "Bahamas, The": "Bahamas",
    "Gambia, The": "Gambia",

    # Directly recognizable by Plotly
    "Afghanistan": "Afghanistan",
    "Albania": "Albania",
    "Algeria": "Algeria",
    "Andorra": "Andorra",
    "Angola": "Angola",
    "Antarctica": "Antarctica",
    "Argentina": "Argentina",
    "Armenia": "Armenia",
    "Australia": "Australia",
    "Austria": "Austria",
    "Azerbaijan": "Azerbaijan",
    "Bahamas": "Bahamas",
    "Bahrain": "Bahrain",
    "Bangladesh": "Bangladesh",
    "Barbados": "Barbados",
    "Belarus": "Belarus",
    "Belgium": "Belgium",
    "Belize": "Belize",
    "Benin": "Benin",
    "Bhutan": "Bhutan",
    "Bolivia": "Bolivia",
    "Bosnia and Herzegovina": "Bosnia and Herzegovina",
    "Botswana": "Botswana",
    "Brazil": "Brazil",
    "Brunei": "Brunei",
    "Bulgaria": "Bulgaria",
    "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Cambodia": "Cambodia",
    "Cameroon": "Cameroon",
    "Canada": "Canada",
    "Central African Republic": "Central African Republic",
    "Chad": "Chad",
    "Chile": "Chile",
    "China": "China",
    "Colombia": "Colombia",
    "Comoros": "Comoros",
    "Costa Rica": "Costa Rica",
    "Croatia": "Croatia",
    "Cuba": "Cuba",
    "Cyprus": "Cyprus",
    "Czech Republic": "Czech Republic",
    "Denmark": "Denmark",
    "Djibouti": "Djibouti",
    "Dominica": "Dominica",
    "Dominican Republic": "Dominican Republic",
    "Ecuador": "Ecuador",
    "Egypt": "Egypt",
    "El Salvador": "El Salvador",
    "Equatorial Guinea": "Equatorial Guinea",
    "Eritrea": "Eritrea",
    "Estonia": "Estonia",
    "Eswatini": "Swaziland",
    "Ethiopia": "Ethiopia",
    "Fiji": "Fiji",
    "Finland": "Finland",
    "France": "France",
    "Gabon": "Gabon",
    "Gambia": "Gambia",
    "Georgia": "Georgia",
    "Germany": "Germany",
    "Ghana": "Ghana",
    "Greece": "Greece",
    "Grenada": "Grenada",
    "Guatemala": "Guatemala",
    "Guinea": "Guinea",
    "Guinea-Bissau": "Guinea-Bissau",
    "Guyana": "Guyana",
    "Haiti": "Haiti",
    "Honduras": "Honduras",
    "Hungary": "Hungary",
    "Iceland": "Iceland",
    "India": "India",
    "Indonesia": "Indonesia",
    "Iran": "Iran",
    "Iraq": "Iraq",
    "Ireland": "Ireland",
    "Israel": "Israel",
    "Italy": "Italy",
    "Jamaica": "Jamaica",
    "Japan": "Japan",
    "Jordan": "Jordan",
    "Kazakhstan": "Kazakhstan",
    "Kenya": "Kenya",
    "Kiribati": "Kiribati",
    "Kosovo": "Kosovo",
    "Kuwait": "Kuwait",
    "Kyrgyzstan": "Kyrgyzstan",
    "Laos": "Laos",
    "Latvia": "Latvia",
    "Lebanon": "Lebanon",
    "Lesotho": "Lesotho",
    "Liberia": "Liberia",
    "Libya": "Libya",
    "Liechtenstein": "Liechtenstein",
    "Lithuania": "Lithuania",
    "Luxembourg": "Luxembourg",
    "Madagascar": "Madagascar",
    "Malawi": "Malawi",
    "Malaysia": "Malaysia",
    "Maldives": "Maldives",
    "Mali": "Mali",
    "Malta": "Malta",
    "Marshall Islands": "Marshall Islands",
    "Mauritania": "Mauritania",
    "Mauritius": "Mauritius",
    "Mexico": "Mexico",
    "Micronesia": "Federated States of Micronesia",
    "Moldova": "Moldova",
    "Monaco": "Monaco",
    "Mongolia": "Mongolia",
    "Montenegro": "Montenegro",
    "Montserrat": "Montserrat",
    "Morocco": "Morocco",
    "Mozambique": "Mozambique",
    "Myanmar": "Myanmar",
    "Namibia": "Namibia",
    "Nauru": "Nauru",
    "Nepal": "Nepal",
    "Netherlands": "Netherlands",
    "New Zealand": "New Zealand",
    "Nicaragua": "Nicaragua",
    "Niger": "Niger",
    "Nigeria": "Nigeria",
    "North Macedonia": "North Macedonia",
    "Norway": "Norway",
    "Oman": "Oman",
    "Pakistan": "Pakistan",
    "Palau": "Palau",
    "Palestine": "Palestine",
    "Panama": "Panama",
    "Papua New Guinea": "Papua New Guinea",
    "Paraguay": "Paraguay",
    "Peru": "Peru",
    "Philippines": "Philippines",
    "Poland": "Poland",
    "Portugal": "Portugal",
    "Qatar": "Qatar",
    "Romania": "Romania",
    "Russia": "Russia",
    "Rwanda": "Rwanda",
    "Saint Kitts and Nevis": "Saint Kitts and Nevis",
    "Saint Lucia": "Saint Lucia",
    "Saint Vincent and the Grenadines": "Saint Vincent and the Grenadines",
    "Samoa": "Samoa",
    "San Marino": "San Marino",
    "Sao Tome and Principe": "Sao Tome and Principe",
    "Saudi Arabia": "Saudi Arabia",
    "Senegal": "Senegal",
    "Serbia": "Serbia",
    "Seychelles": "Seychelles",
    "Sierra Leone": "Sierra Leone",
    "Singapore": "Singapore",
    "Slovakia": "Slovakia",
    "Slovenia": "Slovenia",
    "Solomon Islands": "Solomon Islands",
    "Somalia": "Somalia",
    "South Africa": "South Africa",
    "South Korea": "Korea, Republic of",
    "South Sudan": "South Sudan",
    "Spain": "Spain",
    "Sri Lanka": "Sri Lanka",
    "Sudan": "Sudan",
    "Suriname": "Suriname",
    "Swaziland": "Swaziland",
    "Sweden": "Sweden",
    "Switzerland": "Switzerland",
    "Syria": "Syria",
    "Taiwan": "Taiwan",
    "Tajikistan": "Tajikistan",
    "Tanzania": "Tanzania",
    "Thailand": "Thailand",
    "Togo": "Togo",
    "Tonga": "Tonga",
    "Trinidad and Tobago": "Trinidad and Tobago",
    "Tunisia": "Tunisia",
    "Turkey": "Turkey",
    "Turkmenistan": "Turkmenistan",
    "Tuvalu": "Tuvalu",
    "Uganda": "Uganda",
    "Ukraine": "Ukraine",
    "United Arab Emirates": "United Arab Emirates",
    "United Kingdom": "United Kingdom",
    "United States": "United States",
    "Uruguay": "Uruguay",
    "Uzbekistan": "Uzbekistan",
    "Vanuatu": "Vanuatu",
    "Vatican City": "Vatican City",
    "Venezuela": "Venezuela",
    "Vietnam": "Vietnam",
    "Yemen": "Yemen",
    "Zambia": "Zambia",
    "Zimbabwe": "Zimbabwe",
}

def map_country_names(countries):
    if not countries:  # Handle empty or None values
        return []
    return [country_mapping.get(country.strip(), country.strip()) for country in countries if isinstance(country, str)]

# Map production countries to Plotly-compatible names
movies_df['mapped_production_countries'] = movies_df['production_countries'].apply(map_country_names)

# Filter out rows with empty mapped production countries
movies_df = movies_df[movies_df['mapped_production_countries'].apply(lambda x: isinstance(x, list) and len(x) > 0)]

# # Debug: Show mapped production_countries
# st.write("Sample of Mapped Production Countries")
# st.dataframe(movies_df[['title', 'mapped_production_countries']].head())

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Page 1", "Page 2", "Page 3"])

if page == "Page 1":
    # Page 1: Movie Dashboard
    st.title("Movie Dashboard")

    # Initialize session state for lists
    if "to_watch" not in st.session_state:
        st.session_state.to_watch = []
    if "watched" not in st.session_state:
        st.session_state.watched = []

    # Create a three-column layout: Bar chart (left), Movie information (center), Search/List (right)
    col1, col2, col3 = st.columns(3)

    # Bar Chart Section (Left Column)
    with col1:
        st.subheader("Top 5 Movies by Popularity")

        # Slider and Dropdown for Filtering
        year = st.slider("Filter by Year", min_value=int(movies_df['release_year'].min()), max_value=int(movies_df['release_year'].max()), value=int(movies_df['release_year'].max()))
        genres = st.selectbox("Filter by Genre", options=["All"] + sorted(set(genre for genres in movies_df['genres_list'].dropna() for genre in genres)))

        # Filter DataFrame based on user input
        filtered_df = movies_df[movies_df['release_year'] == year]
        if genres != "All":
            filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: genres in x if isinstance(x, list) else False)]

        # Sort by popularity and get top 5
        top_movies = filtered_df.sort_values(by='popularity', ascending=False).head(5)

        # Display Bar Chart using Plotly
        if not top_movies.empty:
            fig = px.bar(
                top_movies,
                x='popularity',
                y='title',
                orientation='h',
                title=f"Top 5 Movies in {year} (Genre: {genres})",
                labels={'popularity': 'Popularity', 'title': 'Movie Title'},
                hover_data={'title': True, 'popularity': True}
            )
            fig.update_layout(
                yaxis=dict(
                    tickfont=dict(size=10),
                    categoryorder="total ascending",
                ),
                margin=dict(l=120, r=10, t=50, b=20),
                height=300
            )
            fig.update_traces(marker_color='skyblue', marker_line_width=1.5)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No movies found for the selected year and genre.")

    # Movie Information Section (Center Column)
    with col2:
        st.subheader("Movie Information")

        # Dropdown for Movie Selection
        movie_titles = movies_df['title'].tolist()
        selected_movie = st.selectbox("Choose a Movie", movie_titles)

        # Display Selected Movie Information
        if selected_movie:
            movie_details = movies_df[movies_df['title'] == selected_movie].iloc[0].to_dict()

            st.markdown(f"**Release Date:** {movie_details.get('release_date', 'N/A')}")
            st.markdown(f"**Popularity:** {movie_details.get('popularity', 'N/A')}")
            st.markdown(f"**Runtime:** {movie_details.get('runtime', 'N/A')} minutes")

            genres_list = movie_details.get('genres_list', [])
            st.markdown(f"**Genres:** {', '.join(genres_list) if isinstance(genres_list, list) else 'Unknown'}")


            st.markdown(f"**Status:** {movie_details.get('status', 'Unknown')}")

            st.markdown("---")
            st.subheader("Overview")
            st.text_area("Overview", movie_details.get('overview', 'No overview available'), height=200)

    # Search Bar and Lists Section (Right Column)
    with col3:
        st.subheader("Search and Manage Lists")
        
        # Auto-suggest search bar using selectbox
        search_query = st.text_input("Search for a movie or show")
        if search_query:
            # Dynamically filter movies based on input
            suggestions = movies_df[movies_df['title'].str.contains(search_query, case=False, na=False)]['title'].tolist()
            if suggestions:
                selected_suggestion = st.selectbox("Suggestions:", suggestions)
            else:
                st.write("No matches found.")
        else:
            selected_suggestion = None

        # Add the selected suggestion to lists
        if selected_suggestion:
            st.write(f"Selected Movie: {selected_suggestion}")
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button(f"Add to To Watch: {selected_suggestion}"):
                    if selected_suggestion not in st.session_state.to_watch:
                        st.session_state.to_watch.append(selected_suggestion)
            with col_b:
                if st.button(f"Add to Watched: {selected_suggestion}"):
                    if selected_suggestion not in st.session_state.watched:
                        st.session_state.watched.append(selected_suggestion)

        # Display "To Watch" and "Watched" Lists
        st.write("### To Watch List")
        if st.session_state.to_watch:
            for item in st.session_state.to_watch:
                st.write(f"- {item}")
        else:
            st.write("Your To Watch list is empty.")

        st.write("### Watched List")
        if st.session_state.watched:
            for item in st.session_state.watched:
                st.write(f"- {item}")
        else:
            st.write("Your Watched list is empty.")


elif page == "Page 2":
    st.title("Production Countries Overview")

    # First row: Production Countries Map and Movies by Country
    col1, col2 = st.columns([2, 1])  # Adjust the width ratio as needed

    # Prepare data for the map and charts
    country_data = []
    for _, row in movies_df.iterrows():
        # Split multiple countries into individual entries
        for country in row['mapped_production_countries']:
            separated_countries = [c.strip() for c in country.split(",") if c.strip()]
            for separated_country in separated_countries:
                country_data.append({
                    'Country': separated_country,
                    'Movie Title': row['title'],
                    'Release Year': row['release_year'],
                    'Popularity': row['popularity']
                })

    if not country_data:
        st.write("No production country data available.")
    else:
        # Convert to DataFrame
        country_df = pd.DataFrame(country_data)

        # Count occurrences of each country
        country_counts = country_df['Country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Count']

        # Calculate percentage for each country
        country_counts['Percentage'] = (country_counts['Count'] / country_counts['Count'].sum()) * 100

        # Prepare data for the line chart
        release_year_data = movies_df.groupby('release_year').size().reset_index(name='Count')

        # Column 1: Display the geographical scatter map
        with col1:
            st.subheader("Production Countries Map")
            fig = px.scatter_geo(
                country_counts,
                locations="Country",
                locationmode="country names",
                size="Count",
                title="Production Countries",
                projection="natural earth",
            )
            fig.update_traces(marker=dict(color="blue", opacity=0.7))
            st.plotly_chart(fig, use_container_width=True)

        # Column 2: Display 5 random movies by country
        with col2:
            st.subheader("Movies by Country")
            selected_country = st.selectbox(
                "Select a country to view movies:",
                country_df['Country'].unique(),
                help="Choose a country to view movies produced there.",
            )
            if selected_country:
                # Filter and randomly pick up to 5 movies
                movies_from_country = country_df[country_df['Country'] == selected_country]
                st.write(f"Movies from {selected_country}:")
                import random
                if len(movies_from_country) > 5:
                    movies_from_country = movies_from_country.sample(5)  # Pick 5 random movies
                for _, movie in movies_from_country.iterrows():
                    st.write(f"- **{movie['Movie Title']}** (Year: {movie['Release Year']}, Popularity: {movie['Popularity']:.2f})")

         # Prepare data for the line chart
        release_year_data = movies_df.groupby('release_year').size().reset_index(name='Count')
        release_year_data['release_year'] = release_year_data['release_year'].astype(int)  # Ensure release_year is integer

        # Second row: Pie chart and line chart
        col3, col4 = st.columns([1, 1])  # Split the row into two equal-width columns
        with col3:
            st.subheader("Production Country Distribution (Pie Chart)")
            pie_fig = px.pie(
                country_counts,
                values='Percentage',
                names='Country',
                title="Production Country Percentage",
                hover_data=['Count'],
                labels={'Percentage': 'Percentage (%)'},
            )
            pie_fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(pie_fig, use_container_width=True)

        with col4:
            st.subheader("Number of Movies Released Over Time (Line Chart)")
            line_fig = px.line(
                release_year_data,
                x='release_year',
                y='Count',
                title="Movies Released Per Year",
                labels={'release_year': 'Year', 'Count': 'Number of Movies'},
                markers=True
            )
            line_fig.update_layout(
                xaxis=dict(
                    title='Release Year',
                    tickmode='linear'  # Ensure only integer values appear
                ),
                yaxis=dict(title='Number of Movies'),
                margin=dict(l=0, r=0, t=30, b=50),
            )
            st.plotly_chart(line_fig, use_container_width=True)

elif page == "Page 3":
    st.title("Actors and Their Movies")

    # Prepare data for actor search
    def parse_cast_list(cast_str):
        try:
            # Convert the cast list from string to a Python list
            return ast.literal_eval(cast_str) if isinstance(cast_str, str) else []
        except:
            return []

    # Apply the parsing function to the 'Cast_list' column
    movies_df['Cast_list'] = movies_df['Cast_list'].apply(parse_cast_list)

    # Create a search bar for actor names
    st.subheader("Search for an Actor")
    actor_name = st.text_input("Enter the name of an actor:", help="Type the name of an actor to see their movies.")

    if actor_name:
        # Convert user input to lowercase
        actor_name_lower = actor_name.lower()

        # Filter movies where the actor appears in the Cast_list (case-insensitive)
        movies_with_actor = movies_df[movies_df['Cast_list'].apply(
            lambda x: any(actor_name_lower == actor.lower() for actor in x) if isinstance(x, list) else False
        )]

        if not movies_with_actor.empty:
            st.write(f"Movies featuring **{actor_name}**:")
            for _, movie in movies_with_actor.iterrows():
                st.write(f"- **{movie['title']}** (Year: {movie['release_year']}, Popularity: {movie['popularity']:.2f})")
        else:
            st.write(f"No movies found featuring **{actor_name}**.")
    else:
        st.write("Enter an actor's name in the search bar above to find their movies.")
