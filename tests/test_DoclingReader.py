from llama_index.readers.docling import DoclingReader

reader = DoclingReader()
documents = reader.load_data("data/llamaidex.docx")

print(documents)
