import requests
import pandas as pd
from app.models import db, MovieDetails

OMDB_API_KEY = "3360d77c"

# Load TMDB dataset
df = pd.read_csv("tmdb_dataset.csv")

def fetch_from_omdb(imdb_id):
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("Response") == "True":
            return {
                "imdb_id": imdb_id,
                "title": data.get("Title"),
                "year": data.get("Year"),
                "poster": data.get("Poster") if data.get("Poster") != "N/A" else None,
                "plot": data.get("Plot"),
                "genre": data.get("Genre"),
                "director": data.get("Director"),
                "actors": data.get("Actors"),
                "language": data.get("Language"),
                "country": data.get("Country"),
                "runtime": data.get("Runtime"),
                "source": "OMDB",
            }
    return None

def get_movie_info(imdb_id):
    """Fetch poster + title (from cache → OMDB → TMDB)"""
    movie = MovieDetails.query.get(imdb_id)
    if movie:
        return {"imdb_id": imdb_id, 
                "title": movie.title, 
                "year": movie.year,
                "poster": movie.poster or "/static/no-poster.png",
                "plot": movie.plot,
                "genre": movie.genre,
                "director": movie.director,
                "actors": movie.actors,
                "language": movie.language,
                "country": movie.country,
                "runtime": movie.runtime,
                "source": movie.source}

    # Try OMDB
    data = fetch_from_omdb(imdb_id)
    if data:
        movie = MovieDetails(**data)
        db.session.add(movie)
        db.session.commit()
        return {"imdb_id": imdb_id, 
                "title": data.get("title"),
                "year": data.get("year"),
                "poster": data.get("poster") or "/static/no-poster.png",
                "plot": data.get("plot"),
                "genre": data.get("genre"),
                "director": data.get("director"),
                "actors": data.get("actors"),
                "language": data.get("language"),
                "country": data.get("country"),
                "runtime": data.get("runtime"),
                "source": "OMDB"}

    # Fallback to TMDB CSV
    row = df[df["imdb_id"] == imdb_id]
    if not row.empty:
        row = row.iloc[0]
        movie = MovieDetails(
            imdb_id=imdb_id,
            title=row["title"],
            year=str(row["release_date"]).split("-")[0] if pd.notna(row["release_date"]) else None,
            poster=None,
            plot=row["overview"],
            genre=row["genres"],
            director=None,
            actors=None,
            language=row["original_language"],
            country=row["production_countries"],
            runtime=str(row["runtime"]) if pd.notna(row["runtime"]) else None,
            source="TMDB",
        )
        db.session.add(movie)
        db.session.commit()
        
        return {"imdb_id": imdb_id, 
                "title": row["title"], 
                "poster": "/static/no-poster.png"}

    return {"imdb_id": imdb_id, "title": "Unknown", "poster": "/static/no-poster.png"}
