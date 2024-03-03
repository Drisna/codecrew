from flask import Flask, request, jsonify, render_template,redirect,url_for
from bs4 import BeautifulSoup
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
@app.route('/')
def index():
    return render_template('afront.html')
@app.route('/home')
def home():
    return redirect(url_for(".search"))

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/result')
def result():
    return render_template('result.html')

def scrape_amazon(product):
    products = []
    amazon_url = f"https://www.amazon.in/s?k={product.replace(' ', '+')}"
    response = requests.get(amazon_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all(class_='s-result-item')
        for result in results:
            name = result.find(class_='a-text-normal')
            price = result.find(class_='a-price-whole')
            image = result.find('img')['src'] if result.find('img') else None
            if name and price:
                products.append({'retailer': 'Amazon', 'name': name.text.strip(), 'price': price.text.strip(), 'image': image})
    return products

def scrape_flipkart(product):
    products = []
    flipkart_url = f"https://www.flipkart.com/search?q={product.replace(' ', '%20')}"
    response = requests.get(flipkart_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all(class_='s-include-content-margin')
        for result in results:
            name = result.find(class_='s-title')
            price = result.find(class_='_30jeq3')
            image = result.find('img')['src'] if result.find('img') else None
            if name and price:
                products.append({'retailer': 'Flipkart', 'name': name.text.strip(), 'price': price.text.strip(), 'image': image})
    return products

def get_prices(product):
    amazon_products = scrape_amazon(product)
    flipkart_products = scrape_flipkart(product)
    all_products = amazon_products + flipkart_products
    min_price = min([float(product['price'].replace(',', '')) for product in all_products])
    min_price_product = [product for product in all_products if float(product['price'].replace(',', '')) == min_price][0]
    return min_price_product



@app.route('/api/search', methods=['GET'])
def search1():
    product = request.args.get('product')
    if not product:
        return jsonify({'error': 'Product keyword is required'}), 400
    product_info = get_prices(product)
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(debug=True)
