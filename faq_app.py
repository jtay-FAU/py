import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import time

openai.api_key = st.secrets["openai"]["api_key"]

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
    chunk_size = 3000
    text_chunks = chunk_text(text, chunk_size)
    all_faqs = []

    for chunk in text_chunks:
        prompt = f"Generate 2 frequently asked question (FAQ) from the following text from my website. The FAQ should be succinct, informative and include the most useful information for the reader. The format should start with the question (Q:), followed by the answer (A:). Text: \n\n{chunk}\n\nFAQ:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=800,
            n=1,
            stop=None,
            temperature=0.7,
            top_p=1
        )
        time.sleep(2)  # Add sleep between API requests
        faq = response.choices[0].text.strip()
        all_faqs.append(faq)

    return all_faqs

def main():
    # Page layout
    st.set_page_config(
        page_title="FAQ Generator",
        page_icon="📚",
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
        answer_color = "#33cc33"  # Green
        question_style = f"background-color: {question_color}; padding: 10px; color: white; font-weight: bold;"
        answer_style = f"padding: 10px;"

        faqs = generate_faqs(text)

        for i in range(0, len(faqs), 2):
            question_1 = faqs[i][3:].strip() if faqs[i].startswith("Q:") else ""
            answer_1 = faqs[i+1][3:].strip() if faqs[i+1].startswith("A:") else ""
            question_2 = faqs[i+2][3:].strip() if i+2 < len(faqs) and faqs[i+2].startswith("Q:") else ""
            answer_2 = faqs[i+3][3:].strip() if i+3 < len(faqs) and faqs[i+3].startswith("A:") else ""

            if question_1:
                st.markdown(f"<div style='{question_style}'>Q: {question_1}</div>", unsafe_allow_html=True)
            if answer_1:
                st.markdown(f"<div style='{answer_style}'>A: {answer_1}</div>", unsafe_allow_html=True)
            if question_2:
                st.markdown(f"<div style='{question_style}'>Q: {question_2}</div>", unsafe_allow_html=True)
            if answer_2:
                st.markdown(f"<div style='{answer_style}'>A: {answer_2}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.write("Thank you for using the FAQ Generator!")

    else:
        st.write("Enter a URL and click the 'Generate FAQs' button.")

if __name__ == "__main__":
    main()

