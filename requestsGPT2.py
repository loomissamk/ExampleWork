import requests
from bs4 import BeautifulSoup
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Initialize GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
# Set padding token
tokenizer.pad_token = tokenizer.eos_token

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

def articles_to_chunks(text):
    chunk_size = 500
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

def summarize_for_senior_citizen(text):
    request_text = "Please summarize the following so an average person over sixty-five could understand it: " + text
    inputs = tokenizer.encode(request_text, return_tensors='pt', max_length=1024, padding=True, truncation=True)
    outputs = model.generate(inputs, max_length=500, pad_token_id=tokenizer.eos_token_id, do_sample=True)
    summarized_text = tokenizer.decode(outputs[0])
    return summarized_text

def summarize_website(url):
    website_text = fetch_website_content(url)
    if website_text:
        chunks = articles_to_chunks(website_text)
        for chunk in chunks:
            summarized_chunk = summarize_for_senior_citizen(chunk)
            print("Summarized text for a person over sixty-five:")
            print(summarized_chunk)
            print("-------------------------------------------")
    else:
        print("Failed to fetch content from the provided URL.")


if __name__ == "__main__":
    url = 'https://www.nih.gov/' # Replace with the desired URL
    summarize_website(url)
