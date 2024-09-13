import os
from PIL import Image


# specify the directory path
# dir_path = "./localsite/auxapp/static"
dir_path = "./imagenes_tienda_el_tio_1"


def convert_jpg_to_png(jpg_path, png_path):
    try:
        # Open the JPG image
        with Image.open(jpg_path) as img:
            # Check the mode and convert if necessary
            if img.mode == 'CMYK':
                img = img.convert('RGB')
            # Convert the image to PNG and save it
            img.save(png_path, 'PNG')
            print(f"Image converted and saved as {png_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def convert_all_jpgs_in_directory(dir_path):
    # loop through all files in the directory
    for filename in os.listdir(dir_path):
        # check if the file is a text file
        if filename.endswith('.jpg') or filename.endswith('.jpeg'):
            jpg_path = os.path.join(dir_path, filename)
            png_path = os.path.splitext(jpg_path)[0] + '.png'
            convert_jpg_to_png(jpg_path, png_path)

convert_all_jpgs_in_directory(dir_path)
