from dotenv import load_dotenv
import os
import gradio as gr
import plotly.graph_objects as go
import pandas as pd
import json
import tempfile
from llama_index.readers.google import GoogleMapsTextSearchReader
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import re

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Use the API key
os.environ["GOOGLE_MAPS_API_KEY"] = google_maps_api_key

# Initialize GoogleMapsTextSearchReader
loader = GoogleMapsTextSearchReader()

# Function to get the embedding model
def get_embed_model():
    try:
        return HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        print(f"Error loading HuggingFaceEmbedding: {e}")
        print("Falling back to default embedding model...")
        from llama_index.embeddings.openai import OpenAIEmbedding
        return OpenAIEmbedding()

# Use the function to get the embedding model
embed_model = get_embed_model()

def parse_response(response_text):
    try:
        # Try to parse as JSON first
        data = json.loads(response_text)
        return [
            {
                "Name": station["name"],
                "Address": station["address"],
                "Rating": station["rating"],
                "Latitude": station["coordinates"]["latitude"],
                "Longitude": station["coordinates"]["longitude"]
            }
            for station in data
        ]
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract information using regex
        stations = []
        pattern = r"(.*?),\s*Address:\s*(.*?),\s*Rating:\s*([\d.]+)"
        matches = re.findall(pattern, response_text)
        
        for match in matches:
            name, address, rating = match
            # Since we don't have lat/long in this format, we'll use placeholder values
            stations.append({
                "Name": name.strip(),
                "Address": address.strip(),
                "Rating": float(rating),
                "Latitude": 0.0,  # placeholder
                "Longitude": 0.0  # placeholder
            })
        
        return stations

    # If all else fails, return an empty list
    return []

def natural_language_search(query, max_results=50):
    # Load data from Google Maps
    documents = loader.load_data(
        text=query,
        number_of_results=max_results
    )
    
    # Create index from documents with the embedding model
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
    
    # Create a query engine from the index
    query_engine = index.as_query_engine()
    
    # Query using the query engine
    response = query_engine.query("Provide a list of gas stations in Santo Domingo, including their names, addresses, ratings, and exact latitude and longitude coordinates if available. Format the response as a JSON array.")
    
    # Parse the response and create a DataFrame
    places = parse_response(str(response))
    df = pd.DataFrame(places)
    
    # Create map only if we have lat/long data
    if 'Latitude' in df.columns and 'Longitude' in df.columns and not df['Latitude'].isnull().all():
        fig = go.Figure()
        for _, row in df.iterrows():
            fig.add_trace(go.Scattermapbox(
                lat=[row['Latitude']],
                lon=[row['Longitude']],
                mode='markers',
                marker=go.scattermapbox.Marker(size=10, color='blue'),
                text=[row['Name']],
            ))
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
                zoom=12
            ),
            showlegend=False,
            height=600,
            margin={"r":0,"t":0,"l":0,"b":0},
        )
    else:
        fig = go.Figure()  # Empty figure if no map data
    
    return fig, df, str(response)

def export_data(df, file_type):
    if file_type == "json":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp.write(json.dumps(df.to_dict(orient="records")).encode())
            return tmp.name
    else:  # CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            df.to_csv(tmp.name, index=False)
            return tmp.name

def load_data(file):
    if file.name.endswith('.json'):
        with open(file.name, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(parse_response(json.dumps(data)))
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file.name)
    else:
        raise ValueError("Unsupported file format. Please upload a JSON or CSV file.")
    
    fig = go.Figure()
    for _, row in df.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[row['Latitude']],
            lon=[row['Longitude']],
            mode='markers',
            marker=go.scattermapbox.Marker(size=10, color='blue'),
            text=[row['Name']],
        ))
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=df['Latitude'].mean(), lon=df['Longitude'].mean()),
            zoom=12
        ),
        showlegend=False,
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
    )
    
    return df, fig

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            query = gr.Textbox(label="Enter your search query", value="Estoy en la avenida Charles Sumner y necesito una estacion de gasolina")
            max_results = gr.Slider(minimum=10, maximum=160, step=10, value=50, label="Maximum number of results")
            btn = gr.Button("Search")
            
            export_type = gr.Radio(["json", "csv"], label="Export Format", value="json")
            export_btn = gr.Button("Export Data")
            
            upload_file = gr.File(label="Upload JSON or CSV")
            upload_btn = gr.Button("Load Data")
            export_output = gr.File(label="Exported Data")
        
        with gr.Column(scale=2):
            output_map = gr.Plot()
            output_table = gr.DataFrame()
            output_text = gr.Textbox(label="Query Response")
    
    btn.click(natural_language_search, inputs=[query, max_results], outputs=[output_map, output_table, output_text])
    export_btn.click(export_data, inputs=[output_table, export_type], outputs=export_output)
    upload_btn.click(load_data, inputs=upload_file, outputs=[output_table, output_map])

demo.launch()