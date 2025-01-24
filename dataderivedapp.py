import customtkinter as ctk  # CustomTkinter for modern GUI design
from tkinter import messagebox  # For displaying message boxes
from PIL import Image  # To handle image processing
import requests  # For making HTTP requests to the API
from io import BytesIO  # To handle image data as a byte stream

# TMDB API key and endpoints
TMDB_API_KEY = "7ce3762a2866cb52a41c8caaa08192f1"  # Your TMDB API key
TMDB_POPULAR_URL = "https://api.themoviedb.org/3/movie/popular"  # Popular movies endpoint
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"  # Movie search endpoint
TMDB_TRENDING_URL = "https://api.themoviedb.org/3/trending/movie/day"  # Trending movies endpoint
TMDB_TV_URL = "https://api.themoviedb.org/3/tv/popular"  # Popular TV shows endpoint
TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"  # Base URL for movie poster images

# Initialize the main application window
app = ctk.CTk()
app.title("MOVIES.CO")  # App title
app.geometry("1000x600")  # Window size
app.configure(bg="black")  # Background color

# Function to fetch data from the API
def fetch_data(url, params):
    """
    Fetch data from the given API endpoint with the provided parameters.
    :param url: API endpoint URL
    :param params: Parameters for the API request
    :return: List of results from the API response
    """
    try:
        response = requests.get(url, params=params)  # Make a GET request
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("results", [])  # Extract 'results' from JSON response
    except requests.exceptions.RequestException as e:
        # Show an error message in case of failure
        messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return []

# Function to display movies in a scrollable grid
def display_movies(data, container):
    """
    Display movie data in a grid layout inside a given container.
    :param data: List of movies to display
    :param container: Parent container for the grid
    """
    # Clear existing widgets in the container
    for widget in container.winfo_children():
        widget.destroy()

    row, col = 0, 0  # Initialize grid row and column
    for movie in data[:15]:  # Limit display to 15 movies
        poster_path = movie.get("poster_path")  # Get poster path
        title = movie.get("title", "Unknown Title")  # Get movie title

        # Fetch poster image if available
        if poster_path:
            image_url = TMDB_IMAGE_URL + poster_path
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                poster_image = ctk.CTkImage(Image.open(image_data), size=(150, 225))
            else:
                poster_image = None
        else:
            poster_image = None

        # Create a frame for each movie
        movie_frame = ctk.CTkFrame(
            container, 
            fg_color="black",  
            border_color="teal",  
            border_width=3,  
            corner_radius=15  
        )
        movie_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nw")

        # Add poster image to the frame
        if poster_image:
            poster_label = ctk.CTkLabel(movie_frame, image=poster_image, text="")
            poster_label.grid(row=0, column=0, padx=10, pady=10)
            # Bind click event to show movie details
            poster_label.bind("<Button-1>", lambda e, m=movie: show_movie_details(m))

        # Add movie title to the frame
        title_label = ctk.CTkLabel(
            movie_frame, text=title, text_color="white", wraplength=150, font=("Helvetica", 10)
        )
        title_label.grid(row=1, column=0, pady=5)

        # Adjust grid position
        col += 1
        if col > 4:  # Move to the next row after 5 columns
            col = 0
            row += 1

# Function to show detailed information about a movie
def show_movie_details(movie):
    """
    Display a detailed view of the selected movie in a new window.
    :param movie: Movie data dictionary
    """
    details_window = ctk.CTkToplevel(app)  # Create a new window
    details_window.title(movie.get("title", "Details"))  # Window title
    details_window.geometry("400x600")  # Window size
    details_window.configure(bg="black")  # Background color

    # Scrollable frame for details
    scroll_frame = ctk.CTkScrollableFrame(details_window, fg_color="black", corner_radius=15)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Fetch poster image if available
    poster_path = movie.get("poster_path")
    if poster_path:
        image_url = TMDB_IMAGE_URL + poster_path
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            poster_image = ctk.CTkImage(Image.open(image_data), size=(300, 450))
        else:
            poster_image = None
    else:
        poster_image = None

    # Add poster image to the details window
    if poster_image:
        poster_label = ctk.CTkLabel(scroll_frame, image=poster_image, text="")
        poster_label.pack(pady=10)

    # Add movie title
    title = movie.get("title", "Unknown Title")
    title_label = ctk.CTkLabel(scroll_frame, text=title, font=("Helvetica", 16, "bold"), text_color="white")
    title_label.pack(pady=5)

    # Add movie description
    overview = movie.get("overview", "No description available.")
    overview_label = ctk.CTkLabel(scroll_frame, text=overview, wraplength=350, text_color="white", justify="left")
    overview_label.pack(pady=10)

    # Watch and close buttons
    watch_button = ctk.CTkButton(scroll_frame, text="Watch Now", fg_color="teal")
    watch_button.pack(pady=10)

    close_button = ctk.CTkButton(scroll_frame, text="Close", command=details_window.destroy, fg_color="teal")
    close_button.pack(pady=10)

# Search functionality
def search_movies():
    """
    Search for movies based on the user's query and display the results.
    """
    query = search_entry.get()  # Get search query
    if not query:  # Show warning if query is empty
        messagebox.showwarning("Warning", "Please enter a search term.")
        return
    params = {"api_key": TMDB_API_KEY, "query": query, "language": "en-US"}
    results = fetch_data(TMDB_SEARCH_URL, params)  # Fetch search results
    display_movies(results, grid_frame)  # Display results

# Show trending movies
def show_trending():
    """
    Fetch and display trending movies.
    """
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    trending_movies = fetch_data(TMDB_TRENDING_URL, params)
    display_movies(trending_movies, grid_frame)

# Show popular TV shows
def show_tv_shows():
    """
    Fetch and display popular TV shows.
    """
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    tv_shows = fetch_data(TMDB_TV_URL, params)
    display_movies(tv_shows, grid_frame)

# Header
header = ctk.CTkLabel(app, text="MOVIES.CO", font=("Helvetica", 24, "bold"), text_color="black")
header.pack(pady=10)

# Navigation bar
nav_bar = ctk.CTkFrame(app, fg_color="teal", corner_radius=15)
nav_bar.pack(fill="x", padx=10, pady=10)

# Search bar and buttons in the navigation bar
search_entry = ctk.CTkEntry(nav_bar, width=300, placeholder_text="Search movies...")
search_entry.pack(side="left", padx=10)

search_button = ctk.CTkButton(nav_bar, text="Search", command=search_movies, fg_color="black")
search_button.pack(side="left", padx=10)

trending_button = ctk.CTkButton(nav_bar, text="Trending", command=show_trending, fg_color="black")
trending_button.pack(side="left", padx=10)

tv_button = ctk.CTkButton(nav_bar, text="Popular TV Shows", command=show_tv_shows, fg_color="black")
tv_button.pack(side="left", padx=10)

# Scrollable frame for movies
scroll_frame = ctk.CTkScrollableFrame(app, fg_color="black", corner_radius=15)
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Grid frame inside the scrollable frame
grid_frame = ctk.CTkFrame(scroll_frame, fg_color="black")
grid_frame.pack(fill="both", expand=True)

# Start the application
show_trending()  # Display trending movies by default
app.mainloop()
