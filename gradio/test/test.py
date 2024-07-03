import os
from llama_index.readers.google import GoogleMapsTextSearchReader

# Make sure your API key is set in the environment variable
api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

print(f"API Key: {api_key[:5]}...{api_key[-5:]}")  # Print first and last 5 characters

loader = GoogleMapsTextSearchReader()
documents = loader.load_data(
    text="restaurants in New York",
    number_of_results=5
)

print(f"Number of documents: {len(documents)}")
if documents:
    print(f"First document: {documents[0]}")