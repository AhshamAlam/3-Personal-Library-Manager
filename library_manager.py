# Import necessary libraries
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
import requests

# Configure Streamlit page settings
st.set_page_config(
    page_title="Personal Library Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .sub-header {
        font-size: 2rem !important;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .success-message {
        padding: 1rem;
        background-color: #ECFDF3;
        border-left: 4px solid #10B981;
        border-radius: 0.375rem;
    }
    
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        border-radius: 0.375rem;
    }

    .book-card {
        padding: 1rem;
        background-color: #F3F4F6;
        border-left: 4px solid #3B82F6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .read-badge {
        padding: 0.25rem 0.75rem;
        background-color: #10B981;
        color: white;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .unread-badge {
        padding: 0.25rem 0.75rem;
        background-color: #F87171;
        color: white;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .action-button {
        margin-right: 0.5rem;
    }

    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animation from URL with better error handling
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            st.warning("Could not load animation. Using default animation.")
            return None
    except Exception as e:
        st.warning(f"Error loading animation: {str(e)}")
        return None

# Initialize session state variables
if 'library' not in st.session_state:
    st.session_state.library = []               
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'

# Function to load library data from JSON file
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
                return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Function to save library data to JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Function to add a new book to the library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Function to remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Function to search books based on criteria
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in str(book['genre']):
            results.append(book)
    st.session_state.search_results = results

# Function to calculate library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items(), key=lambda x: x[0]))
    }

# Function to create visualizations for library statistics
def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171'],
        )])
        fig_read_status.update_layout(title_text='Read vs Unread Books', height=400)
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['genres']:
        genres_df = pd.DataFrame({'Genre': list(stats['genres'].keys()), 'Count': list(stats['genres'].values())})
        fig_genres = px.bar(genres_df, x='Genre', y='Count', color='Count', color_continuous_scale=px.colors.sequential.Blues)
        fig_genres.update_layout(title_text='Books by Genre', height=400)
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        decades_df = pd.DataFrame({'Decade': [f'{dec}s' for dec in stats['decades'].keys()], 'Count': list(stats['decades'].values())})
        fig_decades = px.line(decades_df, x='Decade', y='Count', markers=True, line_shape='spline')
        fig_decades.update_layout(title_text='Books by Publication Decade', height=400)
        st.plotly_chart(fig_decades, use_container_width=True)

# Load library data
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>Navigation</h1>", unsafe_allow_html=True)
nav_options = st.sidebar.radio("Choose an option", ["View Library", "Add Book", "Search Books", "Library Statistics"])

st.session_state.current_view = nav_options.lower().replace(" ", "")

st.markdown("<h1 class='main-header'>Personal Library Manager</h1>", unsafe_allow_html=True)

if st.session_state.current_view == "addbook":
    st.markdown("<h2 class='sub-header'>Add a new book</h2>", unsafe_allow_html=True)

    with st.form(key="add_book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)
        with col2:
            genre = st.selectbox("Genre", ["Programming", "JavaScript", "Software Engineering", "Sci-Fi", "Fantasy", "Non-Fiction", "Romance", "Mystery", "Thriller", "Biography"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        submit_button = st.form_submit_button(label="Add Book")
        if submit_button:
            add_book(title, author, publication_year, genre, read_bool)

    if st.session_state.book_added:
        st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
        st.session_state.book_added = False
