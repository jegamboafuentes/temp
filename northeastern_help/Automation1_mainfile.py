#importing libraries
import pandas as pd
from datetime import date, datetime
import PyPDF2
import streamlit as st
import numpy as np
import re
import io
import os
import pycountry
import pdf2image
import pytesseract

def extract_text_from_pdf(uploaded_file):
    images = pdf2image.convert_from_path(uploaded_file,dpi=300)
    text = ""
    for image in images:
        image_text = pytesseract.image_to_string(image)
        text += image_text + '\n'
    return text


def pdf_upload(year, convention_name):
    df = pd.read_excel('CountryExtraction.xlsx',sheet_name = 0)
    mylist = df['COUNTRY'].tolist()
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
    merged_dataframe1 = pd.DataFrame(columns=["Year", "Convention_Name", "Country", "Convention_Question", "Country_Answer", "Code", "Score"])
    for uploaded_file in uploaded_files:
        dataframe1 = pd.DataFrame(columns=["Year", "Convention_Name", "Country", "Convention_Question", "Country_Answer", "Code", "Score"])
        pdfReader = PyPDF2.PdfFileReader(uploaded_file)
        st.write("Filename: ", uploaded_file.name)
        if uploaded_file:
    # Save the uploaded file to a temporary file
            file_path = "temp.pdf"
            uploaded_file.seek(0)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
        text = extract_text_from_pdf(file_path)
        os.remove(file_path)
        
        lines=text.splitlines()
        start_word = "Question"
        specific_line = " "
        country_values = " "
        for line in lines:
            if line.startswith(start_word):
                specific_line = line
            for j in mylist:
                if line.startswith(j + ":"):
                    country_values = line
                    dataframe1 = dataframe1.append({'Year': year, 'Convention_Name': convention_name, 'Country': j, 'Convention_Question': specific_line, 'Country_Answer':country_values}, ignore_index=True)
        merged_dataframe1 = merged_dataframe1.append(dataframe1,ignore_index=True)

    return merged_dataframe1

  

html_temp = '<p style= "color:Black; font-size: 20px;">Automation of Index</p>'
st.markdown(html_temp, unsafe_allow_html = True)

convention_name = st.text_input("Enter the convention name", key="convention_name")
year = st.text_input("Enter the year of convention", key="year")
st.write("For", convention_name, "convention", "- Year", year)
merged_dataframe1_result = pd.DataFrame()
merged_dataframe1_result = pdf_upload(year, convention_name)

split_col = merged_dataframe1_result['Country_Answer'].str.split(': ', 1, expand=True)
for i in split_col:
    merged_dataframe1_result['Code'] = split_col[1]

for i, row in merged_dataframe1_result.iterrows():
    if re.search(r"\bdoes not exist\b|\bdo not exist\b|\bnot implemented\b|\bnot used\b|\bcontrol not established\b", row['Country_Answer'].lower()):
        merged_dataframe1_result.at[i, 'Score'] = 1
    elif re.search(r"\bpartly\b", row['Country_Answer'].lower()):
        merged_dataframe1_result.at[i, 'Score'] = 4
    elif re.search(r"\bin preparation\b|\bunder preparation\b", row['Country_Answer'].lower()):
        merged_dataframe1_result.at[i, 'Score'] = 3
    elif re.search(r"\bexists\b|\bexist\b|\bimplemented\b|\bused\b|\bestablished\b", row['Country_Answer'].lower()):
        merged_dataframe1_result.at[i, 'Score'] = 5
    else:
        merged_dataframe1_result.at[i, 'Score'] = 0

st.write(merged_dataframe1_result)

if st.button('Export to Excel'):
    # Save the DataFrame to an Excel file
    merged_dataframe1_result.to_excel('ResultFile.xlsx', index=False)
    st.write("File Exported Successfully.")



