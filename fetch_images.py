import requests
import json
import os
from PIL import Image
from io import BytesIO

errors = []

with open('./manifest.json', 'r', encoding="utf8") as f:
    data = json.load(f)

for idx, book in enumerate(data):
    cover_path = book['image_paths'][0]

    try:
        response = requests.get(book['image_urls'][0])
        # open(cover_path, "wb").write(response.content)

        image = Image.open(BytesIO(response.content))
        image = image.convert('RGB')

        book['image_paths'][0] = f"{os.path.splitext(cover_path)[0]}.webp"
        image.save(book['image_paths'][0], 'webp')


        print(f"Progress: {idx+1}/{len(data)}")

    except:
        errors.append(book['image_urls'][0])
        print("Failed to fetch cover!")

print(f"Stats: {len(data) - len(errors)} completed, {len(errors)} errors")

for i, error in enumerate(errors):
    print(f"Error ({i}): {error}")

with open("./manifest.json", "w", encoding="utf8") as outfile:
    json.dump(data, outfile)