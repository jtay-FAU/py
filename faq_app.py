import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import time
import os
import re

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]["api_key"]
client = OpenAI()

def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1_title = soup.find('h1').get_text().strip() if soup.find('h1') else ""
    bespoke_page = soup.find(id='bespokePage', class_='bespokePage')

    if bespoke_page:
        for table in bespoke_page.find_all(class_='table'):
            table.extract()
        for info_box in bespoke_page.find_all(class_='infoBox'):
            info_box.extract()
        for card_body in bespoke_page.find_all(class_='card-body'):
            card_body.extract()    
        for territory in bespoke_page.find_all(class_='territory'):
            territory.extract() 

        text = bespoke_page.get_text().strip()
    else:
        text = "No text found in the specified div."

    return h1_title, text

def chunk_text(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_faqs(text):
    chunk_size = 1200
    text_chunks = chunk_text(text, chunk_size)
    all_faqs = []

    for chunk in text_chunks:
      completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          temperature=0.7,
          max_tokens=800,
          messages=[
              {"role": "system", "content": "You are a helpful Frequently Asked Questions generating assistant. You will generate FAQs based on text provided. The format should start with the question (Q:), followed by the answer (A:). You will ensure that questions end with a question mark ('?')."},
              {"role": "user", "content": f"Generate 2 frequently asked question (FAQ) from the following text from my website. The FAQ should be succinct, informative and include the most useful information for the reader. The format should start with the question (Q:), followed by the answer (A:). Ensure that questions end with a question mark ('?'). Text: \n\n{chunk}\n\nFAQ:"}
          ]
      )
      time.sleep(3)  # Add sleep between API requests
      faq = completion.choices[0].message.content
      all_faqs.append(faq)

    return all_faqs

def main():
    # Page layout
    st.set_page_config(
        page_title="FAQ Generator",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Logo and title
    logo_url = "https://www.findauniversity.com/img/logo.png"
    st.image(logo_url, width=200)
    st.title("FAQ Generator")

    # Input URL and generate FAQs
    url = st.text_input("Enter the URL:", value="", key="url_input")
    run_button = st.button("Generate FAQs")

    if run_button:
        h1_title, text = fetch_text_from_url(url)

        st.markdown("---")
        st.header("Generated FAQs")
        st.write(f"H1 Title: {h1_title}")
        st.write(f"URL: {url}")

        st.subheader("Article Text")
        st.write(text)

        st.subheader("Generated FAQs")

        # Styling for FAQs
        question_color = "#3399ff"  # Blue
        question_style = f"background-color: {question_color}; padding: 10px; color: white; font-weight: bold; border-radius: 5px;"
        answer_style = "padding: 10px; margin-top: 10px; border-radius: 5px;"

        def clean_and_find_faqs(text):
            text = text.replace("FAQ:", "").strip()
            faqs = []
            parts = text.split("Q: ")
            for part in parts[1:]:   
                try:
                    question, answer = part.split(" A: ")
                except ValueError: 
                    continue
                question = question.strip().split('\n')[0]
                answer = answer.strip().split('\n')[0]
                faq = {'question': f"{question}?", 'answer': answer}
                faqs.append(faq)
            return faqs
            
        def display_faqs(faq_list):
            if faq_list:
                for faq in faq_list:
                    st.markdown(f"<div style='{question_style}'>Q: <b>{faq['question']}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='{answer_style}'>A: {faq['answer']}</div>", unsafe_allow_html=True)
            else:
                st.warning("No FAQs found in the text.")

        for faq in generate_faqs(text):
            faq_list = clean_and_find_faqs(faq.strip())
            display_faqs(faq_list)
        
        st.markdown("---")
        st.write("Thank you for using the FAQ Generator!")

    else:
        st.write("Enter a URL and click the 'Generate FAQs' button.")

if __name__ == "__main__":
    main()
