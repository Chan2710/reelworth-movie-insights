import os
import requests
import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ---------------- CINEMATIC REELWORTH THEME ----------------
st.markdown("""
<style>
/* Overall app background and typography */
.stApp {
    background: linear-gradient(135deg, #0B1020 0%, #11182B 55%, #151126 100%);
    color: #F8FAFC;
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", sans-serif;
}

/* Main content spacing */
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1, h2, h3 {
    color: #F8FAFC !important;
    letter-spacing: -0.4px;
}

h1 {
    font-weight: 800 !important;
}

h2 {
    border-bottom: 1px solid #303951;
    padding-bottom: 0.45rem;
}

/* Paragraphs and supporting text */
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #C3CCDD;
}

/* Inputs, search boxes and dropdowns */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: #171E31 !important;
    color: #F8FAFC !important;
    border: 1px solid #35415C !important;
    border-radius: 10px !important;
}

/* Sliders */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: #A78BFA;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #A78BFA, #8065D9);
    color: #FFFFFF !important;
    border: 1px solid #B9A5FF;
    border-radius: 10px;
    padding: 0.55rem 1.1rem;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #B9A5FF, #9278EC);
    border-color: #D4C7FF;
    transform: translateY(-1px);
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #171E31;
    border: 1px solid #303951;
    padding: 1rem;
    border-radius: 14px;
}

/* Charts and data panels */
[data-testid="stPlotlyChart"],
[data-testid="stVegaLiteChart"],
[data-testid="stDataFrame"] {
    background-color: #171E31;
    border-radius: 14px;
}

/* Expanders and bordered containers */
[data-testid="stExpander"],
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #303951 !important;
    border-radius: 12px;
}

/* Dividers */
hr {
    border-color: #303951 !important;
}

/* Links */
a {
    color: #B9A5FF !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0E1424;
    border-right: 1px solid #303951;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------

st.set_page_config(page_title="CineScope | Movie Insights", page_icon="🎬", layout="wide")

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
analyzer = SentimentIntensityAnalyzer()


left, right = st.columns([1.25, 1], gap="large")

with left:
    st.markdown(
        """
        <div style="padding: 24px 0 12px 0;">
            <h1 style="font-size: 3rem; margin-bottom: 12px;">
                🎬 CineScope
            </h1>
            <p style="font-size: 1.1rem; color: #c7c9dc;">
                Movie insights powered by TMDB ratings and audience reviews.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div style="
            margin-top: 18px;
            padding: 28px;
            min-height: 150px;
            border-radius: 18px;
            background: linear-gradient(120deg, #211d42, #39245f, #171b32);
            border: 1px solid #514477;
            box-shadow: 0 8px 30px rgba(0,0,0,0.22);
        ">
            <div style="
                color: #c4a7ff;
                font-size: 0.8rem;
                letter-spacing: 3px;
                text-transform: uppercase;
            ">
                YOUR PERSONAL MOVIE GUIDE
            </div>
            <h2 style="
                color: white;
                font-size: 1.8rem;
                margin: 14px 0 8px 0;
            ">
                Find your next favorite film.
            </h2>
            <p style="color: #d0cde3; margin: 0;">
                Discover stories. Compare ratings. Choose what to watch.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()



def get_token():
    try:
        token = st.secrets.get("TMDB_TOKEN", "")
    except Exception:
        token = ""
    return token or os.getenv("TMDB_TOKEN", "")


def tmdb(endpoint, token, params=None):
    response = requests.get(
        f"{API}/{endpoint}",
        headers={"Authorization": f"Bearer {token}"},
        params=params or {},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


token = get_token()

if not token:
    st.error("TMDB_TOKEN is missing. Add it to Streamlit Cloud → Manage app → Settings → Secrets.")
    st.stop()


# --------------- SEARCH FOR A MOVIE ----------------
st.divider()
st.header("Find a movie by name")
st.write("Search for a specific movie to explore its ratings and audience reviews.")

search_col, button_col = st.columns([5, 1])

with search_col:
    movie_query = st.text_input(
        "Movie title",
        placeholder="Try Interstellar, 3 Idiots, or Dune",
        key="title_search_input",
    )

with button_col:
    st.write("")
    search_clicked = st.button("Search", key="title_search_button", use_container_width=True)

if search_clicked:
    if not movie_query.strip():
        st.warning("Please enter a movie title.")
    else:
        try:
            search_data = tmdb(
                "search/movie",
                token,
                {"query": movie_query.strip()},
            )
            st.session_state["title_search_results"] = search_data.get("results", [])
        except requests.exceptions.RequestException as error:
            st.error(f"Movie search failed: {error}")

if st.session_state.get("title_search_results"):
    search_results = st.session_state["title_search_results"]

    movie_labels = [
        f"{movie.get('title', 'Untitled')} ({(movie.get('release_date') or 'Unknown')[:4]})"
        for movie in search_results
    ]

    selected_label = st.selectbox(
        "Choose the movie you want",
        movie_labels,
        key="title_search_selection",
    )

    selected_movie = search_results[movie_labels.index(selected_label)]


    if selected_movie.get("poster_path"):
        st.image(
            f"https://image.tmdb.org/t/p/w500{selected_movie['poster_path']}",
            width=180,
        )


    st.subheader(selected_movie.get("title", "Untitled"))
    st.write(selected_movie.get("overview") or "No overview available.")
    st.write(f"TMDB rating: {selected_movie.get('vote_average', 0):.1f}/10")

# --------------- END SEARCH FOR A MOVIE ----------------


# ---------------- MOVIE DISCOVERY ----------------
st.divider()
st.header("Discover your next movie")
st.write("Find something to watch based on your mood and taste.")

mood_options = {
    "Any mood": [],
    "Feel-good": [35, 10751],
    "Mind-bending": [878, 9648, 53],
    "Laugh-out-loud": [35],
    "Suspenseful": [53, 9648, 80],
    "Epic adventure": [12, 14, 28],
    "Romantic": [10749, 18],
}

genre_options = {
    "Any genre": None,
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "Horror": 27,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "Thriller": 53,
}

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_mood = st.selectbox(
        "Choose a mood",
        list(mood_options.keys()),
        key="discovery_mood",
    )

with filter_col2:
    selected_genre = st.selectbox(
        "Choose a genre",
        list(genre_options.keys()),
        key="discovery_genre",
    )

minimum_rating = st.slider(
    "Minimum TMDB rating",
    min_value=0.0,
    max_value=9.0,
    value=6.5,
    step=0.5,
    key="discovery_min_rating",
)

if st.button("Discover movies", key="discover_movies_button"):
    try:
        with st.spinner("Finding movies for you..."):
            params = {
                "sort_by": "popularity.desc",
                "vote_count.gte": 50,
                "vote_average.gte": minimum_rating,
                "include_adult": False,
                "page": 1,
            }

            mood_genres = mood_options[selected_mood]
            chosen_genre = genre_options[selected_genre]

            genre_ids = []

            if mood_genres:
                genre_ids.extend(mood_genres)

            if chosen_genre is not None:
                genre_ids.append(chosen_genre)

            if genre_ids:
                params["with_genres"] = ",".join(
                    str(g) for g in dict.fromkeys(genre_ids)
                )

            discovery_data = tmdb("discover/movie", token, params)

            st.session_state["discovery_results"] = (
                discovery_data.get("results", [])
            )

    except requests.exceptions.RequestException as error:
        st.error(f"Could not discover movies: {error}")

discovery_results = st.session_state.get("discovery_results", [])

if discovery_results:
    st.subheader("Movies picked for you")

    cards = st.columns(3)

    for index, movie in enumerate(discovery_results[:9]):
        with cards[index % 3]:
            if movie.get("poster_path"):
                st.image(
                    IMG + movie["poster_path"],
                      width=380,
                )

            st.markdown(f"**{movie.get('title', 'Untitled')}**")

            if st.button(
                "Analyze this movie",
                key=f"analyze_movie_{movie['id']}",
            ):
                st.session_state["movie_search_query"] = movie.get("title", "")
                st.session_state["selected_movie_id"] = movie["id"]
                st.session_state["movie_results"] = [movie]
                st.rerun()

            release_year = (
                (movie.get("release_date") or "Unknown")[:4]
            )

            st.caption(
                f"{release_year} · "
                f"TMDB rating {movie.get('vote_average', 0):.1f}/10"
            )

            
            overview = movie.get("overview") or "No overview available."
            st.write(overview[:160] + ("..." if len(overview) > 160 else ""))
            
            reasons = []
            
            if movie.get("vote_average", 0) >= 7.5:
                reasons.append("Highly rated by TMDB users")
            elif movie.get("vote_average", 0) >= 6.5:
                reasons.append("Decent audience rating")
            
            if selected_mood != "Any mood":
                reasons.append(f"Matches your {selected_mood.lower()} preference")
            
            if selected_genre != "Any genre":
                reasons.append(f"Matches your {selected_genre.lower()} genre")
            
            if reasons:
                st.caption("Why this pick?")
                for reason in reasons:
                    st.write(f"• {reason}")
            

elif "discovery_results" in st.session_state:
    st.info(
        "No movies matched those filters. Try another mood, genre, "
        "or a lower minimum rating."
    )

st.divider()
# ---------------- END MOVIE DISCOVERY ----------------

if "movie_results" not in st.session_state:
    st.session_state.movie_results = []


if st.session_state.movie_results:
    results = st.session_state.movie_results

    movie_names = [
        f"{m['title']} ({(m.get('release_date') or 'Unknown')[:4]})"
        for m in results[:10]
    ]


    selected_movie_id = st.session_state.get("selected_movie_id")
    
    default_index = 0
    
    if selected_movie_id is not None:
        for i, result in enumerate(results[:10]):
            if result.get("id") == selected_movie_id:
                default_index = i
                break
    
    selected = st.selectbox(
        "Choose a movie",
        movie_names,
        index=default_index,
    )
    
    movie = results[movie_names.index(selected)]


    try:
        details = tmdb(f"movie/{movie['id']}", token)
        reviews = tmdb(
            f"movie/{movie['id']}/reviews",
            token,
            {"page": 1},
        ).get("results", [])

        left, right = st.columns([1, 2])

        with left:
            if details.get("poster_path"):
                st.image(
                    IMG + details["poster_path"],
                    use_container_width=True,
                )

        with right:
            st.header(details.get("title", "Movie"))
            st.write(details.get("overview", "No overview available."))
            st.metric(
                "TMDB rating",
                f"{details.get('vote_average', 0):.1f}/10",
            )
            st.write(
                "Genres:",
                ", ".join(g["name"] for g in details.get("genres", [])),
            )
            st.write(
                "Release date:",
                details.get("release_date", "Unknown"),
            )

        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}

        for review in reviews:
            text = review.get("content", "").strip()
            if not text:
                continue

            compound = analyzer.polarity_scores(text)["compound"]

            if compound >= 0.05:
                counts["Positive"] += 1
            elif compound <= -0.05:
                counts["Negative"] += 1
            else:
                counts["Neutral"] += 1

        total = sum(counts.values())
        st.subheader("Audience review sentiment")

        if total > 0:
            st.bar_chart(
                pd.DataFrame(
                    {"Reviews": list(counts.values())},
                    index=list(counts.keys()),
                )
            )

            positive_share = counts["Positive"] / total
            rating_share = float(details.get("vote_average") or 0) / 10
            score = 100 * (
                0.65 * rating_share + 0.35 * positive_share
            )

            # Create a simple, explainable recommendation
            if score >= 75:
                verdict = "Worth watching"
                explanation = "The rating and review sentiment are encouraging."
            elif score >= 60:
                verdict = "Worth considering"
                explanation = "The overall signals are mixed or moderately positive."
            else:
                verdict = "Consider skipping"
                explanation = "The current rating and review sentiment are less encouraging."
            
            # Show how much audience evidence is available
            vote_count = details.get("vote_count", 0) or 0
            
            if total < 10:
                confidence = "Limited review evidence"
            elif vote_count < 100:
                confidence = "Limited rating evidence"
            else:
                confidence = "More audience data available"
            
            st.subheader("Should you watch this movie?")
            st.title(verdict)
            st.write(explanation)
            st.caption(
                f"ReelWorth score: {score:.0f}/100 · "
                f"TMDB votes: {vote_count:,} · "
                f"Written reviews analyzed: {total}"
            )
            st.info(
                f"Evidence note: {confidence}. "
                "This is a simple indicator, not a guarantee of whether you will enjoy the film."
            )
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Reviews analyzed", total)
            col2.metric("Positive reviews", f"{positive_share:.0%}")
            col3.metric("ReelWorth score", f"{score:.0f}/100")
        else:
            st.info("No review text was available for this movie.")

    except requests.exceptions.RequestException as error:
        st.error(f"Could not load movie details: {error}")
