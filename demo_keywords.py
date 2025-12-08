from langextract import KeywordExtractor

text = "Hey myself Sam, I am AI Developer."

extractor =  KeywordExtractor()
keywords = extractor.extract(text)

print("Keywords are: ", keywords)