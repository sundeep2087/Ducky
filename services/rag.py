import numpy as np
from openai import OpenAI
import pandas as pd
from PyPDF2 import PdfFileReader, PdfReader
from sklearn.neighbors import NearestNeighbors
from pdf2image import convert_from_path
import os

# Update the base directory to be the parent of the services directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Two levels up to reach your project

# Update the path to the PDF and CSV using os.path.join
pdf_file_path = os.path.join(BASE_DIR, 'data', 'ThePragmaticProgrammer.pdf')
embeddings_file_path = os.path.join(BASE_DIR, 'data', 'pragmatic_programmer_embeddings.csv')

# ================== Helper Functions ================== #


# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    pages = []
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for i in range(reader.getNumPages()):
            text = reader.getPage(i).extractText().replace("\n", "")
            pages.append((i + 1, text))  # Store (page_number, text)
    return pages


# Function to generate embeddings from the PDF
def generate_embeddings():
    pdf_pages = extract_text_from_pdf(pdf_file_path)

    data = []
    for page_number, text in pdf_pages:
        data.append({
            "pdf_file_path": pdf_file_path,
            "page_number": page_number,
            "context": text
        })

    client = OpenAI(
        base_url='http://aitools.cs.vt.edu:7860/openai/v1',
        api_key="aitools"
    )

    EMBEDDING_MODEL = "text-embedding-3-small"
    BATCH_SIZE = 50

    embeddings = []
    for batch_start in range(0, len(data), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = [entry['context'] for entry in data[batch_start:batch_end]]
        print(f"Batch {batch_start} to {batch_end - 1}")
        response = client.embeddings.create(
            model=EMBEDDING_MODEL, input=batch, encoding_format="float")

        for i, be in enumerate(response.data):
            assert i == be.index  # double-check embeddings are in the same order as input
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    # Add embeddings to the data
    for i, embedding in enumerate(embeddings):
        data[i]["embedding"] = embedding

    # Create the DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(embeddings_file_path, index=False)


# Function to load embeddings from the CSV
def load_embeddings():
    return pd.read_csv(embeddings_file_path)


# Function to embed user query and find the closest match
def embed_user_query(query, embeddings):
    client = OpenAI(
        base_url='http://aitools.cs.vt.edu:7860/openai/v1',
        api_key="aitools"
    )

    EMBEDDING_MODEL = "text-embedding-3-small"
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=query)
    query_embedding = np.array(response.data[0].embedding).reshape(1, -1)

    nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree').fit(embeddings)  # To get only the closest match
    distances, indices = nbrs.kneighbors(query_embedding)

    return indices[0][0], distances[0][0]  # Return only the index and distance of the closest match


# Function to find the closest context using semantic search and return context and page image file name
def get_closest_context_and_image(query):
    if not os.path.exists(embeddings_file_path):
        generate_embeddings()

    df = load_embeddings()
    embeddings = df['embedding'].apply(
        lambda x: np.fromstring(x[1:-1], sep=',')).tolist()  # Convert string back to list of floats

    idx, distance = embed_user_query(query, embeddings)

    # Retrieve context and image file name for the closest match
    page_number = idx + 1  # Adjusting for 1-based page number
    context = df.iloc[idx]['context']
    image_file_name = os.path.join(BASE_DIR, 'data', f'page_{page_number}.jpg')  # Image file name pattern

    # Generate image if it does not exist
    if not os.path.exists(image_file_name):
        pdf_page_to_image(pdf_file_path, page_number, image_file_name)

    return context, page_number, image_file_name  # Return only the closest match


# Function to convert a specific page of a PDF to an image
def pdf_page_to_image(pdf_path, page_number, output_image_path):
    images = convert_from_path(pdf_path, first_page=page_number, last_page=page_number)
    if images:
        images[0].save(output_image_path, 'JPEG')
        print(f"Saved page {page_number} as {output_image_path}")
    else:
        print("No image generated.")



# Example usage
# query = "What is Debugging?"
# context, page_number, image_file = get_closest_context_and_image(query)
#
# print(f"Context: {context}")
# print(f"Page Number: {page_number}")
# print(f"Image file: {image_file}")
#
# # Convert the specific page to image if needed
# pdf_page_to_image(pdf_file_path, page_number, image_file)
