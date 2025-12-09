import os
import requests
import textwrap
import langextract as lx
from pprint import pprint
from bs4 import BeautifulSoup

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
def run_gemini(url: str):
    # Model ID specifically for Gemini
    model = "gemini-2.0-flash"

    article_text = fetch_article_text(url)
    result = extract_from_text(article_text, model)

    pprint(result.to_dict())  # raw structured result

    lx.io.save_annotated_documents(
        [result], 
        output_name="gemini_extracted.jsonl",
        output_dir="."
    )

    print("Saved: gemini_extracted.jsonl")
    return result


if __name__ == "__main__":
    os.environ["LANGEXTRACT_API_KEY"] = "YOUR_GEMINI_API_KEY"
    run_gemini("https://example.com/article-url")

