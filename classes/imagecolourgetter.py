from PIL import Image
import requests
from io import BytesIO
import discord

def get_image_colour(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # Get the dimensions of the image
    width, height = img.size

    # Calculate the center of the image
    center = (int(width / 2), int(height / 2))

    dominant_colour = img.getpixel(center)

    colour = discord.Colour.from_rgb(dominant_colour[0], dominant_colour[1], dominant_colour[2])

    return colour