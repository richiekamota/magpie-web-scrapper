from selenium import webdriver
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def scrape_magpie_products(url):
    driver = webdriver.Chrome()  
    driver.get(url)
    
    # Get the page source from Selenium
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    products = []
    seen_products = set()  # To track unique products

    # Find all product containers
    product_containers = soup.find_all('div', class_='product')

    for container in product_containers:
        # Extract product title and capacity
        title_element = container.find('h3', class_='text-blue-600')
        title = title_element.text.strip() if title_element else None

        capacity_element = container.find('p', class_='product-capacity')
        capacity_mb = None
        if capacity_element:
            capacity_str = capacity_element.text.strip().replace('GB', '')
            try:
                capacity_mb = int(capacity_str) * 1000  # Convert GB to MB
            except ValueError:
                capacity_mb = None

        # Extract price
        price_element = container.find('p', class_='text-lg')
        price = None
        if price_element:
            price_str = price_element.text.strip()
            price_str = ''.join(filter(str.isdigit, price_str))
            price = float(price_str) if price_str else None

        # Extract image URL
        img_element = container.find('img')
        image_url = None
        if img_element and img_element['src']:
            image_url = 'https://www.magpiehq.com/developer-challenge/smartphones/' + img_element['src'].replace('..', '')

        # Extract colors
        color_elements = container.find_all('span', {'data-colour': True})
        colors = [color_element['data-colour'] for color_element in color_elements] if color_elements else []

        # Extract availability
        availability_element = container.find('div', class_='bg-white').find_all('div')[2]
        availability_text = availability_element.text.strip() if availability_element else None
        is_available = "In Stock" in availability_text if availability_text else False

        # Extract shipping information
        shipping_element = container.find('div', class_='bg-white').find_all('div')[-1]
        shipping_text = shipping_element.text.strip() if shipping_element else None
        shipping_date = None
        if shipping_text:
            # Extract shipping date using regex
            date_match = re.search(r'(\d{2}(?:st|nd|rd|th) \w+ \d{4})', shipping_text)
            if date_match:
                try:
                    shipping_date = datetime.strptime(date_match.group(0), "%dth %B %Y").strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Create a separate product entry for each color
        for color in colors:
            # Create a unique key for each product variant (title + capacity + color)
            product_key = f"{title} {capacity_mb} {color}"
            if product_key not in seen_products:
                seen_products.add(product_key)

                product = {
                    'title': f"{title} {capacity_mb}MB" if title and capacity_mb else title,
                    'price': price,
                    'imageUrl': image_url,
                    'capacityMB': capacity_mb,
                    'colour': color,
                    'availabilityText': availability_text,
                    'isAvailable': is_available,
                    'shippingText': shipping_text,
                    'shippingDate': shipping_date
                }
                products.append(product)

    driver.quit()
    return products

def main():
    url = "https://www.magpiehq.com/developer-challenge/smartphones"
    products = scrape_magpie_products(url)

    # Output the scraped products to a JSON file
    with open('output.json', 'w') as f:
        json.dump(products, f, indent=4)

if __name__ == "__main__":
    main()
