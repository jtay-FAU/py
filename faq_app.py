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
        for article-inner in bespoke_page.find_all(class_='article-inner'):
            article-inner.extract()    
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
    logo_url = "https://www.findauniversity.com/img/logo.png"
    st.image(logo_url, width=200)
    st.title("FAQ Generator")
    url = st.text_input("Enter the URL:", value="", key="url_input")
    run_button = st.button("Generate FAQs")

    if run_button:
        h1_title, text = fetch_text_from_url(url)

        st.write(f"H1 Title: {h1_title}")
        st.write(f"URL: {url}")

        st.write("### Article Text:")
        st.write(text)

        st.write("### Generated FAQs:")
        faqs = generate_faqs(text)
        st.write('\n'.join(faqs))

        for faq in faqs:
            st.write(faq)

    else:
        st.write("Enter a URL and click the 'Generate FAQs' button.")

if __name__ == "__main__":
    main()
