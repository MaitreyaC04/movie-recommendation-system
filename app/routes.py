from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import re
import os

from datetime import datetime
from werkzeug.utils import secure_filename

from app.models import db, User, UserDetails, UserPreferences, RecommendationHistory, Watchlist, Watched
from app.recommender import recommend_movies
from app.utils import get_movie_info

UPLOAD_FOLDER = "static/uploads"   # ensure folder exists
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

auth_bp = Blueprint("auth", __name__)
#app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@auth_bp.route("/")
def home():
    if "user" in session:
        return f"Welcome {session['user']}! <br><a href='/logout'>Logout</a>"
    return render_template("login.html")
    #return redirect(url_for("auth.login"))

# ---------------- SIGNUP ----------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        phone = request.form["phone"].strip()
        
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        # Validation rules
        if not re.match(r"^[a-zA-Z0-9._%+-]+@(gmail|yahoo|outlook)\.com$", email):
            flash("Email must be Gmail, Yahoo, or Outlook only!", "danger")
            return redirect(url_for('auth.signup'))

        if not re.match(r"^[1-9][0-9]{9}$", phone):
            flash("Phone number must be 10 digits and not start with 0!", "danger")
            return redirect(url_for('auth.signup'))

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", password):
            flash("Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number!", "danger")
            return redirect(url_for('auth.signup'))
        
        if (password != confirm_password):
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.signup'))
        
        # Check if email or phone already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.phone == phone)
        ).first()

        # Check uniqueness
        if existing_user:
            flash("Email or phone already registered!", "danger")
            return redirect(url_for("auth.signup"))

        # Create new user and hash password
        new_user = User(email=email, phone=phone)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.home"))

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier'].strip().lower()
        password = request.form['password']

        user = User.query.filter(
            (User.email == identifier) | (User.phone == identifier)
        ).first()
            
        if user and user.check_password(password):
            session["user_id"] = user.user_id
            
            if not user.is_profile_complete:
                return redirect(url_for('auth.complete_profile'))
            elif not user.is_preferences_set:
                return redirect(url_for('auth.set_preferences'))
            else:
                flash("Login successful! Welcome back.", "success")
                return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid login credentials!", "danger")
            return redirect(url_for("auth.home"))
        
    return render_template("login.html")

# ---------------- LOGOUT ----------------
@auth_bp.route('/logout')
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.home'))

# ---------------- DASHBOARD ----------------
@auth_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.home"))
    
    user = User.query.get(session['user_id'])
    user_details = UserDetails.query.filter_by(user_id=user.user_id).first()
    return render_template("dashboard.html", user=user, user_details=user_details)

# ---- COMPLETE PROFILE ----
@auth_bp.route('/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    if request.method == 'POST':
        user_id = session['user_id']
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        
        country = request.form.get('country')
        state = request.form.get('state')
        city = request.form.get('city')
        
        occupation = request.form.get('occupation')
        streaming_platforms = request.form.getlist('streaming_platforms')
        
        bio = request.form.get('bio')
        profile_pic = request.files.get('profile_picture')

        # ---- VALIDATION ----
        if not (first_name and last_name and dob and gender and country and state and city):
            flash("All required fields must be filled!", "error")
            return redirect(url_for('complete_profile'))

        # ---- HANDLE FILE UPLOAD ----
        profile_pic_path = None
        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            profile_pic_path = os.path.join(auth_bp.config['UPLOAD_FOLDER'], filename)
            profile_pic.save(profile_pic_path)

        # ---- SAVE TO DB ----
        user_details = UserDetails(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=datetime.strptime(dob, "%Y-%m-%d"),
            gender=gender,
            country=country,
            state=state,
            city=city,
            occupation=occupation,
            streaming_platforms=streaming_platforms,
            bio=bio,
            profile_picture=profile_pic_path
        )
        db.session.add(user_details)

        # mark profile as complete
        user = User.query.get(user_id)
        user.is_profile_complete = True

        db.session.commit()

        flash("Profile completed successfully! Now set your preferences.", "success")
        return redirect(url_for('auth.set_preferences'))
    
    return render_template('complete_profile.html')

# ---- SET PREFERENCES ----
@auth_bp.route('/set-preferences', methods=['GET', 'POST'])
def set_preferences():
    languages = ['English', 'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Kannada', 'Marathi',
                 'Malayalam', 'Urdu', 'Punjabi', 'Gujarati', 'French', 'Italian', 
                 'Spanish', 'German', 'Japanese', 'Russian', 'Portuguese', 'Mandarin', 
                 'Swedish', 'Korean', 'Arabic', 'Turkish']
    
    genres = ['Action', 'Science Fiction', 'Adventure', 'Drama', 'Crime', 'Thriller', 
              'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War', 'Family', 
              'Animation', 'Horror', 'Music', 'History', 'TV Movie', 'Documentary']
    
    if request.method == 'POST':
        user_id = session['user_id']
        
        selected_genres = request.form.get("genres", "").split(",") if request.form.get("genres") else []
        selected_languages = request.form.get("languages", "").split(",") if request.form.get("languages") else []

        # Validation
        if not selected_genres:
            flash("Please select at least one genre.", "danger")
            return redirect(url_for('auth.set_preferences'))
        if not selected_languages:
            flash("Please select at least one language.", "danger")
            return redirect(url_for('auth.set_preferences'))

        # Save preferences
        preferences = UserPreferences(
            user_id=user_id,
            genres=selected_genres,
            languages=selected_languages,
        )
        db.session.add(preferences)

        user = User.query.get(user_id)
        user.is_preferences_set = True
        db.session.commit()

        flash("Preferences saved successfully! Redirecting to dashboard.", "success")
        return redirect(url_for('auth.dashboard'))
    
    return render_template('set_preferences.html', languages=languages, genres=genres)

# ---- VIEW PROFILE ----
@auth_bp.route('/profile', methods=['GET', 'POST'])
def view_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    user_details = UserDetails.query.filter_by(user_id=user.user_id).first()
    return render_template('view_profile.html', user=user, user_details=user_details)

# ---- UPDATE PROFILE ----
@auth_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    details = UserDetails.query.filter_by(user_id=user.user_id).first()

    details.first_name = request.form['first_name']
    details.last_name = request.form['last_name']
    
    details.date_of_birth = request.form['dob']
    details.gender = request.form['gender']
    
    details.country = request.form['country']
    details.state = request.form['state']
    details.city = request.form['city']
    
    details.occupation = request.form.get('occupation')
    details.streaming_platforms = request.form.getlist('platforms')
    details.bio = request.form['bio']

    if 'profile_picture' in request.files:
        pic = request.files['profile_picture']
        if pic.filename != "":
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(auth_bp.config['UPLOAD_FOLDER'], filename))
            details.profile_picture = filename

    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('auth.dashboard'))

# ---- VIEW PREFERENCES ----
@auth_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    languages = ['English', 'Hindi', 'Bengali', 'Tamil', 'Telugu', 'Kannada', 'Marathi',
                 'Malayalam', 'Urdu', 'Punjabi', 'Gujarati', 'French', 'Italian', 
                 'Spanish', 'German', 'Japanese', 'Russian', 'Portuguese', 'Mandarin', 
                 'Swedish', 'Korean', 'Arabic', 'Turkish']
    
    genres = ['Action', 'Science Fiction', 'Adventure', 'Drama', 'Crime', 'Thriller', 
              'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War', 'Family', 
              'Animation', 'Horror', 'Music', 'History', 'TV Movie', 'Documentary']
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    preferences = UserPreferences.query.filter_by(user_id=user.user_id).first()
    user_details = UserDetails.query.filter_by(user_id=user.user_id).first()
    
    return render_template('preferences.html', user=user, languages=languages, genres=genres, 
                           user_details=user_details, preferences=preferences)

# ---- UPDATE PREFERENCES ----
@auth_bp.route('/update_preferences', methods=['POST'])
def update_preferences():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    prefs = UserPreferences.query.filter_by(user_id=user.user_id).first()

    prefs.languages = request.form.getlist('languages')
    prefs.genres = request.form.getlist('genres')

    if not prefs.languages or not prefs.genres:
        flash("You must select at least one language, genre, and actor!", "danger")
        return redirect(url_for('auth.preferences'))

    db.session.commit()
    flash("Preferences updated successfully!", "success")
    return redirect(url_for('auth.dashboard'))

# ---- GET NEW RECOMMENDATIONS ----
@auth_bp.route("/get_recommendations")
def get_recommendations():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(session['user_id'])
    
    prefs = UserPreferences.query.filter_by(user_id=user.user_id).first()
    imdb_ids = recommend_movies(prefs.genres, prefs.languages)

    # save in history
    history = RecommendationHistory(
        user_id=user_id,
        imdb_ids=imdb_ids
    )
    db.session.add(history)
    db.session.commit()

    # Fetch movie details for display
    movies = [get_movie_info(imdb_id) for imdb_id in imdb_ids]
    return render_template("recommendations.html", movies=movies, title="New Recommendations")

# ---- VIEW PAST RECOMMENDATIONS ----
@auth_bp.route("/past_recommendations")
def past_recommendations():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session["user_id"]
    
    history = (
        RecommendationHistory.query.filter_by(user_id=user_id)
        .order_by(RecommendationHistory.created_at.desc())
        .all()
    )

    # Prepare sessions with movie details
    sessions = []
    for rec in history:
        movies = [get_movie_info(imdb_id) for imdb_id in rec.imdb_ids]
        sessions.append({"id": rec.id, "date": rec.created_at, "movies": movies})

    return render_template("past_recommendations.html", sessions=sessions)

# ---- MOVIE DETAILS ----
@auth_bp.route("/movie/<imdb_id>")
def movie_details(imdb_id):
    details = get_movie_info(imdb_id)
    if not details:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify(details)

# ---- ADD TO WATCHLIST ----
@auth_bp.route("/watchlist/add/<imdb_id>", methods=["POST"])
def add_to_watchlist(imdb_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    entry = Watchlist(user_id=user_id, imdb_id=imdb_id)
    
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({"message": "Movie added to Watchlist!"})

# ---- ADD TO WATCHED ----
@auth_bp.route("/watched/add", methods=["POST"])
def add_watched_movie():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    data = request.json
    imdb_id = data.get("imdb_id")
    
    like_dislike = data.get("like_dislike")
    rating = data.get("rating")
    review = data.get("review")

    entry = Watched(
        user_id=user_id,
        imdb_id=imdb_id,
        like_dislike=like_dislike,
        rating=rating,
        review=review,
    )
    db.session.add(entry)
    db.session.commit()
    
    return jsonify({"message": "Review saved!"})

# ---- VIEW WATCHLIST ----
@auth_bp.route("/watchlist")
def view_watchlist():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    watchlist = Watchlist.query.filter_by(user_id=user_id).all()
    movies = [get_movie_info(w.imdb_id) for w in watchlist]
    
    return render_template("watchlist.html", movies=movies)

# ---- VIEW WATCHED MOVIES ----
@auth_bp.route("/watched")
def view_watched():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    watched = Watched.query.filter_by(user_id=user_id).all()
    
    movies = []
    for w in watched:
        movie_data = get_movie_info(w.imdb_id)
        movie_data["like_dislike"] = w.like_dislike
        movie_data["rating"] = w.rating
        movie_data["review"] = w.review
        movies.append(movie_data)
        
    return render_template("watched.html", movies=movies)
