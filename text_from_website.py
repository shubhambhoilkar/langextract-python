import requests
import langextract as lx
from bs4 import BeautifulSoup
# from langextract import KeywordExtractor

response = requests.get(url = "https://english.mahamoney.com/what-is-usage-based-insurance-and-how-can-it-reduce-my-auto-insurance-premium", timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

paragraphs = [p.get_text(strip = True) for p in soup.find_all("p")]
print(paragraphs)
input_text = paragraphs

result = lx.extract(
    text_or_documents = input_text,
    prompt_description = "extract all the major keywords",
    # examples = "",
    model_id = "gemini-2.5-flash"
)