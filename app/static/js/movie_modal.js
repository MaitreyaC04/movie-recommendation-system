document.addEventListener("DOMContentLoaded", function () {
  const movieCards = document.querySelectorAll(".movie-card");

  movieCards.forEach(card => {
    card.addEventListener("click", function () {
      const imdbId = this.getAttribute("data-imdb");

      if (!imdbId) {
        console.error("Missing imdb_id on card");
        return;
      }

      fetch(`/movie/${imdbId}`)
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            alert("Movie details not found");
            return;
          }

          // Fill modal fields
          document.getElementById("movieTitle").textContent = data.title || "Unknown Title";
          document.getElementById("moviePoster").src = data.poster || "/static/no-poster.png";
          document.getElementById("movieYear").textContent = data.year || "N/A";
          document.getElementById("movieGenre").textContent = data.genre || "N/A";
          document.getElementById("movieDirector").textContent = data.director || "N/A";
          document.getElementById("movieActors").textContent = data.actors || "N/A";
          document.getElementById("movieLanguage").textContent = data.language || "N/A";
          document.getElementById("movieCountry").textContent = data.country || "N/A";
          document.getElementById("movieRuntime").textContent = data.runtime || "N/A";
          document.getElementById("moviePlot").textContent = data.plot || "N/A";
          document.getElementById("movieSource").textContent = data.source || "N/A";

          // Show modal
          const movieModal = new bootstrap.Modal(document.getElementById("movieModal"));
          movieModal.show();
        })
        .catch(err => {
          console.error("Error fetching movie details:", err);
        });
    });
  });
});

let currentImdbId = null;

// Attach handlers when modal is opened
function showMovieModal(data) {
  currentImdbId = data.imdb_id;

  // Populate modal details as before
  document.getElementById("movieTitle").innerText = data.title || "N/A";
  document.getElementById("movieYear").innerText = data.year || "N/A";
  document.getElementById("moviePoster").src = data.poster || "/static/no-poster.png";
  document.getElementById("moviePlot").innerText = data.plot || "N/A";

  // Button actions
  document.getElementById("watchlistBtn").onclick = () => addToWatchlist(currentImdbId);
  document.getElementById("watchedBtn").onclick = () => {
    // Show review modal
    const reviewModal = new bootstrap.Modal(document.getElementById("reviewModal"));
    reviewModal.show();
  };

  const movieModal = new bootstrap.Modal(document.getElementById("movieModal"));
  movieModal.show();
}

function addToWatchlist(imdbId) {
  fetch(`/watchlist/add/${imdbId}`, { method: "POST" })
    .then(r => r.json())
    .then(data => {
      alert(data.message);
    })
    .catch(err => console.error("Error adding to watchlist:", err));
}

function markAsWatched(imdbId) {
  // First just mark watched
  fetch(`/watched/add/${imdbId}`, { method: "POST" })
    .then(r => r.json())
    .then(data => {
      alert(data.message);
      // optionally open review form directly
      window.location.href = `/watched/edit/${imdbId}`;
    })
    .catch(err => console.error("Error marking watched:", err));
}

// Submit review
document.getElementById("reviewForm").onsubmit = function (e) {
  e.preventDefault();
  const payload = {
    imdb_id: currentImdbId,
    like_dislike: document.getElementById("likeDislike").value,
    rating: document.getElementById("rating").value,
    review: document.getElementById("review").value,
  };

  fetch(`/watched/add`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then(r => r.json())
    .then(res => {
      alert(res.message);
      bootstrap.Modal.getInstance(document.getElementById("reviewModal")).hide();
    })
    .catch(err => console.error(err));
};

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".movie-card").forEach(card => {
    card.addEventListener("click", () => {
      const imdbId = card.getAttribute("data-imdb");

      fetch(`/movie/${imdbId}`)
        .then(r => r.json())
        .then(data => {
          if (data.error) {
            alert("Movie details not found.");
          } else {
            showMovieModal(data);  // Reuse your existing modal display function
          }
        })
        .catch(err => console.error("Error fetching movie details:", err));
    });
  });
});
