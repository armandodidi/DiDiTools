import pandas as pd
import json
import string
import random

class CreateJSON:
    BRAND_NAME = "Musi"
    FILE_NAME = "Musi10"
    URL_DOMAIN = "https://respectful-alligator.static.domains/MySite/static/"
    IS_TOBACCO_BRAND = False
    IS_WINE_BRAND = False
    SHEET_POSITION = 0
    # Suply categories
    DEFAULT_CATEGORY_NAME = "Vapes"
    REPLACE_CATEGORIES = False
    LENGTH_ITEM_ID = 14
    NUMBER_ITEMS = None
    # Json strcuture
    JSON_STRUCTURE = {
        "auth_token": "{{auth_token}}",
        "menus": [
            {
                "menu_name": f"Catálogo {BRAND_NAME}",
                "app_menu_id": f"Catálogo {BRAND_NAME}",
                "app_category_ids": []
            }
        ],
        "categories": [],
        "items": [],
        "merge_policy": 0
    }
    
    @classmethod
    def find_category(cls, categories, category_name):
        for category in categories:
            if category["category_name"] == category_name:
                return category
        return None

    @classmethod
    def trunk_string(cls, string: str, length: int):
        if len(string) > length:
            return string[:length - 3] + "..."
        return string

    @classmethod
    def replace_same_category(cls, categories, new_category):
        for category in categories:
            category["category_name"] = new_category
        return categories

    
    @classmethod
    def get_url_image(cls, image_name):
        return str(image_name)
    

    @classmethod
    def create(cls):
        dataframe1 = pd.read_excel(f"menus/{cls.FILE_NAME}.xlsx", sheet_name=cls.SHEET_POSITION)
        null_df = dataframe1.isnull()
        digits = string.digits
        
        category_counter_id = 0
        product_counter = 0        
        for i in range(0, len(dataframe1)):
            item_id = ''.join(random.choices(digits, k=cls.LENGTH_ITEM_ID)) if null_df["EAN/SKU"][i] else str(dataframe1["EAN/SKU"][i])
            price = int(dataframe1["PRECIO"][i]) * 100
            url = cls.get_url_image(dataframe1["URL DE LA IMAGEN DEL PRODUCTO"][i])
            item_detail = {
                "activity_price": price,
                "head_img": url,
                "app_item_id": item_id,
                "item_name": cls.trunk_string(dataframe1["NOMBRE DEL PRODUCTO"][i], 50),
                "price": price,
                "short_desc": cls.trunk_string(str(dataframe1["DESCRIPCIÓN"][i]), 400),
                "status": 1,
                "upc": item_id,
                "item_tags": []
            }
            if dataframe1["ALCOHOL"][i] == "Si":
                item_detail["item_tags"] = [2]
                item_detail["sold_info_intl"] = [
                    {
                        "time":[
                            {
                                "begin":"08:00",
                                "end":"23:59"
                            }
                        ],
                        "day":[
                            1,
                            2,
                            3,
                            4,
                            5,
                            6,
                            7,
                        ]
                    }
                ]
            elif dataframe1["TABACO"][i] == "Si":
                item_detail["item_tags"] = [1]
            elif dataframe1["SEXUAL"][i] == "Si":
                item_detail["item_tags"] = [4]
            cls.JSON_STRUCTURE["items"].append(item_detail)
            
            category = cls.find_category(cls.JSON_STRUCTURE["categories"], dataframe1["CATEGORIA"][i])
            if category:
                category["app_item_ids"].append(item_id)
            else:
                cls.JSON_STRUCTURE["categories"].append({
                    "app_category_id": f"{category_counter_id}",
                    "app_item_ids": [item_id],
                    "category_name": dataframe1["CATEGORIA"][i]
                })
                cls.JSON_STRUCTURE["menus"][0]["app_category_ids"].append(f"{category_counter_id}")
                category_counter_id += 1
            product_counter += 1

        if cls.REPLACE_CATEGORIES:
            cls.replace_same_category(cls.JSON_STRUCTURE["categories"], cls.DEFAULT_CATEGORY_NAME)

        with open(f"jsons/{cls.BRAND_NAME}.json", "w", encoding='utf-8') as outfile:
            outfile.write(json.dumps(cls.JSON_STRUCTURE, indent=4, ensure_ascii=False))

        return cls.JSON_STRUCTURE


CreateJSON.create()

