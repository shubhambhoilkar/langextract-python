import os
import requests
from bs4 import BeautifulSoup
import langextract as lx
import textwrap

def fetch_article_text(url : str) -> str:
    resp = requests.get(url, timeout=9)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(['script', 'style','nav','footer', 'header']):
        tag.decompose()
    paragraphs = [p.get_text(separator = '', strip =  True) for p in soup.find_all("p")]
    return "\n".join(paragraphs)

def extract_from_text(text: str):
    prompt = textwrap.dedent("""
        Extract key tools, concepts and keywords from this article.
        Return a JSON array where each item is an object with:
            -"entity" : the keyword or concept as it appears in the text
            -"span_start" : start character index in the text
            -"span_end": end character index in the text
            -"score" : relevance or confidence (optional)
        """).strip()
    examples = [
        lx.data.ExampleData(
            text = "Artificial Intelligence is rapidly changing the industry landscape.",
            extractions = [
                lx.data.Extraction(
                    extraction_class = "keywords",
                    extraction_text = "Artificial Intelligence",
                    attributes = {"relevence":"medium"}
                )
            ]
        )
    ]
    result = lx.extract(
        text_or_documents = text,
        prompt_description = prompt,
        examples = examples,
        model_id = "gemini-2.5-flash",
        extraction_passes = 1,
        max_workers = 4
    )
    return result

if __name__ == "__main__":
    url = "https://english.mahamoney.com/what-is-usage-based-insurance-and-how-can-it-reduce-my-auto-insurance-premium"
    article = fetch_article_text(url)
    extraction = extract_from_text(article)
    print(extraction.to_dict())

    lx.io.save_annotated_documents([extraction], output_name="extracted.jsonl", output_dir=".")
    html =lx.visualize("extracted.jsonl")
    with open("extraction_preview.html", "w") as f:
        if hasattr(html.data):
            f.write(html.data)
        else:
            f.write(html)