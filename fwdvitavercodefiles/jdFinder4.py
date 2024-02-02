import os
import re
import openai
import json
import docx2txt

# Set your OpenAI GPT-3 API key here
api_key = "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"

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessage, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI

from PyPDF2 import PdfReader
from docx import Document

def read_text_from_file(file_path):
    text = ""
    # print(file_path)
    if file_path.endswith(('.doc', '.docx')):
        document = docx2txt.process(file_path)
        # print(document)
        # for paragraph in document.paragraphs:
        #     text += paragraph.text + "\n"
        #     print(text)
        text += document + "\n"
    elif file_path.endswith('.pdf'):

        text = read_pdf(file_path)
        # reader = PdfReader(file_path)    
        # for page in range(len(reader.pages)):
        #     text += reader.pages[page].extract_text()
    else:
        print("Error: File format not supported")
    return text


def is_page_relevant(page_text):
    prompt = f"Is the following text relevant to a job description? if you're not sure consider it a 'yes' \n\n{page_text}"
    # Send the prompt to the OpenAI API
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": 'Analyse if the content is a part of a job description or not. Only answer with "yes" or "no".'},
                  {"role": "user", "content": prompt }],
        n=1,
        max_tokens=5,
        temperature=0.0,
    )

    # Check the model's response to determine relevance
    answer = response["choices"][0]["message"]["content"]
    return "yes" in answer.lower()


def is_page0_relevant(page_text):
    prompt = f"Is the following text meant to be a REQUEST FOR QUOTATIONS cover page ? if you're not sure consider it a 'no' \n\n{page_text}"
    # Send the prompt to the OpenAI API
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": """Analyse if the content is a part of a job description or only the cover page to a REQUEST FOR QUOTATIONS.
        a REQUEST FOR QUOTATIONS cover page will be like a letter, may contains the words: (from, to, subject, awards),
        a REQUEST FOR QUOTATIONS cover page doesn't descript the job but rather the conditions around to to suppliers so they can find a candidate.
        it may also contains an email or a phone number.
        Only answer with "yes" or "no".
        "yes" if it is an RFQ.
        "no" if it is a job description or if you are not sure.
        """},
                  {"role": "user", "content": prompt }],
        n=1,
        max_tokens=5,
        temperature=0.0,
    )

    # Check the model's response to determine relevance
    answer = response["choices"][0]["message"]["content"]
    return "no" in answer.lower()


import PyPDF2

def clean_text(text):
    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove phone numbers (various formats)
    text = re.sub(r'\(?\+?[0-9]*\)?-?[0-9]+-?[0-9]+-?[0-9]+', '', text)

    # Remove characters that repeat more than 10 times
    text = re.sub(r'(.)\1{10,}', '', text)

    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def read_pdf(file_path, max_tokens=5500):
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        relevant_text = []

        num_pages = len(pdf_reader.pages)

        if num_pages < 5:
            # print("small pdf")
            for page_num in range(num_pages):
                page_text = pdf_reader.pages[page_num].extract_text().lower()
                cleaned_page_text = clean_text(page_text)
                relevant_text.append(cleaned_page_text)
        else:
            # print("big pdf")
            page_text = pdf_reader.pages[0].extract_text().lower()
            if is_page0_relevant(page_text):
                    # print("page 0 added")
                    cleaned_page_text = clean_text(page_text)
                    relevant_text.append(cleaned_page_text)
            for page_num in range(1, num_pages):
                page_text = pdf_reader.pages[page_num].extract_text().lower()
                if is_page_relevant(page_text):
                    cleaned_page_text = clean_text(page_text)
                    relevant_text.append(cleaned_page_text)

            if not relevant_text:
                print("No relevant page found, including as much content as possible.")
                all_text = " ".join([pdf_reader.pages[i].extract_text().lower() for i in range(num_pages)])
                cleaned_text = clean_text(all_text)
                relevant_text.append(cleaned_text)

    return str(" ".join(relevant_text))[:max_tokens]



def is_jd(new_filename):
    filename = new_filename
    

    try:    
        # Check if the file exists
        if os.path.exists(filename):
            # Copying the content of the specified file to "input_jd.pdf"
            with open(filename, 'rb') as original_file:
                content = original_file.read()
                with open(new_filename, 'wb') as new_file:
                    new_file.write(content)
            # print(f"{filename} has been copied to {new_filename}")
        else:
            # print(f"Error: {filename} does not exist!")
            return 'no'
    except Exception as e:
        # print(f"Error: {e}")
        return 'no'

    text = read_text_from_file(new_filename)
    # print(text)

    jd_document = text
    print(text)

    #Part 1
    jd_field = ResponseSchema(name="is_jd",
                                description="Does the content above describe a job's requirements? Please ONLY answer with 'yes' or 'no'.")

    response_schemas_part1 = [jd_field]
    output_parser_part1 = StructuredOutputParser.from_response_schemas(response_schemas_part1)
    format_instructions_part1 = output_parser_part1.get_format_instructions()


    check_jd_p_template = ChatPromptTemplate.from_template(
        """
        A Job Description (JD) is a document that will describe some of the following: duties, responsibilities, necessary qualifications, and work environment of a particular job. It may include information such as job title, job purpose, duties and responsibilities, required qualifications, skills, and possibly details about the hiring company. It may also contain extra details not directly relevant for the job. 

        Given the context about what a Job Description can include, please analyze the following document content and determine whether it is a Job Description (JD) or not:

        {jd_document}

        ----------------------------
        {format_instructions}
        ----------------------------
        return a valid JSON object
        """
    )

    check_jd = check_jd_p_template.format_messages(jd_document=jd_document, format_instructions=format_instructions_part1)

    # llm_model = "gpt-4-1106-preview"
    llm_model = "gpt-4"
    chat = ChatOpenAI(temperature=0.0, model=llm_model, openai_api_key=api_key)
    part1_raw = chat(check_jd)
    print(part1_raw)

    part1 = output_parser_part1.parse(part1_raw.content)

    return part1["is_jd"]

# CALL THE FUNCTION
# jd = is_jd("1700576769_FW Seeking IT Technical Support Technician(s).pdf")
# print(jd)