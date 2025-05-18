import pdfplumber
import re
from typing import List, Dict, Any, Tuple

def extract_text_from_pdf(filepath: str) -> str:
    """
    Extracts all text content from a PDF file.

    Args:
        filepath (str): The path to the PDF file.

    Returns:
        str: The concatenated text from all pages of the PDF.
             Returns an empty string if no text can be extracted.
    """
    pdf_text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pdf_text += text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {filepath}: {e}")
        # Optionally, re-raise or handle more gracefully
    return pdf_text

def extract_text_and_tables(filepath: str) -> Dict[str, Any]:
    """
    Extracts both text and table data from a PDF file.
    
    Args:
        filepath (str): The path to the PDF file.
        
    Returns:
        Dict: A dictionary containing:
            - 'text': Full text content
            - 'tables': List of extracted tables
            - 'chunks': Text split into manageable chunks
            - 'financial_sections': Text from likely financial sections
    """
    result = {
        'text': '',
        'tables': [],
        'chunks': [],
        'financial_sections': ''
    }
    
    try:
        with pdfplumber.open(filepath) as pdf:
            full_text = ""
            tables_text = ""
            
            # Financial section keywords to look for
            financial_keywords = [
                "consolidated statements",
                "balance sheet",
                "income statement",
                "statement of operations",
                "cash flow",
                "financial data",
                "financial results",
                "financial statements",
                "financial highlights"
            ]
            
            # Extract text and tables from each page
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract regular text
                text = page.extract_text() or ""
                full_text += f"\n--- Page {page_num} ---\n{text}"
                
                # Extract tables on this page
                tables = page.extract_tables()
                if tables:
                    for i, table in enumerate(tables):
                        if table:
                            # Convert table to text format
                            table_text = "\n".join([" | ".join([str(cell) if cell else "" for cell in row]) for row in table])
                            tables_text += f"\n--- Table on Page {page_num}, #{i+1} ---\n{table_text}\n"
                            result['tables'].append({
                                'page': page_num,
                                'table_num': i+1,
                                'content': table
                            })
            
            # Combine full text with table text
            combined_text = full_text + "\n\n" + tables_text
            result['text'] = combined_text
            
            # Split into chunks of approximately 10,000 characters each
            chunks = split_text_into_chunks(combined_text, 10000)
            result['chunks'] = chunks
            
            # Extract sections likely containing financial data
            financial_section_text = ""
            for keyword in financial_keywords:
                # Find all occurrences of the keyword
                pattern = re.compile(f"(.{{0,300}}{re.escape(keyword)}.{{0,2000}})", re.IGNORECASE | re.DOTALL)
                matches = pattern.findall(combined_text)
                if matches:
                    for match in matches:
                        financial_section_text += match + "\n\n"
            
            result['financial_sections'] = financial_section_text
                
    except Exception as e:
        print(f"Error extracting content from PDF {filepath}: {e}")
        
    return result

def split_text_into_chunks(text: str, chunk_size: int = 10000) -> List[str]:
    """
    Splits text into chunks of approximately the specified size.
    
    Args:
        text (str): The text to split
        chunk_size (int): Target size for each chunk
        
    Returns:
        List[str]: List of text chunks
    """
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        # Find a good break point around the chunk_size
        end_pos = min(current_pos + chunk_size, len(text))
        
        # If we're not at the end, try to find a paragraph break
        if end_pos < len(text):
            # Look for a paragraph break
            next_paragraph = text.find('\n\n', end_pos - 200, end_pos + 200)
            if next_paragraph != -1:
                end_pos = next_paragraph + 2  # Include the paragraph break
            else:
                # If no paragraph break, try to find a sentence break
                next_sentence = text.find('. ', end_pos - 100, end_pos + 100)
                if next_sentence != -1:
                    end_pos = next_sentence + 2  # Include the period and space
        
        # Extract the chunk and add to results
        chunks.append(text[current_pos:end_pos])
        current_pos = end_pos
    
    return chunks
