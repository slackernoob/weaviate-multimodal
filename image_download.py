import argparse
from simple_image_download import simple_image_download as simp
from PIL import Image
import os

# Initialize the argument parser
parser = argparse.ArgumentParser(description="Download and convert images to PNG format.")
parser.add_argument('query', type=str, help='Search query for images')
parser.add_argument('number', type=int, nargs='?', default=5, help='Number of images to download (default: 5)')
args = parser.parse_args()

# Extract arguments
search_query = args.query
num_images = args.number

# Initialize the simple image download instance
response = simp.simple_image_download

# Specify the directory where images will be downloaded
download_directory = 'downloads'

# Download images for the specified query
response().download(search_query, num_images)  # Download images for the search query

# # Convert all downloaded images to PNG
# for root, dirs, files in os.walk(download_directory):
#     for file in files:
#         if not file.endswith('.png'):
#             file_path = os.path.join(root, file)
#             with Image.open(file_path) as img:
#                 # Convert and save the image in PNG format
#                 img = img.convert('RGB')
#                 png_file_path = os.path.splitext(file_path)[0] + '.png'
#                 img.save(png_file_path, 'PNG')
#                 print(f"Saved {png_file_path}")

#                 # Optionally, delete the original file
#                 os.remove(file_path)
