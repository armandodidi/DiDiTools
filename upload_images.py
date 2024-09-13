import os
import requests
import time
import json

dir_url = "./localsite/auxapp/static"

def resize_images_in_directory(directory):
    final_json = {}
    # for filename in os.listdir(directory):
    for filename in os.listdir(directory):
        url = "https://openapi.didi-food.com/v3/image/image/uploadImage"
        payload = {'auth_token': 'NjZmYzkxNjMwZDIyNzQ3OWE5YWRmNjFjYjZiZGEyZjA=', 'ext': f'{filename}'}
        files=[
            ('image_file',(filename,open(os.path.join(directory, filename),'rb'),'image/png'))
        ]
        headers = {}
        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        data = response.json()
        
        if "giftKey" in data["data"]:
            final_json[filename] = data["data"]["giftKey"]
        else:
            final_json[filename] = ""

        time.sleep(2)

    print(final_json)
    with open("images.json", "w", encoding='utf-8') as outfile:
        outfile.write(json.dumps(final_json, indent=4, ensure_ascii=False))

resize_images_in_directory(dir_url)