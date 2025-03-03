import os
import re
from PIL import Image
# specify the directory path
# dir_path = "./localsite/auxapp/static"
dir_path = "./images/Supernat"
size = (300, 300)

def rename_images_in_directory(dir_path):
    # loop through all files in the directory
    for filename in os.listdir(dir_path):
        # check if the file is a text file
        if filename.endswith(".jpg"):
            # construct the old file path
            old_file_path = os.path.join(dir_path, filename)
            # construct the new file name
            new_file_name = re.search('[0-9]{4}', filename).group() + ".jpg"
            # construct the new file path
            new_file_path = os.path.join(dir_path, new_file_name)
            # rename file
            try:
                os.rename(old_file_path, new_file_path)
            except Exception:
                print(filename)

def resize_image(input_path, output_path, size):
    try:
        with Image.open(input_path) as img:
            # Resize image
            resized_img = img.resize(size, Image.LANCZOS)
            # Save the resized image
            resized_img.save(output_path)
            print(f"Image resized and saved as {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def resize_images_in_directory(directory, size):
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            input_path = os.path.join(directory, filename)
            output_path = os.path.join(directory, filename)
            resize_image(input_path, output_path, size)


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
            os.remove(jpg_path)
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


# resize_images_in_directory(dir_path, size)
# convert_all_jpgs_in_directory(dir_path)
rename_images_in_directory(dir_path)
