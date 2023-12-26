#loomissamk

import datetime
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import torch
import pandas as pd
from PyPDF2 import PdfFileReader
import docx2txt

#cuda boiler
torch_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
model.to(torch_device)

# Set padding token
tokenizer.pad_token = tokenizer.eos_token

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
            pdf_reader = PdfFileReader(file)
            text = ''
            for page in range(pdf_reader.getNumPages()):
                text += pdf_reader.getPage(page).extractText()
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

def name(file_path):
    file_name, extension = os.path.splitext(file_path)
    file_name = os.path.basename(file_name)
    return file_name

def articles_to_chunks(text):
    chunk_size = 1000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def summarize(text, prompt):
    request_text = f'{prompt}' + text + '\n\n\n'
    inputs = tokenizer.encode(request_text, return_tensors='pt', max_length=1024, padding=True, truncation=True)
    outputs = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id, do_sample=True)
    summarized_text = tokenizer.decode(outputs[0])
    return summarized_text

def save(summarized_text):
    date = datetime.datetime.now().strftime("%Y-%m-%d")   
    file_path = f"{file_name}_{prompt}_{date}.txt"
    with open(file_path, 'a') as file:
        file.write(summarized_text + '\n')
        
def summarize_paper(text, prompt):
    chunks = articles_to_chunks(text)
    for chunk in chunks:
        summarized_chunk = summarize(chunk, prompt)
        save(summarized_chunk)
        print("Summarized text in chunks:")
        print(summarized_chunk)
        print("-------------------------------------------")

if __name__ == "__main__":
    #example usage
    #prompt = "Summarize the following for a newspaper"
    #file = "/home/test_file.txt"
    
    file = input("Input file location: ")
    prompt = input("Prompt: ")
    file_name = name(file)
    text = read_paper(file)
    summarize_paper(text, prompt)