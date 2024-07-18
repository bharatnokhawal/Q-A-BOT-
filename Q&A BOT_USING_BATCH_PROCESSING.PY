import docx2txt
import pandas as pd
from transformers import pipeline
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor


def load_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        return f"Error loading DOCX file: {e}"


def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error loading Excel file: {e}"


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

def load_jpeg(file_path):
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error loading JPEG file: {e}"


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

# cache the results
def load_and_cache_files():
    combined_texts = []
    with ThreadPoolExecutor() as executor:
        future_to_file_type = {executor.submit(parallel_load, ft, fp): ft for ft, fp in files.items()}
        for future in future_to_file_type:
            combined_texts.extend(future.result())

   
    combined_text = "\n".join(combined_texts)
    return combined_text

#  combined text
combined_text = load_and_cache_files()

combined_text += "\nGenerative AI, or frameworks such as Groq and Mistral, or other relevant technologies."

#  Q&A pipeline
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def query_index(question, context):
    result = qa_pipeline(question=question, context=context)
    return result['answer']

# TEXT generation pipeline
generation_pipeline = pipeline("text-generation", model="gpt2")

def generate_text_batch(prompts):
    generated_texts = generation_pipeline(prompts, max_length=100, num_return_sequences=1, do_sample=True)
    return [text['generated_text'] for text in generated_texts]

# Main chatbot 
def chatbot():
    print("Namste दोस्तों and Welcome to the Document Query Chatbot! ...पूछे कुछ भी अब ")
    print("You can ask questions about the content of various documents.")
    print("To exit, type 'exit'.")
    print("To process the batch of questions, type 'process'.")

    questions = []

    while True:
        user_question = input("\nPlease enter your question: ")

        if user_question.lower() == 'exit':
            print("Thank you for using the chatbot. वापस सेवा का मोका अवश्य दे |")
            break
        elif user_question.lower() == 'process':
            if not questions:
                print("No questions to process. Please enter some questions first.")
                continue

            try:
                answers = [query_index(question, combined_text) for question in questions]
                generated_answers = generate_text_batch(answers)

                for question, answer, generated_answer in zip(questions, answers, generated_answers):
                    print(f"\nQuestion: {question}")
                    print(f"Answer: {answer}")
                    print(f"Generated Answer: {generated_answer}")

                # Clear questions after processing
                questions.clear()
            except Exception as e:
                print(f"An error occurred while processing your questions: {e}")
        else:
            questions.append(user_question)

# Run chatbot
if __name__ == "__main__":
    chatbot()
