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
    page_title="Personal Library Manager",  # Title of the page
    layout="wide",  # Use a wide layout
    initial_sidebar_state="expanded"  # Open the sidebar initially
)

# Custom CSS for styling the application
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Subheader styling */
    .sub-header {
        font-size: 2rem !important;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Success and warning messages styling */
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

    /* Book card styling */
    .book-card {
        padding: 1rem;
        background-color: #F3F4F6;
        border-left: 4px solid #3B82F6;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .book-card:hover {
        transform: translateY(-5px);  /* Adds hover effect */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Read and unread badges */
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

    /* Button styling */
    .action-button {
        margin-right: 0.5rem;
    }

    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables for managing the library state
if 'library' not in st.session_state:
    st.session_state.library = []  # List to store book data
if 'search_results' not in st.session_state:
    st.session_state.search_results = []  # List to store search results
if 'book_added' not in st.session_state:
    st.session_state.book_added = False  # Boolean to track book addition
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False  # Boolean to track book removal
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'library'  # Default view set to 'library'

# Function to load library data from a JSON file
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)  # Load the book data into session state
                return True
        return False  # Return False if file doesn't exist
    except Exception as e:
        st.error(f"Error loading library: {e}")  # Display error message
        return False

# Function to save library data to a JSON file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)  # Save the book data to the file
            return True
    except Exception as e:
        st.error(f"Error saving library: {e}")  # Display error message
        return False

# Function to add a new book to the library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Store the current date as the added date
    }
    st.session_state.library.append(book)  # Add the book to the library
    save_library()  # Save the updated library
    st.session_state.book_added = True  # Set book added status to True
    time.sleep(0.5)  # Add a small delay

# Function to remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]  # Delete the book from the list
        save_library()  # Save the updated library
        st.session_state.book_removed = True  # Set book removed status to True
        return True
    return False  # Return False if index is out of range

# Function to search books based on search criteria
def search_books(search_term, search_by):
    search_term = search_term.lower()  # Convert search term to lowercase for case-insensitive search
    results = []

    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in str(book['genre']):
            results.append(book)
    st.session_state.search_results = results  # Store search results in session state

# Function to calculate library statistics (total books, read books, etc.)
def get_library_stats():
    total_books = len(st.session_state.library)  # Total number of books
    read_books = sum(1 for book in st.session_state.library if book['read_status'])  # Count of read books
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0  # Percentage of read books

    genres = {}
    authors = {}
    decades = {}

    # Loop through books to calculate statistics by genre, author, and publication decade
    for book in st.session_state.library:
        # Count genres
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        
        # Count authors
        authors[book['author']] = authors.get(book['author'], 0) + 1

        # Count books by decade
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    # Sort statistics by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Function to create visualizations for library statistics
def create_visualizations(stats):
    # Pie chart for read vs unread books
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=0.4,
            marker_colors=['#10B981', '#F87171'],
        )])
        fig_read_status.update_layout(
            title_text='Read vs Unread Books',
            showlegend=True,
            height=400,
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
    
    # Bar chart for genres
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df,
            x='Genre',
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues,
        )
        fig_genres.update_layout(
            title_text='Books by Genre',
            xaxis_title='Genre',
            yaxis_title='Number of Books',
            height=400,
        )
        st.plotly_chart(fig_genres, use_container_width=True)

    # Line chart for decades
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f'{decade}s' for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df,
            x='Decade',
            y='Count',
            markers=True,
            line_shape='linear',
            title='Books by Decade',
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Function to render the library page
def render_library():
    st.markdown("<h1 class='main-header'>My Personal Library</h1>", unsafe_allow_html=True)
    
    stats = get_library_stats()  # Get library statistics
    create_visualizations(stats)  # Generate and display visualizations

    # Display book list
    st.subheader("Library Collection")
    if len(st.session_state.library) > 0:
        for i, book in enumerate(st.session_state.library):
            read_status = "Read" if book['read_status'] else "Unread"
            st.markdown(f"""
                <div class="book-card">
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class="{ 'read-badge' if book['read_status'] else 'unread-badge' }">{read_status}</span></p>
                    <button class="stButton" style="background-color: #FF5C5C;" onclick="remove_book({i})">Remove</button>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No books found in your library.")

# Function to render the search page
def render_search():
    st.markdown("<h1 class='main-header'>Search for Books</h1>", unsafe_allow_html=True)

    search_term = st.text_input("Search term")
    search_by = st.selectbox("Search by", ["Title", "Author", "Genre"])

    if search_term:
        search_books(search_term, search_by)  # Search books
        st.subheader(f"Results for '{search_term}' in {search_by}")

        if len(st.session_state.search_results) > 0:
            for book in st.session_state.search_results:
                st.markdown(f"""
                    <div class="book-card">
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class="{ 'read-badge' if book['read_status'] else 'unread-badge' }">{"Read" if book['read_status'] else "Unread"}</span></p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No results found.")
