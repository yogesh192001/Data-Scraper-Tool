from flask import Flask, request, send_file
import requests
from bs4 import BeautifulSoup
import csv
import os

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return "Query is required", 400

    # Fetch search results (example: using Wikipedia)
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "No results found", 404

    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    topic_header = soup.find('h1').text
    content = soup.find('p').text  # Fetch first paragraph as basic info

    # Save data to CSV
    csv_file = 'results.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Topic Header', 'Location', 'Basic Info'])
        writer.writerow([topic_header, url, content])

    # Return CSV file
    return send_file(csv_file, as_attachment=True, mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
