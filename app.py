from flask import Flask, request, jsonify
import requests
import statistics

app = Flask(__name__)

# Function to query Vinted API for a given search term
def fetch_vinted_listings(search_query, page=1, per_page=50):
    url = "https://www.vinted.com/api/v2/catalog/items"
    params = {
        "search_text": search_query,
        "page": page,
        "per_page": per_page,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to extract prices from listings with optional condition filtering
def extract_prices(data, condition_filter=None):
    if not data or 'items' not in data:
        return []
    prices = []
    for item in data['items']:
        price = item.get('price', {}).get('amount')
        condition = item.get('status')
        if price and (not condition_filter or condition in condition_filter):
            prices.append(float(price))
    return prices

# Function to remove outliers using IQR (Interquartile Range) method
def remove_outliers(prices):
    if not prices:
        return prices
    q1 = statistics.quantiles(prices, n=4)[0]
    q3 = statistics.quantiles(prices, n=4)[2]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [price for price in prices if lower_bound <= price <= upper_bound]

# API route to get average sell price
@app.route('/average-price', methods=['GET'])
def average_price():
    search_query = request.args.get('query')
    condition_filter = request.args.getlist('condition')  # can pass multiple conditions
    page_limit = int(request.args.get('pages', 2))  # default to 2 pages
    per_page = int(request.args.get('per_page', 50))  # default to 50 items per page
    remove_outliers_flag = request.args.get('remove_outliers', 'false').lower() == 'true'

    if not search_query:
        return jsonify({"error": "Missing 'query' parameter."}), 400

    all_prices = []

    for page in range(1, page_limit + 1):
        data = fetch_vinted_listings(search_query, page, per_page)
        prices = extract_prices(data, condition_filter)
        all_prices.extend(prices)

    if not all_prices:
        return jsonify({"error": "No prices found for query."}), 404

    if remove_outliers_flag:
        all_prices = remove_outliers(all_prices)

    if not all_prices:
        return jsonify({"error": "No prices left after outlier removal."}), 404

    average = round(statistics.mean(all_prices), 2)
    return jsonify({
        "query": search_query,
        "average_price": average,
        "listings_found": len(all_prices),
        "condition_filter": condition_filter,
        "outliers_removed": remove_outliers_flag
    })

if __name__ == '__main__':
    app.run(debug=True)