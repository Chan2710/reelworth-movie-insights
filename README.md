# 🎬 ReelWorth — Movie Insights

ReelWorth is a movie recommendation web app that combines
TMDB ratings with sentiment analysis of audience reviews.

## Features

- Search for movies by title
- View movie posters, release dates, genres, and overviews
- Explore TMDB ratings and vote counts
- Analyze audience reviews using VADER sentiment analysis
- View positive, neutral, and negative sentiment counts
- Get a recommendation score based on ratings and sentiment

## Technology Stack

- Python
- Streamlit
- TMDB API
- Pandas-ready Python data workflow
- VADER Sentiment Analysis

## How It Works

ReelWorth combines a normalized TMDB rating with the proportion
of positive written reviews to calculate a recommendation score.

The current scoring approach is a heuristic, not a trained
machine-learning model.

## Run Locally

Install dependencies:

    pip install -r requirements.txt

Set your TMDB API Read Access Token as a Streamlit secret
named TMDB_TOKEN, then run:

    streamlit run app.py

## Data and Attribution

Movie information and audience reviews are retrieved from
The Movie Database (TMDB).

This project is an independent learning project and is not
endorsed or certified by TMDB.
