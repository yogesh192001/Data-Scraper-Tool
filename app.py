from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

app = Flask(__name__)

# Scraping Function
def scrape_google_business(query, num_results=10):
    """
    Scrapes Google search results for business-related data.

    Parameters:
        query (str): Search query.
        num_results (int): Number of results to fetch.

    Returns:
        list[dict]: Scraped data with name, location, contact details, and industry.
    """
    base_url = "https://www.google.com/search"
    params = {"q": query, "num": num_results}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for business in soup.select(".tF2Cxc"):
        name = business.select_one(".DKV0Md").text if business.select_one(".DKV0Md") else "N/A"
        link = business.select_one(".yuRUbf a")["href"] if business.select_one(".yuRUbf a") else "N/A"
        snippet = business.select_one(".IsZvec").text if business.select_one(".IsZvec") else "N/A"
        location_element = business.select_one(".LrzXr")
        location = location_element.text if location_element else "N/A"
        contact_details_element = business.select_one(".LrzXr")
        contact_details = contact_details_element.text if contact_details_element else "N/A"

        results.append({
            "Name": name,
            "Link": link,
            "Snippet": snippet,
            "Location": location,
            "Contact Details": contact_details,
        })

    return results

# Cleaning Function
def clean_data(data):
    df = pd.DataFrame(data)
    df.drop_duplicates(inplace=True)
    df.fillna("N/A", inplace=True)
    df = df.applymap(lambda x: x.strip().title() if isinstance(x, str) else x)
    return df

# Flask Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    num_results = int(request.form.get("num_results", 10))

    # Scrape data
    scraped_data = scrape_google_business(query, num_results)
    if not scraped_data:
        return "No data scraped. Please try a different query."

    # Clean data
    cleaned_data = clean_data(scraped_data)

    # Save to CSV
    output_file = "scraped_data.csv"
    cleaned_data.to_csv(output_file, index=False)

    return send_file(output_file, as_attachment=True)

# Run the Application
if __name__ == "__main__":
    app.run(debug=True)
