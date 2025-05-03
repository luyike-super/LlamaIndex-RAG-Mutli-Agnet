import json
import os
from llama_index.node_parser.dashscope import (
    DashScopeJsonNodeParser,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import Document

# Set your Dashscope API key in the environment
os.environ["DASHSCOPE_API_KEY"] = "your_api_key_here"

documents = [
    # Prepare your documents obtained from the Dashscope reader
]

# Initialize the DashScope JsonNodeParser
node_parser = DashScopeJsonNodeParser(
    chunk_size=100, overlap_size=0, separator=" |,|，|。|？|！|\n|\?|\!"
)

# Set up the ingestion pipeline with the node parser
pipeline = IngestionPipeline(transformations=[node_parser])

# Process the documents and print the resulting nodes
nodes = pipeline.run(documents=documents, show_progress=True)
for node in nodes:
    print(node)