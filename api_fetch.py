from email import header
import json
import requests
import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()

ENV_API_SECRET = os.getenv('API_SECRET')

if not ENV_API_SECRET:
    raise TypeError("A valid API secret is required!")

ENV_API_ENDPOINT = os.getenv('API_ENDPOINT')

if not ENV_API_ENDPOINT:
    raise TypeError("A valid API enpoint is required!")

errors = []

header = {"x-api-key": ENV_API_SECRET}

with open(f'./manifest.json', 'r', encoding="utf8") as f:
    data = json.load(f)

for idx, book in enumerate(data):
    cover_path = book['image_paths'][0]
    
    try:
        with open(cover_path, "rb") as img_file:
            b64_string = base64.b64encode(img_file.read())

        book_details = json.dumps({
            "title": book['title'],
            "author": book['author'],
            "publisher": book['publisher'],
            "color_palette": book['color_palette'],
            "cover_image": "data:image/webp;base64," + b64_string.decode('utf-8')
        })

        response = requests.post(ENV_API_ENDPOINT, headers=header, json=book_details)

        if (response.status_code != 200):
            errors.append(f"API: {response.status_code} - {response.json()} | {book['title']}")
            print(f"{response.status_code} - {response.json()}")

    except:
        errors.append(book['title'])
        print("Failed to read book!")

    print(f"Progress: {idx+1}/{len(data)}")
    time.sleep(.1)


print(f"Stats: {len(data) - len(errors)} completed, {len(errors)} errors")

for i, error in enumerate(errors):
    print(f"Error ({i}): {error}")
