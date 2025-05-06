# Import required libraries
import requests
import time
import os
from pathlib import Path
import PyPDF2
from llama_index.core import Document

# Create PDF directory if it doesn't exist
pdf_dir = Path("state_pdfs")
pdf_dir.mkdir(exist_ok=True)

# Define all US states
# states = [
#     "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", 
#     "Connecticut", "Delaware", "Florida", "Georgia (U.S. state)", "Hawaii", "Idaho", 
#     "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", 
#     "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", 
#     "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
#     "New Hampshire", "New Jersey", "New Mexico", "New York", 
#     "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", 
#     "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
#     "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", 
#     "West Virginia", "Wisconsin", "Wyoming"
# ]

# --- Let's just focus on a sample of 5 states for this project --- #
states = ["Hawaii", "Alaska", "Arizona", "California","New York" ]

# Function to download Wikipedia page as PDF
def download_wikipedia_pdf(title, output_path):
    """
    Download a Wikipedia page as PDF using Wikipedia's PDF export feature
    """
    # URL encode the title
    encoded_title = title.replace(' ', '_')
    
    # Wikipedia's PDF export URL
    url = f"https://en.wikipedia.org/api/rest_v1/page/pdf/{encoded_title}"
    
    # Add a user agent to avoid being blocked
    headers = {
        'User-Agent': 'Wikipedia PDF Downloader for Research (contact@example.com)'
    }
    
    # Download the PDF
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Save the PDF
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Error downloading {title}: {response.status_code}")
        return False

# Function to extract text from PDF for indexing
def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

# Download PDFs for all states and prepare documents
pdf_documents = []

for state in states:
    pdf_filename = pdf_dir / f"{state.replace(' ', '_')}_state.pdf"
    print(f"Downloading PDF for {state}...")
    
    # Download the PDF
    success = download_wikipedia_pdf(f"{state} (state)", pdf_filename)
    
    if success:
        # Extract text from pdf
        text_content = extract_text_from_pdf(pdf_filename)
        
        # Create a document that points to the PDF but also contains the text
        doc = Document(
            text=text_content,
            metadata={
                "title": f"{state} State Information",
                "source": str(pdf_filename),
                "file_type": "pdf",
                "state": state
            }
        )
        pdf_documents.append(doc)
        print(f"  Successfully processed {state}")
    
    # Add a small delay to avoid hitting rate limits
    time.sleep(1)

print(f"Total PDFs downloaded and processed: {len(pdf_documents)}")