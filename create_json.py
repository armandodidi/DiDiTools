import pandas as pd
import json
import string
import random

class CreateJSON:
    BRAND_NAME = "Plantiflores"
    FILE_NAME = "Floria"
    URL_DOMAIN = "https://respectful-alligator.static.domains/MySite/static/"
    IS_TOBACCO_BRAND = False
    IS_WINE_BRAND = False
    SHEET_POSITION = 1
    # Suply categories
    DEFAULT_CATEGORY_NAME = "Flores"
    REPLACE_CATEGORIES = True
    LENGTH_ITEM_ID = 14
    NUMBER_ITEMS = None
    # Json strcuture
    JSON_STRUCTURE = {
        "auth_token": "",
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
    
    CERDO = 29
    RES = 81
    POLLO = 28
    
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

    # @classmethod
    # def get_url_image(cls, upc, category):
    #     if category == "Cerdo":
    #         cls.CERDO = cls.CERDO - 1
    #         if cls.CERDO > 9:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}00{cls.CERDO}.jpg"
    #         else:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}000{cls.CERDO}.jpg"
    #     if category == "Pollo":
    #         cls.POLLO = cls.POLLO - 1
    #         if cls.POLLO > 9:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}00{cls.POLLO}.jpg"
    #         else:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}000{cls.POLLO}.jpg"
    #     if category == "Res":
    #         cls.RES = cls.RES - 1
    #         if cls.RES > 9:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}00{cls.RES}.jpg"
    #         else:
    #             return f"{cls.URL_DOMAIN}/static/{category.upper()}000{cls.RES}.jpg"
    #     return ""

    # @classmethod
    # def get_url_image(cls, image_name):
    #     return f"{cls.URL_DOMAIN}{image_name.replace("/", "").replace(":", "").replace(" ", "").replace("´", "")}.png"
    
    @classmethod
    def get_url_image(cls, image_name):
        return image_name
    
    # @classmethod
    # def get_url_image(cls, image_name):
    #     return f"{cls.URL_DOMAIN}{image_name}.png"

    @classmethod
    def create(cls):
        dataframe1 = pd.read_excel(f"menus/{cls.FILE_NAME}.xlsx", sheet_name=cls.SHEET_POSITION)
        null_df = dataframe1.isnull()
        digits = string.digits
        
        category_counter_id = 0
        product_counter = 0        
        for i in range(0, len(dataframe1)):
            item_id = ''.join(random.choices(digits, k=cls.LENGTH_ITEM_ID)) if null_df["UPC"][i] else str(dataframe1["UPC"][i])
            price = int(dataframe1["PRICE"][i]) * 100
            url = cls.get_url_image(dataframe1["URL"][i])
            item_detail = {
                "activity_price": price,
                "head_img": url,
                "app_item_id": item_id,
                "item_name": cls.trunk_string(dataframe1["NAME"][i], 50),
                "price": price,
                "short_desc": cls.trunk_string(dataframe1["DESCRIPTION"][i], 400),
                "status": 1,
                "upc": item_id,
            }
            if cls.IS_TOBACCO_BRAND:
                item_detail["item_tags"] = [1]
            elif cls.IS_WINE_BRAND:
                item_detail["item_tags"] = [0]
            cls.JSON_STRUCTURE["items"].append(item_detail)
            
            category = cls.find_category(cls.JSON_STRUCTURE["categories"], dataframe1["CATEGORY"][i])
            if category:
                category["app_item_ids"].append(item_id)
            else:
                cls.JSON_STRUCTURE["categories"].append({
                    "app_category_id": f"{category_counter_id}",
                    "app_item_ids": [item_id],
                    "category_name": dataframe1["CATEGORY"][i]
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

