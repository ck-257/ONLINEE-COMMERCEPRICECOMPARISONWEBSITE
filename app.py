from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Replace with your actual API keys
amazon_api_key = "ccb10b315emsh858ae6d3b8f45b1p12e347jsnec96427d91c3"
flipkart_api_key = 'ccb10b315emsh858ae6d3b8f45b1p12e347jsnec96427d91c3'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        amazon_results = fetch_amazon_data(query)
        flipkart_results = fetch_flipkart_data(query)
        
        # Calculate average price and ratings for Amazon and Flipkart results
        amazon_avg_price = calculate_average_price(amazon_results)
        flipkart_avg_price = calculate_average_price(flipkart_results)
        
        amazon_avg_rating = calculate_average_rating(amazon_results)
        flipkart_avg_rating = calculate_average_rating(flipkart_results)
        
        # Determine which site has the lower average price
        if amazon_avg_price < flipkart_avg_price:
            lowest_price_site = 'Amazon'
        else:
            lowest_price_site = 'Flipkart'
        
        # Determine which site has the higher average rating
        if amazon_avg_rating > flipkart_avg_rating:
            highest_rating_site = 'Amazon'
        else:
            highest_rating_site = 'Flipkart'
        
        return render_template('results.html', 
                               amazon_results=amazon_results, 
                               flipkart_results=flipkart_results,
                               amazon_avg_price=amazon_avg_price,
                               flipkart_avg_price=flipkart_avg_price,
                               amazon_avg_rating=amazon_avg_rating,
                               flipkart_avg_rating=flipkart_avg_rating,
                               lowest_price_site=lowest_price_site,
                               highest_rating_site=highest_rating_site)
    return render_template('index.html')

def fetch_amazon_data(query):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    querystring = {
        "query": query,
        "page": "1",
        "country": "IN",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL"
    }
    headers = {
        "x-rapidapi-key": amazon_api_key,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json().get("data", {}).get("products", [])
        products = []
        for item in data:
            # Check if product_price is present and not None
            if 'product_price' in item and item['product_price'] is not None:
                # Clean price string: remove currency symbol, commas, and any non-numeric characters
                price = ''.join(filter(str.isdigit, item['product_price']))
            else:
                price = '0'  # Default to '0' or any other value you prefer
            
            product = {
                'title': item.get('product_title', ''),
                'price': price,
                'mrp': item.get('product_original_price', ''),
                'rating': item.get('product_star_rating', ''),
                'image_url': item.get('product_photo', ''),
                'product_url': item.get('product_url', '')
            }
            products.append(product)
        return products
    else:
        return []


def fetch_flipkart_data(query):
    url = "https://real-time-flipkart-api.p.rapidapi.com/product-search"
    querystring = {"q": query, "page": "1", "sort_by": "popularity"}
    headers = {
        "x-rapidapi-key": flipkart_api_key,
        "x-rapidapi-host": "real-time-flipkart-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        formatted_products = []
        for product in products:
            # Clean price string: remove currency symbol, commas, and any non-numeric characters
            price = ''.join(filter(str.isdigit, str(product.get('price', '0'))))
            images = product.get('images', [])
            formatted_product = {
                'title': product.get('title', ''),
                'price': price,
                'mrp': product.get('mrp', ''),
                'rating': product.get('rating', {}).get('average', ''),
                'image_url': images[0] if images else None,
                'product_url': product.get('url', '')
            }
            formatted_products.append(formatted_product)
        return formatted_products
    else:
        return []

def calculate_average_price(products):
    if not products:
        return 0.0
    
    total_price = sum(float(product['price']) for product in products if product['price'].isdigit())
    return total_price / len(products)

def calculate_average_rating(products):
    if not products:
        return 0.0
    
    total_rating = sum(float(product['rating']) for product in products if product['rating'])
    return total_rating / len(products)

if __name__ == '__main__':
    app.run(debug=True)
