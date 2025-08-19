from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# --- USER MODEL ---
class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    
    is_profile_complete = db.Column(db.Boolean, default=False)
    is_preferences_set = db.Column(db.Boolean, default=False)

    '''def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)'''
    
    # Set password (hash it before saving)
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    # Verify password
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)

    #def __repr__(self):
        #return f"<User {self.email}>"

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    
    country = db.Column(db.String(50))
    state = db.Column(db.String(50))
    city = db.Column(db.String(50))
    
    occupation = db.Column(db.String(100))
    streaming_platforms = db.Column(db.ARRAY(db.String))
    
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(200))  # store path/URL
    
class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    
    genres = db.Column(db.ARRAY(db.String))
    languages = db.Column(db.ARRAY(db.String))
    
class RecommendationHistory(db.Model):
    __tablename__ = "recommendation_history"
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    imdb_ids = db.Column(db.ARRAY(db.String), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class MovieDetails(db.Model):
    __tablename__ = "movie_details"
    imdb_id = db.Column(db.String, primary_key=True)
    
    title = db.Column(db.String)
    year = db.Column(db.String)
    
    runtime = db.Column(db.String)
    genre = db.Column(db.String)
    
    director = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    
    language = db.Column(db.String)
    country = db.Column(db.String)
    poster = db.Column(db.String)
    
    cached_at = db.Column(db.DateTime,
                          default=lambda: datetime.now(timezone.utc))
    source = db.Column(db.String)  # "OMDB" or "CSV"

    def to_dict(self):
        return {
            "imdbID": self.imdb_id,
            "Title": self.title,
            "Year": self.year,
            "Runtime": self.runtime,
            "Genre": self.genre,
            "Director": self.director,
            "Actors": self.actors,
            "Plot": self.plot,
            "Language": self.language,
            "Country": self.country,
            "Poster": self.poster,
            "source": self.source
        }
        
class Watchlist(db.Model):
    __tablename__ = "watchlist"
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    imdb_id = db.Column(db.String, nullable=False)

class Watched(db.Model):
    __tablename__ = "watched"
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    imdb_id = db.Column(db.String, nullable=False)
    like_dislike = db.Column(db.String)  # "like" / "dislike"
    
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
