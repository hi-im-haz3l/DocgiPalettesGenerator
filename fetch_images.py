import requests
import json
import os
from PIL import Image
from io import BytesIO

errors = []

input_path = input("input json file: ")

with open(f'./{input_path}', 'r', encoding="utf8") as f:
    data = json.load(f)

for idx, book in enumerate(data):
    cover_path = book['image_paths'][0]

    response = requests.get(book['image_urls'][0])
    # open(cover_path, "wb").write(response.content)

    image = Image.open(BytesIO(response.content))
    image = image.convert('RGB')

    book['image_paths'][0] = f"images/{os.path.basename(cover_path).split('.', 1)[0]}.webp"
    image.save(book['image_paths'][0], 'webp')


    print(f"Progress: {idx+1}/{len(data)}")


print(f"Stats: {len(data) - len(errors)} completed, {len(errors)} errors")

for i, error in enumerate(errors):
    print(f"Error ({i}): {error}")

with open("./manifest.json", "w", encoding="utf8") as outfile:
    json.dump(data, outfile)