import os
import requests
import textwrap
import langextract as lx
from pprint import pprint
from bs4 import BeautifulSoup

# --------------------------------------------------------
# 1. Fetch Article Text
# --------------------------------------------------------
def fetch_article_text(url: str) -> str:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove unnecessary tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()

    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all("p")]
    return "\n".join(paragraphs)


# --------------------------------------------------------
# 2. Extract Keywords using LangExtract (OpenAI Model)
# --------------------------------------------------------
def extract_from_text(text: str, model_id: str):
    prompt = textwrap.dedent("""
        Extract important tools, technologies, concepts, and keywords from this article.
        Return a JSON array where each item contains:
            - "entity": the keyword or concept found in the article
            - "span_start": character index where the keyword begins
            - "span_end": character index where the keyword ends
            - "score": relevance score (optional)
    """).strip()

    examples = [
        lx.data.ExampleData(
            text="Artificial Intelligence is rapidly changing the technology landscape.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="keyword",
                    extraction_text="Artificial Intelligence",
                    attributes={"relevance": "high"}
                )
            ]
        )
    ]

    result = lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        model_id=model_id,     # OPENAI MODEL HERE
        extraction_passes=1,
        max_workers=4
    )

    return result


# --------------------------------------------------------
# 3. Main OpenAI Runner
# --------------------------------------------------------
def run_openai(url: str):
    model = "gpt-3.5-turbo-1106"  # Recommended OpenAI model for LangExtract

    # Ensure correct environment variable is used
    os.environ["OPENAI_API_KEY"] = "openai_api_key"
    os.environ["LANGEXTRACT_API_KEY"] = ""  # Disable Gemini

    article_text = fetch_article_text(url)
    result = extract_from_text(article_text, model)

    pprint(result.to_dict())

    # Save results
    lx.io.save_annotated_documents(
        [result],
        output_name="openai_extracted.jsonl",
        output_dir="."
    )

    print("Saved: openai_extracted.jsonl")
    return result


# --------------------------------------------------------
# 4. Entry Point
# --------------------------------------------------------
if __name__ == "__main__":
    run_openai("https://english.mahamoney.com")


