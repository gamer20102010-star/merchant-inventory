import csv
import xml.etree.ElementTree as ET
import urllib.request

# НАЛАШТУВАННЯ
FEED_URL = "https://zadavaka.net/marketplace-integration/google-feed/0433240f7f1dfb0e6d80da0eb96a7dde?langId=3"
STORE_CODE = "14608689277009241074"
OUTPUT_FILE = "local_inventory.csv"

def get_tag_text(elem, tag_name):
    # Шукаємо тег з простором імен Google або без нього через явну перевірку is None
    child = elem.find(f".//{{http://base.google.com/ns/1.0}}{tag_name}")
    if child is None:
        child = elem.find(f".//{tag_name}")
    if child is not None and child.text:
        return child.text.strip()
    return ""

def process_feed():
    print("Завантаження та обробка XML-фіду...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    request = urllib.request.Request(FEED_URL, headers=headers)
    req = urllib.request.urlopen(request)
    
    csv_columns = ["id", "store_code", "quantity", "price", "availability"]
    
    item_count = 0
    total_parsed = 0
    
    with open(OUTPUT_FILE, mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
        writer.writeheader()
        
        for event, elem in ET.iterparse(req, events=("end",)):
            if elem.tag.endswith("item"):
                total_parsed += 1
                
                item_id = get_tag_text(elem, "id")
                if not item_id:
                    elem.clear()
                    continue
                
                availability = get_tag_text(elem, "availability").lower()
                
                # Беремо товари в наявності
                if availability == "in stock":
                    # Спочатку беремо акційну ціну, якщо її немає — звичайну
                    price = get_tag_text(elem, "sale_price")
                    if not price:
                        price = get_tag_text(elem, "price")
                    
                    if price:
                        writer.writerow({
                            "id": item_id,
                            "store_code": STORE_CODE,
                            "quantity": 1,
                            "price": price,
                            "availability": "in_stock"
                        })
                        item_count += 1
                
                elem.clear()

    print(f"Готово! Переглянуто товарів: {total_parsed}, записано в CSV: {item_count}")

if __name__ == "__main__":
    process_feed()