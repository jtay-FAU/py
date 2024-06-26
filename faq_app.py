import streamlit as st
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
import os
import re
import time

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]["api_key"]
client = OpenAI()

def check_password():
    """Returns `True` if the user entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["security"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False
            
    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

@st.cache
def fetch_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    h1_title = soup.find('h1').get_text().strip() if soup.find('h1') else ""
    
    bespoke_page = (soup.find(id='bespokePage') 
                    or soup.find(attrs={'class': 'bespokePage'}) 
                    or soup.find(attrs={'class': 'htmlpage-content'})
                    or soup.find(attrs={'class': 'mainOffsetArticle'}))
    
    if bespoke_page:
        for table in bespoke_page.find_all(class_='table'):
            table.extract()
        for info_box in bespoke_page.find_all(class_='infoBox'):
            info_box.extract()
        for card_body in bespoke_page.find_all(class_='card-body'):
            card_body.extract()    
        for territory in bespoke_page.find_all(class_='territory'):
            territory.extract() 
        for territory in bespoke_page.find_all(class_='emg-similar-courses'):
            territory.extract()                
            
        text = bespoke_page.get_text().strip()
    else:
        text = "Oops. No text was found in the specified webpage."
    
    return h1_title, text

def chunk_text(text, chunk_size):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_faqs(text):
    chunk_size = 1200
    text_chunks = chunk_text(text, chunk_size)
    all_faqs = []
    for chunk in text_chunks:
      completion = client.chat.completions.create(
          model="gpt-3.5-turbo-0125",
          temperature=0.7,
          max_tokens=1000,
          messages=[
              {"role": "system", "content": "You are a helpful Frequently Asked Questions generating assistant. You will generate FAQs based on text provided. The format should start with the question (Q:), followed by the answer (A:). You will ensure that questions (Q:) always end with a question mark ('?'). Answers (A:) should always be definitive, and not themselves interrogative."},
              {"role": "user", "content": f"Generate 2 distinct frequently asked question (FAQ) from the following text from my website. The FAQ should be succinct, informative and include the most useful information for the reader. The format should start with the question (Q:), followed by the answer (A:). Ensure that questions (Q:) end with a question mark ('?'). Text: \n\n{chunk}\n\nFAQ:"}
          ]
      )
      time.sleep(3)  # Add sleep between API requests
      faq = completion.choices[0].message.content
      all_faqs.append(faq)
    return all_faqs

def main():
    if not check_password():
        return

    # Page layout
    st.set_page_config(
        page_title="FAQ Generator",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # Logo and title
    logo_url = "https://www.keg.com/hubfs/keg_left_Sharp.svg"
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
        for faq in generate_faqs(text):
            faq_cleaned = faq.replace("FAQ:", "").strip()
            faq_parts = re.split("Q: |A: ", faq_cleaned)
            faq_parts = [part.strip() for part in faq_parts if part.strip()]
            for i in range(0, len(faq_parts), 2):
                question = faq_parts[i] if i < len(faq_parts) else ""
                answer = faq_parts[i+1] if i+1 < len(faq_parts) else ""
                if question and answer:
                    st.markdown(f"<div style='{question_style}'>Q: <b>{question}</b></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='{answer_style}'>A: {answer}</div>", unsafe_allow_html=True)
                elif question:
                    st.markdown(f"<div style='{question_style}'>Q: <b>{question}</b></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.write("Thank you for using the FAQ Generator!")
    else:
        st.write("Enter a URL and click the 'Generate FAQs' button.")


if __name__ == "__main__":
    main()
