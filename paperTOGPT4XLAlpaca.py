#loomissamk Copyright

import datetime
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os
import pandas as pd
from PyPDF2 import PdfReader as reader
import docx2txt
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Initialize GPT-2 tokenizer and model
tokenizer = T5Tokenizer.from_pretrained('declare-lab/flan-alpaca-gpt4-xl')
model = T5ForConditionalGeneration.from_pretrained('declare-lab/flan-alpaca-gpt4-xl')

# Set padding token
model.config.pad_token_id = tokenizer.eos_token_id

def is_url(path):
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def fetch_content(path):
    if is_url(path):
        return fetch_website_content(path)
    else:
        return read_paper(path)

def read_paper(file_path):
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.csv':
        # Read CSV file
        df = pd.read_csv(file_path)
        text = '\n'.join(df.values.flatten())
    elif file_extension == '.pdf':
        # Read PDF file
        with open(file_path, 'rb') as file:
            pdf_reader = reader(file)
            text = ''
            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()
    elif file_extension == '.docx':
        # Read Word (docx) file
        text = docx2txt.process(file_path)
    elif file_extension == '.txt':
        # Read .txt
        with open(file_path, 'r') as txt:
            text = txt.read()
    else:
        # For other file formats, you can add more handlers here
        raise ValueError(f"Unsupported file format: {file_extension}")

    return text

def fetch_website_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extracting text from the website
            text = ' '.join([p.text for p in soup.find_all('p')])  # Extracting text from paragraphs
            return text
        else:
            print("Failed to fetch website content. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("Error fetching website:", e)
        return None

def name(file_path):
    file_name, extension = os.path.splitext(file_path)
    file_name = os.path.basename(file_name)
    return file_name

def articles_to_chunks(text):
    chunk_size = 20000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def summarize(text, prompt):
    request_text = f'{prompt}' + text + '\n\n\n'
    inputs = tokenizer.encode(request_text, return_tensors='pt', max_length=1024, padding=True, truncation=True)
    outputs = model.generate(inputs, max_length=100000, pad_token_id=tokenizer.eos_token_id, do_sample=True)
    summarized_text = tokenizer.decode(outputs[0])
    return summarized_text

def save(summarized_text, file_name, prompt):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = f"{file_name}_{prompt}_{date}.txt"
    with open(file_path, 'a') as file:
        file.write(summarized_text + '\n')

def summarize_paper(text, prompt, file_name):
    chunks = articles_to_chunks(text)
    all_summaries = []

    for chunk in chunks:
        summarized_chunk = summarize(chunk, prompt)
        save(summarized_chunk, file_name, prompt)
        all_summaries.append(summarized_chunk)
        print("Summarized text in chunks:")
        print(summarized_chunk)
        print("-------------------------------------------")

    return all_summaries

def create_synopsis(all_summaries, file_name, prompt):
    # Combine all individual summaries into a single synopsis
    full_synopsis = '\n'.join(all_summaries)

    # Save the final synopsis
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = f"{file_name}_{prompt}_{date}_synopsis.txt"
    with open(file_path, 'w') as file:
        file.write(full_synopsis + '\n')

    print("\nFinal Synopsis:")
    print(full_synopsis)
    print("-------------------------------------------")

if __name__ == "__main__":
    # Example usage
    #prompt = "Summarize the following for a new parent: "
    #user_input = "https://en.wikipedia.org/wiki/Child_development_stages"
    
    #file_path = input("Input file location: ")
    prompt = input("Prompt: ")
    user_input = input('Your article (file path or URL): ')
    content = fetch_content(user_input)

    if content:
        file_name = name(user_input)
        # Summarize paper in chunks
        all_summaries = summarize_paper(content, prompt, file_name)

        # Generate a synopsis based on the entire conversation
        create_synopsis(all_summaries, file_name, prompt)
    else:
        print("Failed to fetch content from the provided path or URL.")
