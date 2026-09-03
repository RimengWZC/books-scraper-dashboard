import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st


# ============================================
# Page Settings
# ============================================

st.set_page_config(
    page_title="Books Scraper",
    page_icon="📚"
)

st.title("📚 Books to Scrape Dashboard")
st.write("A simple web scraping project built with Python.")


# ============================================
# Scrape Website
# ============================================

url = "https://books.toscrape.com/"

response = requests.get(url)

if response.status_code == 200:

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.find_all(
        "article",
        class_="product_pod"
    )

    data = []

    for book in books:

        title = book.find("h3").find("a")["title"]

        price = book.find(
            "p",
            class_="price_color"
        ).text.strip()

        rating = book.find(
            "p",
            class_="star-rating"
        )["class"][1]

        availability = book.find(
            "p",
            class_="instock"
        ).text.strip()

        data.append({
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Availability": availability
        })

    df = pd.DataFrame(data)

else:

    st.error(
        f"Failed to access website. "
        f"Status code: {response.status_code}"
    )


# ============================================
# Display Results
# ============================================

st.subheader("Scraping Results")

st.write(f"Successfully scraped **{len(df)} books**.")

st.dataframe(
    df,
    use_container_width=True
)