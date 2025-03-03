import os
import requests
import time
import pandas as pd
from PIL import Image
from io import BytesIO


class DownloadAndFormatImages:
    FILE_NAME = "CencoMascotas"
    BRAND_NAME = "CencoMascotas"
    IMAGE_COLUMN_NAME = "IMAGE"
    EAN_COLUMN_NAME = "EAN"
    SIZE = (600, 600)
    MISSING_IMAGES = []
    
    #############################
    # DO NOT EDIT THE NEXT VALUES
    #############################
    IMAGE_FOLDER = f"./images/{BRAND_NAME}/"


    @classmethod
    def rename_images_in_directory(cls, dir_path):
        # loop through all files in the directory
        for filename in os.listdir(dir_path):
            # check if the file is a text file
            if filename.endswith(".png"):
                # construct the old file path
                old_file_path = os.path.join(dir_path, filename)
                # construct the new file name
                new_file_name = filename.replace("/", "").replace("_", "").replace(" ", "").replace("´", "")
                # construct the new file path
                new_file_path = os.path.join(dir_path, new_file_name)
                # rename file
                try:
                    os.rename(old_file_path, new_file_path)
                except Exception:
                    print(filename)

    @classmethod
    def resize_image(cls, image, output_path, size):
        image = image.resize(size, Image.LANCZOS)
        image = cls.change_color_mode(image=image)
        image.save(output_path, format='JPEG')

    @classmethod
    def resize_images_in_directory(cls):
        for filename in os.listdir(cls.IMAGE_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = os.path.join(cls.IMAGE_FOLDER, filename)
                output_path = os.path.join(cls.IMAGE_FOLDER, filename)
                cls.resize_image(input_path, output_path, cls.SIZE)

    @classmethod
    def change_color_mode(cls, image):
        # Check the mode and convert if necessary
        if image.mode == 'CMYK':
            image = image.convert('RGB')
        return image

    @classmethod
    def convert_all_jpgs_in_directory(cls, dir_path):
        # loop through all files in the directory
        for filename in os.listdir(dir_path):
            # check if the file is a text file
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                jpg_path = os.path.join(dir_path, filename)
                png_path = os.path.splitext(jpg_path)[0] + '.png'
                cls.convert_jpg_to_png(jpg_path, png_path)

    @classmethod
    def convert_image_mode(cls, image):
        # Convert the image to RGB mode if it is in "P" mode or any other mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image

    @classmethod
    def download_image(cls, ean, url):
        try:
            response = requests.get(f"https://{url}")
        except Exception:
            return None
        # response = requests.get(url=url)
        print(response.status_code)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        # print(f"Not image found for eam: {ean}")
        cls.MISSING_IMAGES.append(ean)
        return None

    @classmethod
    def convertion_process(cls):
        print("-----------------------------------------")
        print("           1. Formatting images          ")
        print("-----------------------------------------")
        df = pd.read_excel(f"menus/{cls.FILE_NAME}.xlsx")
        # df.to_excel(f"menus/{cls.FILE_NAME}.xlsx")
        null_df = df.isnull()

        for i in range(0, len(df.index)):
            ean = df[cls.EAN_COLUMN_NAME][i]
            image_url = None if null_df[cls.IMAGE_COLUMN_NAME][i] else df[cls.IMAGE_COLUMN_NAME][i]
            image = cls.download_image(ean, image_url) if image_url else None
            if image:
                try:
                    image = cls.convert_image_mode(image)
                    cls.resize_image(image, f"{cls.IMAGE_FOLDER}{ean}.jpg", cls.SIZE)
                except Exception:
                    print(f"Error with image of the UPC: {ean}")
        print("Missing images:")
        print(cls.MISSING_IMAGES)
        print("-----------------------------------------")
        print("           2. Ending processing          ")
        print("-----------------------------------------")
        # cls.convert_all_jpgs_in_directory()


DownloadAndFormatImages.convertion_process()
