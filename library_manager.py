"""
Personal Library Manager Application
----------------------------------
A Streamlit-based web application for managing a personal book library.
Features include:
- Adding and removing books
- Searching books by title, author, or genre
- Tracking read/unread status
- Generating library statistics and visualizations
- Persistent storage using JSON
"""

# Standard library imports
import json      # For JSON file operations
import os        # For file system operations
import time      # For adding delays in UI
from datetime import datetime  # For timestamping book additions

# Third-party library imports
import streamlit as st        # Web application framework
import pandas as pd           # Data manipulation and analysis
import plotly.express as px   # Interactive data visualization
import plotly.graph_objects as go  # Custom plotly charts
import requests               # For potential future API integrations

# Configure Streamlit page settings
# Sets up the web application with a wide layout and expanded sidebar
st.set_page_config(
    page_title="Personal Library Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling the application
# Defines styles for headers, messages, book cards, and buttons
st.markdown("""
<style>
    /* Color Variables */
    :root {
        --primary-color: #2C3E50;
        --secondary-color: #34495E;
        --accent-color: #3498DB;
        --success-color: #27AE60;
        --warning-color: #E67E22;
        --danger-color: #E74C3C;
        --text-color: #2C3E50;
        --bg-color: #ECF0F1;
        --card-bg: #FFFFFF;
    }

    /* Main page header styling */
    .main-header {
        font-size: 3rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Section header styling */
    .sub-header {
        font-size: 2rem !important;
        color: var(--secondary-color);
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--accent-color);
        padding-bottom: 0.5rem;
    }

    /* Success message styling */
    .success-message {
        padding: 1rem;
        background: linear-gradient(90deg, rgba(39, 174, 96, 0.1), rgba(39, 174, 96, 0.05));
        border-left: 4px solid var(--success-color);
        border-radius: 0.375rem;
        color: var(--success-color);
    }
    
    /* Warning message styling */
    .warning-message {
        padding: 1rem;
        background: linear-gradient(90deg, rgba(230, 126, 34, 0.1), rgba(230, 126, 34, 0.05));
        border-left: 4px solid var(--warning-color);
        border-radius: 0.375rem;
        color: var(--warning-color);
    }

    /* Book card styling */
    .book-card {
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--card-bg), #F8F9FA);
        border-left: 4px solid var(--accent-color);
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    /* Hover effect for book cards */
    .book-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid var(--primary-color);
        background: linear-gradient(135deg, #FFFFFF, #F8F9FA);
    }

    /* Read status badge styling */
    .read-badge {
        padding: 0.5rem 1rem;
        background: linear-gradient(45deg, var(--success-color), #2ECC71);
        color: white;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(39, 174, 96, 0.2);
    }

    /* Unread status badge styling */
    .unread-badge {
        padding: 0.5rem 1rem;
        background: linear-gradient(45deg, var(--warning-color), #F39C12);
        color: white;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(230, 126, 34, 0.2);
    }

    /* Action button spacing */
    .action-button {
        margin-right: 0.5rem;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 0.375rem;
        background: linear-gradient(45deg, #4A6CF7, #6B46C1);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(75, 108, 247, 0.2);
    }

    .stButton>button:hover {
        background: linear-gradient(45deg, #3B5BDB, #553C9A);
        box-shadow: 0 4px 6px rgba(75, 108, 247, 0.3);
        transform: translateY(-1px);
    }

    /* Form input styling */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 0.375rem;
        border: 1px solid #BDC3C7;
        padding: 0.5rem;
        background: linear-gradient(180deg, #FFFFFF, #F8F9FA);
    }

    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
        background: linear-gradient(180deg, #FFFFFF, #F8F9FA);
    }

    /* Radio button styling */
    .stRadio>div {
        background: linear-gradient(180deg, var(--bg-color), #F8F9FA);
        padding: 1rem;
        border-radius: 0.375rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-color), #F8F9FA);
    }

    /* Metric card styling */
    .stMetric {
        background: linear-gradient(135deg, var(--card-bg), #F8F9FA);
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
# These variables persist across reruns of the Streamlit app
if 'book_collection' not in st.session_state:
    st.session_state.book_collection = []  # Stores all books in the library
if 'search_output' not in st.session_state:
    st.session_state.search_output = []    # Stores search results
if 'new_book_flag' not in st.session_state:
    st.session_state.new_book_flag = False # Flag for new book addition
if 'book_deleted_flag' not in st.session_state:
    st.session_state.book_deleted_flag = False # Flag for book deletion
if 'active_section' not in st.session_state:
    st.session_state.active_section = 'library' # Current active view

def fetch_library_data() -> bool:
    """
    Load library data from JSON file into session state.
    This function reads the library.json file and loads its contents
    into the application's session state.
    
    Returns:
        bool: True if successful, False if file doesn't exist or error occurs
    """
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.book_collection = json.load(file)
                return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

def persist_library_data() -> bool:
    """
    Save current library data to JSON file.
    This function writes the current state of the library
    to the library.json file for persistence.
    
    Returns:
        bool: True if successful, False if error occurs
    """
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.book_collection, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

def insert_book(book_title: str, book_author: str, pub_year: int, book_genre: str, is_read: bool) -> None:
    """
    Add a new book to the library.
    Creates a new book entry with the provided details and adds it to the library.
    Also updates the JSON file and sets the new book flag.
    
    Args:
        book_title (str): Title of the book
        book_author (str): Author of the book
        pub_year (int): Year of publication
        book_genre (str): Genre of the book
        is_read (bool): Whether the book has been read
    """
    # Create new book entry with current timestamp
    new_entry = {
        'title': book_title,
        'author': book_author,
        'publication_year': pub_year,
        'genre': book_genre,
        'read_status': is_read,
        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    # Add to library and persist changes
    st.session_state.book_collection.append(new_entry)
    persist_library_data()
    st.session_state.new_book_flag = True
    time.sleep(0.5)  # Brief delay for UI feedback

def delete_book(book_index: int) -> bool:
    """
    Remove a book from the library by index.
    Deletes the book at the specified index and updates the JSON file.
    
    Args:
        book_index (int): Index of the book to remove
        
    Returns:
        bool: True if successful, False if index is invalid
    """
    if 0 <= book_index < len(st.session_state.book_collection):
        del st.session_state.book_collection[book_index]
        persist_library_data()
        st.session_state.book_deleted_flag = True
        return True
    return False

def find_books(search_query: str, search_field: str) -> None:
    """
    Search books in the library based on given criteria.
    Performs case-insensitive search on the specified field
    and stores results in session state.
    
    Args:
        search_query (str): Term to search for
        search_field (str): Field to search in ('Title', 'Author', or 'Genre')
    """
    search_query = search_query.lower()
    matches = []

    # Search through each book in the library
    for book in st.session_state.book_collection:
        if search_field == "Title" and search_query in book['title'].lower():
            matches.append(book)
        elif search_field == "Author" and search_query in book['author'].lower():
            matches.append(book)
        elif search_field == "Genre" and search_query in str(book['genre']):
            matches.append(book)
    st.session_state.search_output = matches

def compute_library_metrics() -> dict:
    """
    Calculate various statistics about the library.
    Computes metrics including total books, read status,
    genre distribution, author distribution, and decade distribution.
    
    Returns:
        dict: Dictionary containing library statistics including:
            - total_books: Total number of books
            - read_books: Number of read books
            - percent_read: Percentage of books read
            - genres: Count of books by genre
            - authors: Count of books by author
            - decades: Count of books by publication decade
    """
    # Calculate basic statistics
    book_count = len(st.session_state.book_collection)
    completed_books = sum(1 for book in st.session_state.book_collection if book['read_status'])
    completion_rate = (completed_books / book_count * 100) if book_count > 0 else 0
    
    # Initialize dictionaries for distribution statistics
    genre_distribution = {}
    author_distribution = {}
    decade_distribution = {}

    # Calculate distribution statistics
    for book in st.session_state.book_collection:
        # Count genres
        genre_distribution[book['genre']] = genre_distribution.get(book['genre'], 0) + 1
            
        # Count authors
        author_distribution[book['author']] = author_distribution.get(book['author'], 0) + 1

        # Count books by decade
        decade = (book['publication_year'] // 10) * 10
        decade_distribution[decade] = decade_distribution.get(decade, 0) + 1
    
    # Sort distributions for better presentation
    genre_distribution = dict(sorted(genre_distribution.items(), key=lambda x: x[1], reverse=True))
    author_distribution = dict(sorted(author_distribution.items(), key=lambda x: x[1], reverse=True))
    decade_distribution = dict(sorted(decade_distribution.items(), key=lambda x: x[0]))

    return {
        'total_books': book_count,
        'read_books': completed_books,
        'percent_read': completion_rate,
        'genres': genre_distribution,
        'authors': author_distribution,
        'decades': decade_distribution
    }

def generate_visualizations(metrics: dict) -> None:
    """
    Create and display visualizations for library statistics.
    Generates interactive charts using Plotly to visualize
    the library's statistics.
    
    Args:
        metrics (dict): Dictionary containing library statistics
    """
    # Create pie chart for read vs unread books
    if metrics['total_books'] > 0:
        read_status_chart = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[metrics['read_books'], metrics['total_books'] - metrics['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171'],
        )])
        read_status_chart.update_layout(
            title_text='Read vs Unread Books',
            showlegend=True,
            height=400,
        )
        st.plotly_chart(read_status_chart, use_container_width=True)
    
    # Create bar chart for genres
    if metrics['genres']:
        genre_data = pd.DataFrame({
            'Genre': list(metrics['genres'].keys()),
            'Count': list(metrics['genres'].values())
        })
        genre_chart = px.bar(
            genre_data,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues,
        )
        genre_chart.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height=400,
        )
        st.plotly_chart(genre_chart, use_container_width=True)

    # Create line chart for decades
    if metrics['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f'{decade}s' for decade in metrics['decades'].keys()],
            'Count': list(metrics['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='spline',
        )
        fig_decades.update_layout(
            title_text='Books by Publication Decade',
            xaxis_title='Decade',
            yaxis_title='Number of Books',
            height=400,
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Load library data
fetch_library_data()

# Create sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>📋 Menu</h1>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style="text-align: center;">
        <h1 style="color: var(--text-color);">📚 My Book Haven</h1>
        <p style="color: var(--text-color);">✨ Your personal reading sanctuary ✨</p>
    </div>
    """, unsafe_allow_html=True)

# Create navigation options
nav_options = st.sidebar.radio(
    "🔍 Explore Options",
    ["📖 Browse Collection", "➕ Add New Title", "🔎 Find Books", "📊 Reading Insights"]
)

# Set current view based on navigation selection
if nav_options == "📖 Browse Collection":
    st.session_state.active_section = "library"
elif nav_options == "➕ Add New Title":
    st.session_state.active_section = "add"
elif nav_options == "🔎 Find Books":
    st.session_state.active_section = "search"
elif nav_options == "📊 Reading Insights":
    st.session_state.active_section = "stats"

# Main page header
st.markdown("<h1 class='main-header' style='color: var(--text-color);'>📚 My Personal Reading Sanctuary</h1>", unsafe_allow_html=True)

# Add Book View
if st.session_state.active_section == "add":
    st.markdown("<h2 class='sub-header'>➕ Expand Your Collection</h2>", unsafe_allow_html=True)

    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("📖 Book Title", max_chars=100)
            author = st.text_input("✍️ Author's Name", max_chars=100)
            publication_year = st.number_input(
                "📅 Year Published",
                min_value=1000,
                max_value=datetime.now().year,
                step=1,
                value=2023
            )

        with col2:
            genre = st.selectbox(
                "🏷️ Category",
                ["🎮 Gaming", "🔍 Crime", "🤔 Philosophy", "🐉 Fantasy", "📜 History", "🚀 Science Fiction", "📝 Memoir", "👤 Biography", "💪 Self-Help", "😂 Humor"]
            )
            read_status = st.radio("📚 Reading Status", ["✅ Completed", "⏳ To Read"], horizontal=True)
            read_bool = read_status == "✅ Completed"

        submit_button = st.form_submit_button(label="✨ Add to Collection")

        if submit_button:
            insert_book(title, author, publication_year, genre, read_bool)

    if st.session_state.new_book_flag:
        st.markdown("<div class='success-message'>✨ New title added to your collection!</div>", unsafe_allow_html=True)
        st.session_state.new_book_flag = False

# View Library
elif st.session_state.active_section == "library":
    st.markdown("<h2 class='sub-header'>📚 Your Reading Collection</h2>", unsafe_allow_html=True)

    if not st.session_state.book_collection:
        st.markdown("<div class='warning-message'>📚 Your collection is empty. Start adding some titles!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.book_collection):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>📖 {book['title']}</h3>
                    <p><strong>✍️ Author:</strong> {book['author']}</p>
                    <p><strong>📅 Published:</strong> {book['publication_year']}</p>
                    <p><strong>🏷️ Category:</strong> {book['genre']}</p>
                    <p><span class="{'read-badge' if book['read_status'] else 'unread-badge'}">{"✅ Completed" if book['read_status'] else "⏳ To Read"}</span></p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                        if delete_book(i):
                            st.rerun()
                with col2:
                    new_status = not book['read_status']
                    status_label = "✅ Mark as Completed" if not book['read_status'] else "⏳ Mark as To Read"
                    if st.button(status_label, key=f"status_{i}", use_container_width=True):
                        st.session_state.book_collection[i]['read_status'] = new_status
                        persist_library_data()
                        st.rerun()

    if st.session_state.book_deleted_flag:
        st.markdown("<div class='success-message'>🗑️ Title removed from your collection!</div>", unsafe_allow_html=True)
        st.session_state.book_deleted_flag = False

# Search Books View
elif st.session_state.active_section == "search":
    st.markdown("<h2 class='sub-header'>🔍 Discover Titles</h2>", unsafe_allow_html=True)

    search_by = st.selectbox("🔍 Search by", ["📖 Title", "✍️ Author", "🏷️ Category"])
    search_term = st.text_input("🔎 Enter search term")

    if st.button("🔍 Search", use_container_width=False):
        if search_term:
            with st.spinner("🔍 Exploring your collection..."):
                find_books(search_term, search_by)
                time.sleep(0.5)

    if hasattr(st.session_state, 'search_output'):
        if st.session_state.search_output:
            st.markdown(f"<h3>✨ Found {len(st.session_state.search_output)} Matches</h3>", unsafe_allow_html=True)

            for i, book in enumerate(st.session_state.search_output):
                st.markdown(f"""
                <div class='book-card'>
                    <h3>📖 {book['title']}</h3>
                    <p><strong>✍️ Author:</strong> {book['author']}</p>
                    <p><strong>📅 Published:</strong> {book['publication_year']}</p>
                    <p><strong>🏷️ Category:</strong> {book['genre']}</p>
                    <p><span class="{'read-badge' if book['read_status'] else 'unread-badge'}">{"✅ Completed" if book['read_status'] else "⏳ To Read"}</span></p>
                </div>
                """, unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>🔍 No matches found. Try a different search term.</div>", unsafe_allow_html=True)

# Library Statistics View
elif st.session_state.active_section == "stats":
    st.markdown("<h2 class='sub-header'>📊 Reading Insights</h2>", unsafe_allow_html=True)

    if not st.session_state.book_collection:
        st.markdown("<div class='warning-message'>📚 Your collection is empty. Start adding some titles!</div>", unsafe_allow_html=True)
    else:
        stats = compute_library_metrics()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📚 Total Titles", value=stats['total_books'])
        with col2:
            st.metric("✅ Completed", value=stats['read_books'])
        with col3:
            st.metric("📈 Completion Rate", f"{stats['percent_read']:.1f}%")

        generate_visualizations(stats)

        if stats['authors']:
            st.markdown("<h3>👤 Favorite Authors</h3>", unsafe_allow_html=True)
            top_authors = dict(list(stats['authors'].items())[:5])
            for author, count in top_authors.items():
                st.markdown(f"**{author}**: {count} title{'s' if count > 1 else ''}")
