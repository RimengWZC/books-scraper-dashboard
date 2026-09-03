import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st


# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="Book Market Explorer",
    page_icon="📚",
    layout="wide"
)


# ============================================
# Header
# ============================================

st.title("📚 Book Market Explorer")

st.markdown(
    """
    A web scraping and data analysis project built with
    **Python, Requests, BeautifulSoup, Pandas, and Streamlit**.

    This dashboard collects book information from the
    **Books to Scrape** website and analyzes the catalog
    across multiple pages.
    """
)


# ============================================
# Scraping Function
# ============================================

@st.cache_data
def scrape_books():

    base_url = "https://books.toscrape.com/catalogue/page-{}.html"

    data = []

    # Scrape 50 pages
    for page in range(1, 51):

        url = base_url.format(page)

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        books = soup.find_all(
            "article",
            class_="product_pod"
        )

        for book in books:

            # -----------------------------
            # Title
            # -----------------------------

            title = book.find(
                "h3"
            ).find(
                "a"
            )["title"]


            # -----------------------------
            # Price
            # -----------------------------

            price_text = book.find(
                "p",
                class_="price_color"
            ).text.strip()

            price = float(
                re.search(
                    r"\d+(?:\.\d+)?",
                    price_text
                ).group()
            )


            # -----------------------------
            # Rating
            # -----------------------------

            rating = book.find(
                "p",
                class_="star-rating"
            )["class"][1]


            # -----------------------------
            # Availability
            # -----------------------------

            availability = book.find(
                "p",
                class_="instock"
            ).text.strip()


            # -----------------------------
            # Product URL
            # -----------------------------

            relative_url = book.find(
                "h3"
            ).find(
                "a"
            )["href"]

            product_url = (
                "https://books.toscrape.com/catalogue/"
                + relative_url.replace("../", "")
            )


            # -----------------------------
            # Store Data
            # -----------------------------

            data.append(
                {
                    "Title": title,
                    "Price": price,
                    "Rating": rating,
                    "Availability": availability,
                    "URL": product_url
                }
            )


    return pd.DataFrame(data)


# ============================================
# Run Scraper
# ============================================

with st.spinner("Scraping book catalog..."):

    try:

        df = scrape_books()

    except Exception as e:

        st.error(
            f"Unable to retrieve data: {e}"
        )

        st.stop()


# ============================================
# Data Processing
# ============================================

rating_map = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

df["Rating Number"] = df[
    "Rating"
].map(rating_map)


total_books = len(df)

average_price = df[
    "Price"
].mean()

median_price = df[
    "Price"
].median()

average_rating = df[
    "Rating Number"
].mean()


# ============================================
# KPI Metrics
# ============================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📚 Books Scraped",
        f"{total_books:,}"
    )

with col2:

    st.metric(
        "💰 Average Price",
        f"£{average_price:.2f}"
    )

with col3:

    st.metric(
        "📊 Median Price",
        f"£{median_price:.2f}"
    )

with col4:

    st.metric(
        "⭐ Average Rating",
        f"{average_rating:.1f} / 5"
    )


st.divider()


# ============================================
# Sidebar Filters
# ============================================

st.sidebar.header("🔎 Filters")


# Rating filter

rating_options = [
    "All",
    "One",
    "Two",
    "Three",
    "Four",
    "Five"
]

selected_rating = st.sidebar.selectbox(
    "Rating",
    rating_options
)


# Price range

min_price = float(
    df["Price"].min()
)

max_price = float(
    df["Price"].max()
)

price_range = st.sidebar.slider(
    "Price Range (£)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)


# Search

search_term = st.sidebar.text_input(
    "Search by title"
)


# Sort

sort_option = st.sidebar.selectbox(
    "Sort by",
    [
        "Price: Low to High",
        "Price: High to Low",
        "Rating: High to Low",
        "Title: A to Z"
    ]
)


# ============================================
# Apply Filters
# ============================================

filtered_df = df.copy()


# Rating

if selected_rating != "All":

    filtered_df = filtered_df[
        filtered_df["Rating"]
        == selected_rating
    ]


# Price

filtered_df = filtered_df[
    (filtered_df["Price"] >= price_range[0])
    &
    (filtered_df["Price"] <= price_range[1])
]


# Search

if search_term:

    filtered_df = filtered_df[
        filtered_df["Title"]
        .str.contains(
            search_term,
            case=False,
            na=False
        )
    ]


# Sorting

if sort_option == "Price: Low to High":

    filtered_df = filtered_df.sort_values(
        "Price",
        ascending=True
    )

elif sort_option == "Price: High to Low":

    filtered_df = filtered_df.sort_values(
        "Price",
        ascending=False
    )

elif sort_option == "Rating: High to Low":

    filtered_df = filtered_df.sort_values(
        "Rating Number",
        ascending=False
    )

else:

    filtered_df = filtered_df.sort_values(
        "Title"
    )


# ============================================
# Results Table
# ============================================

st.subheader("📖 Book Catalog")

st.write(
    f"Showing **{len(filtered_df):,}** books"
)


display_df = filtered_df[
    [
        "Title",
        "Price",
        "Rating",
        "Availability"
    ]
].copy()


display_df["Price"] = display_df[
    "Price"
].apply(
    lambda x: f"£{x:.2f}"
)


display_df["Rating"] = display_df[
    "Rating"
].map(
    {
        "One": "⭐",
        "Two": "⭐⭐",
        "Three": "⭐⭐⭐",
        "Four": "⭐⭐⭐⭐",
        "Five": "⭐⭐⭐⭐⭐"
    }
)


display_df = display_df.rename(
    columns={
        "Title": "Book Title"
    }
)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================
# Analytics
# ============================================

st.divider()

st.subheader("📊 Catalog Analytics")


# Rating distribution

rating_counts = (
    df["Rating Number"]
    .value_counts()
    .sort_index()
)

rating_counts.index = [
    f"{int(x)} Stars"
    for x in rating_counts.index
]


st.write("### ⭐ Rating Distribution")

st.bar_chart(
    rating_counts
)


# Price distribution

st.write("### 💰 Price Distribution")

price_bins = pd.cut(
    df["Price"],
    bins=10
)

price_distribution = (
    price_bins
    .value_counts()
    .sort_index()
)

price_distribution.index = (
    price_distribution.index.astype(str)
)

st.bar_chart(
    price_distribution
)


# ============================================
# Project Information
# ============================================

st.divider()

st.subheader("🛠️ About This Project")

st.markdown(
    """
    **Technologies**

    - Python
    - Requests
    - BeautifulSoup
    - Pandas
    - Streamlit

    **Goal**

    This is my first web scraping project, and I’m using it
    to get hands-on experience with scraping, data cleaning,
    and building simple interactive apps.

    **Data Source**

    Books to Scrape (a website made for practicing web scraping).
    """
)


st.caption(
    "Portfolio project — Web Scraping & Data Analytics"
)
