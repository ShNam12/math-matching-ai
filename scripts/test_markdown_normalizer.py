from modules.ingestion.markdown_processing.normalizer import normalize_markdown


text = "Title\r\n\r\n\r\nText with math \\(x^2\\)\r\n"
print(normalize_markdown(text))
