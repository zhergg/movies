import ast
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="dash", layout="wide")

# Initialize Firestore
if not firebase_admin._apps:  # Ensure Firebase is initialized only once
    firebase_creds = dict(st.secrets["firebase"])  # Convert secrets to a dictionary
    cred = credentials.Certificate(firebase_creds)  # Use the dictionary directly
    firebase_admin.initialize_app(cred)  # Initialize Firebase app

# Firestore client
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
    if not countries:
        return []
    return [country_mapping.get(country.strip(), country.strip()) for country in countries if isinstance(country, str)]

movies_df['mapped_production_countries'] = movies_df['production_countries'].apply(map_country_names)
movies_df = movies_df[movies_df['mapped_production_countries'].apply(lambda x: isinstance(x, list) and len(x) > 0)]

# Ensure numeric values
movies_df['release_year'] = pd.to_numeric(movies_df.get('release_year', pd.Series([])), errors='coerce')
movies_df['popularity'] = pd.to_numeric(movies_df.get('popularity', pd.Series([])), errors='coerce')

# Authentication
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

def register_user(username, password):
    user_ref = db.collection('users').document(username)
    if user_ref.get().exists:
        st.error("Username already exists. Choose a different username.")
    else:
        user_ref.set({"password": password, "to_watch": [], "favorites": []})
        st.success("Registration successful! You can now log in.")

def login_user(username, password):
    user_ref = db.collection('users').document(username)
    user_doc = user_ref.get()
    if user_doc.exists and user_doc.to_dict().get("password") == password:
        st.success("Login successful!")
        return username
    else:
        st.error("Invalid username or password.")
        return None

# Sidebar: Login/Registration
if st.session_state.logged_in_user:
    username = st.session_state.logged_in_user
    st.sidebar.write(f"Logged in as: {username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in_user = None
else:
    st.sidebar.write("Please log in or register.")
    auth_option = st.sidebar.radio("Choose an option:", ["Login", "Register"])
    if auth_option == "Register":
        reg_username = st.sidebar.text_input("Username (Register)", key="reg_username")
        reg_password = st.sidebar.text_input("Password (Register)", type="password", key="reg_password")
        if st.sidebar.button("Register"):
            if reg_username and reg_password:
                register_user(reg_username, reg_password)
            else:
                st.error("Please provide both username and password.")
    elif auth_option == "Login":
        login_username = st.sidebar.text_input("Username (Login)", key="login_username")
        login_password = st.sidebar.text_input("Password (Login)", type="password", key="login_password")
        if st.sidebar.button("Login"):
            if login_username and login_password:
                logged_in_user = login_user(login_username, login_password)
                if logged_in_user:
                    st.session_state.logged_in_user = logged_in_user
            else:
                st.error("Please provide both username and password.")

# Main page content
if st.session_state.logged_in_user:
    page = st.sidebar.radio("Go to", ["Page 1", "Page 2", "Page 3"])

    if page == "Page 1":
        st.title("Page 1: Movie Dashboard")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Top 5 Movies by Popularity")
            year = st.slider("Filter by Year", int(movies_df['release_year'].min()), int(movies_df['release_year'].max()), int(movies_df['release_year'].max()))
            genre = st.selectbox("Filter by Genre", ["All"] + list(set(genre for sublist in movies_df['genres_list'].dropna() for genre in sublist)))
            filtered_df = movies_df[movies_df['release_year'] == year]
            if genre != "All":
                filtered_df = filtered_df[filtered_df['genres_list'].apply(lambda x: genre in x if isinstance(x, list) else False)]
            top_movies = filtered_df.sort_values(by="popularity", ascending=False).head(5)
            fig = px.bar(top_movies, x="popularity", y="title", orientation="h", labels={"popularity": "Popularity", "title": "Title"})
            st.plotly_chart(fig, use_container_width=True)

            # Add the text below the chart
            st.write("The chart shows the top 5 most popular movies of 2023 across all genres. "
                    "**Blue Beetle** is the most popular, followed by **Gran Turismo**. Other movies include "
                    "**The Nun II**, **Talk to Me**, and **Saw X** in decreasing popularity. Popularity is "
                    "likely based on audience metrics.")

        with col2:
            st.subheader("Movie Information")
            selected_movie = st.selectbox("Select a Movie", movies_df['title'])
            movie_details = movies_df[movies_df['title'] == selected_movie].iloc[0]
            st.markdown(f"**Release Date:** {movie_details['release_date']}")
            st.markdown(f"**Popularity:** {movie_details['popularity']}")
            st.markdown(f"**Genres:** {', '.join(movie_details['genres_list'])}")
            st.markdown(f"**Overview:** {movie_details['overview']}")

            st.write("This shows the Movie information section for the dashboard."
                     "The user can type the name of a move or show or select one from the dropdown."
                     "Once selected, information regarding the title that the user has selected will be shown.")

        with col3:
            st.subheader("Manage Lists")
            user_ref = db.collection('users').document(st.session_state.logged_in_user)
            user_data = user_ref.get().to_dict()
            to_watch = user_data.get("to_watch", [])
            favorites = user_data.get("favorites", [])
            movie_to_add = st.selectbox("Add Movie to List", movies_df['title'])
            if st.button("Add to To-Watch List"):
                if movie_to_add not in to_watch:
                    to_watch.append(movie_to_add)
                    user_ref.update({"to_watch": to_watch})
                    st.success(f"Added {movie_to_add} to To-Watch List.")
            if st.button("Add to Favorites"):
                if movie_to_add not in favorites:
                    favorites.append(movie_to_add)
                    user_ref.update({"favorites": favorites})
                    st.success(f"Added {movie_to_add} to Favorites List.")

            st.write("### To-Watch List")
            for movie in to_watch:
                st.write(f"- {movie}")
            st.write("### Favorites List")
            for movie in favorites:
                st.write(f"- {movie}")

            st.write("This section shows the 'To watch' list and 'Favourites' list."
                     "The user is searches for a movie and once the user found the movie "
                     "they are searching for, they can either add it to their faviourites list or to watch list")

    elif page == "Page 2":
        st.title("Production Countries and Genre Revenue Overview")

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

                    # Add descriptive sentence
                    st.write(
                        f"This map shows movie production by country. Selected: {selected_country}, with movies like "
                        f"{', '.join([f'{row["Movie Title"]} ({row["Release Year"]}, Popularity: {row["Popularity"]:.2f})' for _, row in movies_from_country.iterrows()])}."
        )


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

                st.write("The pie chart shows the distribution of movie production by country. The United States dominates with 47.4%, followed by the United Kingdom (14%) and Canada (8.13%). Other countries contribute smaller percentages.")

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

                st.write("The line chart shows the number of movies released per year from 2019 to 2023. Movie releases dropped significantly in 2020, peaked in 2021, and dipped in 2022 before rising again in 2023.")

        # Revenue by Genre Analysis
        st.subheader("Revenue by Genre and Year")

        # Dropdown filters for Genre and Year
        selected_genres = st.multiselect(
            "Select Genre(s):",
            options=list(set(genre for sublist in movies_df['genres_list'].dropna() for genre in sublist)),
            default=["Action"]  # Default to one genre
        )
        selected_year = st.slider(
            "Select Year Range:",
            int(movies_df['release_year'].min()),
            int(movies_df['release_year'].max()),
            (int(movies_df['release_year'].min()), int(movies_df['release_year'].max()))
        )

        # Filter data based on selected genres and year range
        filtered_movies = movies_df[
            (movies_df['release_year'] >= selected_year[0]) &
            (movies_df['release_year'] <= selected_year[1]) &
            (movies_df['genres_list'].apply(lambda genres: any(genre in genres for genre in selected_genres)))
        ]

        if not filtered_movies.empty:
            # Group by Genre and calculate total revenue
            genre_revenue = filtered_movies.explode('genres_list').groupby('genres_list')['revenue'].sum().reset_index()
            genre_revenue = genre_revenue[genre_revenue['genres_list'].isin(selected_genres)]

            # Create bar chart
            revenue_chart = px.bar(
                genre_revenue,
                x='genres_list',
                y='revenue',
                title=f"Revenue by Genre ({selected_year[0]} - {selected_year[1]})",
                labels={'genres_list': 'Genre', 'revenue': 'Total Revenue'},
                text='revenue'
            )
            revenue_chart.update_layout(xaxis=dict(title="Genre"), yaxis=dict(title="Total Revenue"))
            st.plotly_chart(revenue_chart, use_container_width=True)
        else:
            st.write("No data available for the selected genres and year range.")

        st.write("This chart allows users to compare the revenue that was generated between 2019 and 2023. The users can choose multiple genres and compare their revenue ")

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

            # Search bar for actor names
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

            st.write("This interface allows users to search for an actor by entering their name. It helps retrieve and display movies associated with the actor.")

            # Flatten the Cast_list column and count actor appearances
            all_actors = movies_df['Cast_list'].explode().value_counts().reset_index()
            all_actors.columns = ['Actor', 'Title Count']

            # Filter out "Miscellaneous"
            all_actors = all_actors[all_actors['Actor'] != "Miscellaneous"]

            # Toggle switch for most/least titles
            toggle = st.radio("Toggle to view actors featured in:", ["Most Titles", "Least Titles"])
            if toggle == "Most Titles":
                filtered_actors = all_actors.head(10)  # Top 10 actors by title count
                title = "Actors Featured in the Most Titles"
            else:
                filtered_actors = all_actors.tail(10)  # Bottom 10 actors by title count
                title = "Actors Featured in the Least Titles"

            # Plot the chart
            if not filtered_actors.empty:
                chart = px.bar(
                    filtered_actors,
                    x="Title Count",
                    y="Actor",
                    orientation="h",
                    title=title,
                    labels={"Title Count": "Number of Titles", "Actor": "Actor Name"},
                    height=400
                )
                chart.update_layout(yaxis=dict(categoryorder="total ascending"))
                st.plotly_chart(chart, use_container_width=True)

            st.write("This bar chart shows the actors that are featured in the most titles."
                     "The user is also able to toggle to see which actors are featured in the least titles")
