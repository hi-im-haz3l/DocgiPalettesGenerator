from email import header
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ENV_API_SECRET = os.getenv('API_SECRET')

if not ENV_API_SECRET:
    raise TypeError("A valid API credential is required!")

api_endpoint = "http://10.0.0.2:3000/api/books-dump"

header = {"x-api-key": ENV_API_SECRET}

book_details = {"title":"Phép tính của một nho sĩ","author":"Trần Vũ","publisher":"Hội nhà văn","image_urls":["http://static.nhanam.com.vn/thumb/0x0/crop/Books/Images/2019/2/25/WPCVSY9L.jpg"],"image_paths":["images/f3eab5a1b5322f60d1ccb57e77f4262ad24d5fc8.jpg"],"color_palette":[{"primary1":"rgb(162, 101, 49)"},{"primary2":"rgb(122, 75, 41)"},{"accent":"rgb(234, 203, 153)"}]}

cover_image = {"cover_image": ('f3eab5a1b5322f60d1ccb57e77f4262ad24d5fc8.jpg', open(book_details['image_paths'][0], "rb"), 'image/jpeg')}

response = requests.post(api_endpoint, headers=header, data=book_details, files=cover_image)

print(response.json())

print(response.status_code)
