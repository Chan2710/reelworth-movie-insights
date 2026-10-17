import os
import requests
import pandas as pd
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="ReelWorth", page_icon="🎬", layout="wide")

API = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
analyzer = SentimentIntensityAnalyzer()

st.title("🎬 ReelWorth")
st.write("Movie insights powered by TMDB ratings and audience reviews.")


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


query = st.text_input("Enter a movie title", "Interstellar")

if "movie_results" not in st.session_state:
    st.session_state.movie_results = []

if st.button("Search movie"):
    if not query.strip():
        st.warning("Please enter a movie title.")
    else:
        try:
            with st.spinner("Searching TMDB..."):
                data = tmdb(
                    "search/movie",
                    token,
                    {"query": query.strip()},
                )
            st.session_state.movie_results = data.get("results", [])
        except requests.exceptions.RequestException as error:
            st.error(f"TMDB search failed: {error}")
            st.session_state.movie_results = []

if st.session_state.movie_results:
    results = st.session_state.movie_results

    movie_names = [
        f"{m['title']} ({(m.get('release_date') or 'Unknown')[:4]})"
        for m in results[:10]
    ]

    selected = st.selectbox("Choose a movie", movie_names)
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
