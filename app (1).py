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

if st.button("Search movie"):
    try:
        results = tmdb("search/movie", token, {"query": query}).get("results", [])

        if not results:
            st.warning("No movies found. Try another title.")
            st.stop()

        movie_names = [
            f"{m['title']} ({(m.get('release_date') or 'Unknown')[:4]})"
            for m in results[:10]
        ]
        selected = st.selectbox("Choose a movie", movie_names)
        movie = results[movie_names.index(selected)]

        details = tmdb(f"movie/{movie['id']}", token)
        reviews = tmdb(
            f"movie/{movie['id']}/reviews", token, {"page": 1}
        ).get("results", [])

        left, right = st.columns([1, 2])

        with left:
            if details.get("poster_path"):
                st.image(IMG + details["poster_path"], use_container_width=True)

        with right:
            st.header(details.get("title", "Movie"))
            st.write(details.get("overview", "No overview available."))
            st.metric("TMDB rating", f"{details.get('vote_average', 0):.1f}/10")
            st.write("Genres:", ", ".join(
                g["name"] for g in details.get("genres", [])
            ))
            st.write("Release date:", details.get("release_date", "Unknown"))

        counts = {"Positive": 0, "Neutral": 0, "Negative": 0}

        for review in reviews:
            text = review.get("content", "").strip()
            if not text:
                continue

            score = analyzer.polarity_scores(text)["compound"]

            if score >= 0.05:
                counts["Positive"] += 1
            elif score <= -0.05:
                counts["Negative"] += 1
            else:
                counts["Neutral"] += 1

        total = sum(counts.values())
        st.subheader("Audience review sentiment")

        if total:
            st.bar_chart(pd.DataFrame(
                {"Reviews": list(counts.values())},
                index=list(counts.keys()),
            ))

            positive_share = counts["Positive"] / total
            rating_share = float(details.get("vote_average") or 0) / 10
            reelworth_score = 100 * (
                0.65 * rating_share + 0.35 * positive_share
            )

            a, b, c = st.columns(3)
            a.metric("Reviews analyzed", total)
            b.metric("Positive reviews", f"{positive_share:.0%}")
            c.metric("ReelWorth score", f"{reelworth_score:.0f}/100")
        else:
            st.info("No review text was available to analyze for this movie.")

        st.caption(
            "The ReelWorth score is a heuristic combining TMDB rating "
            "and review sentiment; it is not a trained ML prediction."
        )

    except requests.exceptions.RequestException as error:
        st.error(f"TMDB request failed: {error}")
