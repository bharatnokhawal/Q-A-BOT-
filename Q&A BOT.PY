import docx2txt
import pandas as pd
from transformers import pipeline
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor
import os

# DOCX files
def load_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        return f"Error loading DOCX file: {e}"

# Excel files
def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error loading Excel file: {e}"

#  PDF files
def load_pdf(file_path):
    try:
        document = fitz.open(file_path)
        text = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error loading PDF file: {e}"

#  JPEG files
def load_jpeg(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error loading JPEG file: {e}"

# Paths to the files
files = {
    "docx": ["./Project links.docx", "./Sales SOP and policies.docx"],
    "excel": ["./Inventory sheet.xlsx", "./Sales schemes.xlsx"],
    "pdf": [
        "./gov.sg _ Property Tax on Residential Property.pdf",
        "./TEMBUSU GRAND_MAIN BROCHURE.pdf",
        "./facade-catalogue-and-specifications.pdf",
        "./Checklist for purchase of property under construction from developers.pdf"
    ],
    "jpeg": [
        "./Tembusu grand 1 Bed + Study unit plan.png",
        "./Tembusu grand 2 Bed +study unit plan.png",
        "./Tembusu grand 2 bed unit plan.png",
        "./Tembusu grand 3 bed unit plan.png",
        "./Tembusu grand 4 Bed unit plan.png",
        "./Tembusu grand Site plan.png",
        "./Tembusu grand image.jpeg",
        "./Tembusu grand Location map.png"
    ]
}


def parallel_load(file_type, file_paths):
    if file_type == "docx":
        return [load_docx(fp) for fp in file_paths]
    elif file_type == "excel":
        return [load_excel(fp) for fp in file_paths]
    elif file_type == "pdf":
        return [load_pdf(fp) for fp in file_paths]
    elif file_type == "jpeg":
        return [load_jpeg(fp) for fp in file_paths]

# parallel and cache the results
def load_and_cache_files():
    combined_texts = []
    with ThreadPoolExecutor() as executor:
        future_to_file_type = {executor.submit(parallel_load, ft, fp): ft for ft, fp in files.items()}
        for future in future_to_file_type:
            combined_texts.extend(future.result())

    # Combine all text data into one large text
    combined_text = "\n".join(combined_texts)
    return combined_text

# combined text
combined_text = load_and_cache_files()

# additional context
combined_text += "\nGenerative AI, or frameworks such as Groq and Mistral, or other relevant technologies."

# Hugging Face Q&A pipeline
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def query_index(question, context):
    result = qa_pipeline(question=question, context=context)
    return result['answer']

#Hugging Face text generation pipeline
generation_pipeline = pipeline("text-generation", model="gpt2")

def generate_text(prompt):
    generated_text = generation_pipeline(prompt, max_length=100, num_return_sequences=1, do_sample=True)
    return generated_text[0]['generated_text']

# Main chatbot 
def chatbot():
    print("Namste दोस्तों and Welcome to the Document Query Chatbot! ...पूछे कुछ भी अब ")
    print("You can ask questions about the content of various documents.")
    print("To exit, type 'exit'.")

    while True:
        user_question = input("\nPlease enter your question: ")

        if user_question.lower() == 'exit':
            print("Thank you for using the chatbot. वापस सेवा का मोका अवश्य दे |")
            break

        try:
            
            answer = query_index(user_question, combined_text)

            # text based on the answer
            generated_answer = generate_text(answer)

            print(f"\nQuestion: {user_question}")
            print(f"Answer: {answer}")
            print(f"Generated Answer: {generated_answer}")
        except Exception as e:
            print(f"An error occurred while processing your question: {e}")

# Run chatbot
if __name__ == "__main__":
    chatbot()
