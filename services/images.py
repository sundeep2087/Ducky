import os
from datetime import datetime
from typing import Literal, Tuple
from urllib.parse import urlparse
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables
load_dotenv()
openai_model = os.getenv('OPENAI_API_MODEL')
OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

__IMAGES_BASE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/images')


# =============================================================================================== #
# =================================== IMPLEMENTATIONS =========================================== #
# =============================================================================================== #


def _extract_filename_from_url(url: str) -> str:
    url_path = urlparse(url).path
    filename = os.path.basename(url_path)
    return filename


def generate_image(
        prompt: str,
        model: str = "dall-e-3",
        style: Literal["vivid", "natural"] = "vivid",
        quality: Literal["standard", "hd"] = "hd",
        timeout: int = 100,
        size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024"
) -> Tuple[str, str]:
    # Ensure the base folder exists
    os.makedirs(__IMAGES_BASE_FOLDER, exist_ok=True)

    client = OpenAI(base_url=OPENAI_API_BASE_URL, api_key=OPENAI_API_KEY)

    response = client.images.generate(
            model=model,
            prompt=prompt,
            style=style,
            quality=quality,
            timeout=timeout,
            size=size
        )

    image_url = response.data[0].url
    image_content = requests.get(image_url)

    image_filename = _extract_filename_from_url(image_url)
    prompt_filename = image_filename.replace(".png", ".txt")

    image_path = os.path.join(__IMAGES_BASE_FOLDER, image_filename)
    prompt_path = os.path.join(__IMAGES_BASE_FOLDER, prompt_filename)

    # Save the image
    with open(image_path, 'wb') as image_file:
        image_file.write(image_content.content)

    # Save the prompt
    with open(prompt_path, 'w') as prompt_file:
        prompt_file.write(prompt)

    return prompt, image_path


def get_all_images() -> pd.DataFrame:
    images_data = []
    for file in os.listdir(__IMAGES_BASE_FOLDER):
        if file.endswith(".png"):
            image_path = os.path.join(__IMAGES_BASE_FOLDER, file)
            description_path = os.path.splitext(image_path)[0] + '.txt'
            creation_time = os.path.getctime(image_path)
            creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')

            description = ''
            if os.path.exists(description_path):
                with open(description_path, 'r') as f:
                    description = f.read().strip()

            images_data.append([image_path, description, creation_date])

    return pd.DataFrame(images_data, columns=['Image', 'Description', 'Date Created'])


def delete_image(image_path: str):
    # Delete the image file
    if os.path.exists(image_path):
        os.remove(image_path)

    # Check and delete the description file if it exists
    description_path = os.path.splitext(image_path)[0] + '.txt'
    if os.path.exists(description_path):
        os.remove(description_path)
