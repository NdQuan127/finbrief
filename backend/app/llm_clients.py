import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
import re

# Load environment variables
load_dotenv()

# Setup API keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_financial_trends_with_llm(financial_data_history: list, api_choice: str = "gemini") -> dict:
    """
    Use LLM to analyze trends in financial data across multiple periods.
    
    Args:
        financial_data_history (list): List of financial data dictionaries for multiple periods
        api_choice (str): The API to use (gemini or openrouter)
        
    Returns:
        dict: A dictionary containing trend analysis results
    """
    if not financial_data_history or len(financial_data_history) < 1:
        return {"error": "Insufficient data for trend analysis"}
    
    # Extract company name if available
    company_name = financial_data_history[0].get("company_name", "the company")
    
    # Collect periods for context
    periods = [f"{data.get('fiscal_year', 'Unknown')} ({data.get('fiscal_period', 'Unknown')})" 
               for data in financial_data_history]
    
    periods_str = ", ".join(periods)
    
    prompt = f"""
    You are a financial analyst. Based on the financial data provided for {company_name} for the periods {periods_str}:
    
    1. **Step 1: Identify notable changes:** List the largest and most significant percentage or absolute changes in the key items of the Income Statement (Revenue, Cost of Goods Sold, Gross Profit, Operating Expenses, Operating Income, Net Income) and Balance Sheet (Cash and Cash Equivalents, Accounts Receivable, Inventory, Total Current Assets, Property, Plant and Equipment (PP&E), Total Assets, Current Liabilities, Short-term Debt, Total Liabilities, Stockholders' Equity).
    
    2. **Step 2: Provide preliminary assessment:** Based on these changes, offer an initial assessment of which operational areas of the company appear to be improving or deteriorating.
    
    3. **Step 3: Requirements (if any):** If any information is missing or unclear for trend analysis, please note it.
    
    Present your results as JSON with the keys: "notable_changes_income_statement", "notable_changes_balance_sheet", "preliminary_trend_assessment".
    
    Here is the financial data for analysis:
    {json.dumps(financial_data_history, indent=2)}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def interpret_financial_ratios_with_llm(financial_data: dict, ratios: dict, api_choice: str = "gemini") -> dict:
    """
    Use LLM to interpret financial ratios with economic significance.
    
    Args:
        financial_data (dict): Extracted financial data for current period
        ratios (dict): Calculated financial ratios
        api_choice (str): The API to use (gemini or openrouter)
        
    Returns:
        dict: A dictionary containing ratio interpretations
    """
    company_name = financial_data.get("company_name", "the company")
    period = f"{financial_data.get('fiscal_year', 'Unknown')} ({financial_data.get('fiscal_period', 'Unknown')})"
    
    prompt = f"""
    You are a financial analyst. Based on the financial data and ratios provided for {company_name} for the period {period}:
    
    1. **Step 1: Calculate financial ratios:** If not already calculated, compute the following financial ratios (note "Not enough data" if unable to calculate):
        * Profitability: ROE, ROA, Gross Profit Margin, Operating Profit Margin, Net Profit Margin
        * Leverage: Debt to Equity (D/E), Debt to Total Assets
        * Liquidity: Current Ratio, Quick Ratio
    
    2. **Step 2: Interpret each ratio:** For each calculated ratio, provide a concise interpretation of its meaning for the company's financial condition and operational efficiency. Compare implicitly with usual thresholds (e.g., ROE > 15% is good).
    
    3. **Step 3: Assess ratio groups overall:** Provide an overall assessment for each ratio group (profitability, leverage, liquidity) as strong, average, or weak.
    
    Present your results in a way that would be understandable to someone without deep financial expertise. Explain the economic significance of each ratio in plain language.
    
    Return your analysis as JSON with these keys: "calculated_ratios" (an object containing ratios), "ratio_interpretations" (an object containing interpretations for each ratio), "overall_ratio_assessment" (an object containing evaluations for each group).
    
    Financial data:
    {json.dumps(financial_data, indent=2)}
    
    Already calculated ratios:
    {json.dumps(ratios, indent=2)}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def predict_earnings_outlook_with_llm(trend_analysis: dict, ratio_analysis: dict, api_choice: str = "gemini") -> dict:
    """
    Use LLM to predict earnings outlook based on trend and ratio analysis.
    
    Args:
        trend_analysis (dict): Output from analyze_financial_trends_with_llm
        ratio_analysis (dict): Output from interpret_financial_ratios_with_llm
        api_choice (str): The API to use (gemini or openrouter)
        
    Returns:
        dict: A dictionary containing earnings prediction and rationale
    """
    prompt = f"""
    You are a financial analyst. Based on the financial trend analysis and ratio analysis provided:
    
    1. **Step 1: Summarize key factors:** Summarize the main strengths and weaknesses derived from the trend analysis and financial ratio analysis.
    
    2. **Step 2: Make a prediction:** Predict whether the company's earnings (EPS or Net Income) in the next period are likely to Increase, Decrease, or Remain Stable.
    
    3. **Step 3: Assess magnitude and confidence:** Indicate the expected magnitude of change (Large, Moderate, Small) and your confidence level in this prediction (from 0 to 1).
    
    4. **Step 4: Explain your prediction:** Provide a detailed paragraph explaining the basis for your prediction, connecting back to the analyses performed.
    
    Return your prediction as JSON with these keys: "key_factors_summary", "earnings_prediction_direction", "earnings_prediction_magnitude", "prediction_confidence", "prediction_rationale".
    
    Trend Analysis:
    {json.dumps(trend_analysis, indent=2)}
    
    Ratio Analysis:
    {json.dumps(ratio_analysis, indent=2)}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def generate_swot_analysis_with_llm(financial_data: dict, ratio_analysis: dict, mda_summary: dict, api_choice: str = "gemini") -> dict:
    """
    Use LLM to generate a comprehensive SWOT analysis based on all available information.
    
    Args:
        financial_data (dict): Extracted financial data
        ratio_analysis (dict): Result from interpret_financial_ratios_with_llm
        mda_summary (dict): MD&A summary and risk factors
        api_choice (str): The API to use (gemini or openrouter)
        
    Returns:
        dict: A SWOT analysis with strengths, weaknesses, opportunities, threats
    """
    company_name = financial_data.get("company_name", "the company")
    
    prompt = f"""
    You are a strategic analyst. Based on all the financial analysis, MD&A summary, and risk factors for {company_name}, perform a SWOT analysis:
    
    1. **Strengths:** List the main financial and operational strengths.
    2. **Weaknesses:** List the main financial and operational weaknesses.
    3. **Opportunities:** Identify potential opportunities based on the company's situation and (if available) market context.
    4. **Threats:** Identify potential threats.
    
    Return your analysis as JSON with these keys: "strengths", "weaknesses", "opportunities", "threats", each being an array of strings.
    
    Financial data:
    {json.dumps(financial_data, indent=2)}
    
    Ratio analysis:
    {json.dumps(ratio_analysis, indent=2)}
    
    MD&A summary and risk factors:
    {json.dumps(mda_summary, indent=2)}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def create_financial_story_with_llm(ratio_analysis: dict, prediction: dict, swot: dict, api_choice: str = "gemini") -> dict:
    """
    Create narrative insights from the financial analysis focusing on storytelling.
    
    Args:
        ratio_analysis (dict): Result from interpret_financial_ratios_with_llm
        prediction (dict): Result from predict_earnings_outlook_with_llm
        swot (dict): Result from generate_swot_analysis_with_llm
        api_choice (str): The API to use (gemini or openrouter)
        
    Returns:
        dict: A dictionary with narrative insights for different financial aspects
    """
    prompt = f"""
    You are a financial storyteller. Create narrative insights based on the financial analysis provided. 
    Explain in plain language that would be understandable to investors without deep financial expertise.
    
    For each category below, create a short, insightful narrative paragraph that connects the data points into a coherent story:
    
    1. Profitability Narrative: Explain how the company is generating returns, connecting ROE, margins, and other relevant metrics.
    
    2. Financial Health Narrative: Tell the story of the company's balance sheet strength and liquidity position.
    
    3. Future Outlook Narrative: Expand on the earnings prediction with a compelling storyline about where the company appears to be heading.
    
    4. Executive Summary: Create a concise 200-300 word overview highlighting the most critical aspects of the company's financial situation, performance, risks, and prospects.
    
    Avoid financial jargon where possible, and when you must use financial terms, briefly explain their meaning.
    
    Return your narratives as JSON with these keys: "profitability_narrative", "financial_health_narrative", "future_outlook_narrative", "executive_summary".
    
    Ratio analysis:
    {json.dumps(ratio_analysis, indent=2)}
    
    Earnings prediction:
    {json.dumps(prediction, indent=2)}
    
    SWOT analysis:
    {json.dumps(swot, indent=2)}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def _call_gemini_api(prompt: str) -> dict:
    """
    Helper function to call the Gemini API.
    
    Args:
        prompt (str): The prompt to send to the API
        
    Returns:
        dict: The JSON response or error message
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        try:
            content = response.text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Could not extract JSON data from Gemini API response"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from Gemini API response"}
            
    except Exception as e:
        return {"error": f"Gemini API request failed: {str(e)}"}

def _call_openrouter_api(prompt: str, model: str = "deepseek/deepseek-chat-v3-0324:free") -> dict:
    """
    Helper function to call the OpenRouter API.
    
    Args:
        prompt (str): The prompt to send to the API
        model (str): The model to use
        
    Returns:
        dict: The JSON response or error message
    """
    if not OPENROUTER_API_KEY:
        return {"error": "OpenRouter API key not configured"}
        
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Could not extract JSON data from API response"}
        else:
            return {"error": "No valid response from OpenRouter API"}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def extract_data_with_openrouter(pdf_data: Dict[str, Any]) -> dict:
    """
    Extract financial data using OpenRouter API

    Args:
        pdf_data (Dict[str, Any]): The extracted data from the PDF including text,
                                   tables, chunks, and financial sections

    Returns:
        dict: Extracted financial data or error message
    """
    if not OPENROUTER_API_KEY:
        return {"error": "OpenRouter API key not configured"}

    # Function to create a prompt for a specific chunk of text
    def create_chunk_prompt(text_chunk):
        return f"""
        Extract the following financial data from this portion of a 10-K report:

    Basic Information:
    1. Company Name
    2. Fiscal Year End Date
    3. Fiscal Period (e.g. Annual, Q1, Q2, etc.)

    Income Statement:
    4. Revenue / Net Sales (in USD)
    5. Cost of Goods Sold (COGS) (in USD)
    6. Gross Profit (in USD)
    7. Operating Expenses (in USD)
    8. Operating Income / EBIT (in USD)
    9. Interest Expense (in USD)
    10. Net Income (in USD)

    Balance Sheet:
    11. Cash and Cash Equivalents (in USD)
    12. Accounts Receivable (in USD)
    13. Inventory (in USD)
    14. Total Current Assets (in USD)
    15. Property, Plant and Equipment (PP&E) (in USD)
    16. Total Assets (in USD)
    17. Accounts Payable (in USD)
    18. Short-Term Debt (in USD)
    19. Total Current Liabilities (in USD)
    20. Long-Term Debt (in USD)
    21. Total Liabilities (in USD)
    22. Total Stockholders' Equity (in USD)
    23. Total Outstanding Shares (count)

    Cash Flow:
    24. Cash Flow from Operating Activities (in USD)
    25. Capital Expenditures (CapEx) (in USD)
    26. Cash Flow from Investing Activities (in USD)
    27. Cash Flow from Financing Activities (in USD)
    28. Free Cash Flow (in USD, which is Operating Cash Flow - CapEx)

        Return ONLY a valid JSON object with the keys listed above. Use null for any values you cannot find.

    Here is the 10-K text:
        {text_chunk}
        """

    # List to store results from each chunk
    chunk_results = []
    
    # First, check if we have financial sections extracted
    if pdf_data.get('financial_sections'):
        # Process the financial sections first - they're most likely to contain key data
        financial_prompt = create_chunk_prompt(pdf_data['financial_sections'][:30000])
        financial_result = _call_openrouter_api(financial_prompt)
        if isinstance(financial_result, dict) and 'error' not in financial_result:
            chunk_results.append(financial_result)

    # Process each chunk of the full text
    for i, chunk in enumerate(pdf_data.get('chunks', [])):
        # Only process a reasonable number of chunks (first 3 chunks)
        if i >= 3:
            break
            
        # Skip if chunk is too small
        if len(chunk) < 1000:
            continue
            
        chunk_prompt = create_chunk_prompt(chunk)
        chunk_result = _call_openrouter_api(chunk_prompt)
        
        if isinstance(chunk_result, dict) and 'error' not in chunk_result:
            chunk_results.append(chunk_result)

    # Combine results from all chunks
    return combine_chunk_results(chunk_results)

def extract_data_with_gemini(pdf_data: Dict[str, Any]) -> dict:
    """
    Extract financial data using Google's Gemini API

    Args:
        pdf_data (Dict[str, Any]): The extracted data from the PDF including text,
                                   tables, chunks, and financial sections

    Returns:
        dict: Extracted financial data or error message
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}

    # Configure the Gemini model
        genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Function to create a prompt for a specific chunk of text
    def create_chunk_prompt(text_chunk):
        return f"""
        Extract the following financial data from this portion of a 10-K report:

        Basic Information:
        1. Company Name
        2. Fiscal Year End Date
        3. Fiscal Period (e.g. Annual, Q1, Q2, etc.)

        Income Statement:
        4. Revenue / Net Sales (in USD)
        5. Cost of Goods Sold (COGS) (in USD)
        6. Gross Profit (in USD)
        7. Operating Expenses (in USD)
        8. Operating Income / EBIT (in USD)
        9. Interest Expense (in USD)
        10. Net Income (in USD)

        Balance Sheet:
        11. Cash and Cash Equivalents (in USD)
        12. Accounts Receivable (in USD)
        13. Inventory (in USD)
        14. Total Current Assets (in USD)
        15. Property, Plant and Equipment (PP&E) (in USD)
        16. Total Assets (in USD)
        17. Accounts Payable (in USD)
        18. Short-Term Debt (in USD)
        19. Total Current Liabilities (in USD)
        20. Long-Term Debt (in USD)
        21. Total Liabilities (in USD)
        22. Total Stockholders' Equity (in USD)
        23. Total Outstanding Shares (count)

        Cash Flow:
        24. Cash Flow from Operating Activities (in USD)
        25. Capital Expenditures (CapEx) (in USD)
        26. Cash Flow from Investing Activities (in USD)
        27. Cash Flow from Financing Activities (in USD)
        28. Free Cash Flow (in USD, which is Operating Cash Flow - CapEx)

        For each metric, extract the most recent fiscal year value.
        Return ONLY a valid JSON object with the keys listed above. Use null for any values you cannot find.

        Here is the 10-K text:
        {text_chunk}
        """

    # List to store results from each chunk
    chunk_results = []
    
    # First, check if we have financial sections extracted
    if pdf_data.get('financial_sections'):
        # Process the financial sections first - they're most likely to contain key data
        financial_prompt = create_chunk_prompt(pdf_data['financial_sections'][:50000])
        financial_result = _call_gemini_api(financial_prompt)
        if isinstance(financial_result, dict) and 'error' not in financial_result:
            chunk_results.append(financial_result)

    # Process each chunk of the full text
    for i, chunk in enumerate(pdf_data.get('chunks', [])):
        # Only process a reasonable number of chunks (first 3 chunks)
        if i >= 3:
            break
            
        # Skip if chunk is too small
        if len(chunk) < 1000:
            continue
            
        chunk_prompt = create_chunk_prompt(chunk)
        chunk_result = _call_gemini_api(chunk_prompt)
        
        if isinstance(chunk_result, dict) and 'error' not in chunk_result:
            chunk_results.append(chunk_result)

    # Combine results from all chunks
    return combine_chunk_results(chunk_results)

def combine_chunk_results(chunk_results: List[Dict]) -> Dict:
    """
    Combine results from multiple chunks, preferring non-null values.

    Args:
        chunk_results (List[Dict]): List of dictionaries with extracted data

    Returns:
        Dict: Combined results with the best values from all chunks
    """
    if not chunk_results:
        return {"error": "No valid data extracted from any text chunk"}
        
    # Create an empty result with all fields initialized to None
    combined_result = {
        "company_name": "",
        "fiscal_year": "",
        "fiscal_period": "",
        "revenue": None,
        "cogs": None,
        "gross_profit": None,
        "operating_expenses": None,
        "operating_income": None,
        "interest_expense": None,
        "net_income": None,
        "cash_and_equivalents": None,
        "accounts_receivable": None,
        "inventory": None,
        "total_current_assets": None,
        "ppe": None,
        "total_assets": None,
        "accounts_payable": None,
        "short_term_debt": None,
        "total_current_liabilities": None,
        "long_term_debt": None,
        "total_liabilities": None,
        "stockholders_equity": None,
        "outstanding_shares": None,
        "operating_cash_flow": None,
        "capex": None,
        "investing_cash_flow": None,
        "financing_cash_flow": None,
        "free_cash_flow": None
    }
    
    # For each result, take the non-null values
    for result in chunk_results:
        for key, value in result.items():
            # Skip if the key doesn't exist in our template
            if key not in combined_result:
                continue
                
            # For string fields, prefer non-empty values
            if key in ["company_name", "fiscal_year", "fiscal_period"]:
                if value and (not combined_result[key] or len(combined_result[key]) < len(value)):
                    combined_result[key] = value
            # For numeric fields, prefer non-null values
            elif value is not None and combined_result[key] is None:
                combined_result[key] = value
    
    return combined_result

def extract_mda_summary(pdf_text: str, api_choice: str ="gemini") -> dict:
    """
    Extract a summary of the Management Discussion and Analysis (MD&A)
    and Risk Factors sections from the 10-K report

    Args:
        pdf_text (str): The text content extracted from the PDF
        api_choice (str): The API to use (gemini or openrouter)

    Returns:
        dict: A dictionary containing the MD&A summary and key risk factors
    """
    # Find sections likely to contain MD&A content
    mda_keywords = [
        "management's discussion", 
        "management discussion", 
        "MD&A", 
        "business overview",
        "results of operations",
        "financial condition"
    ]
    
    risk_keywords = [
        "risk factors", 
        "principal risks", 
        "key risks",
        "material risks"
    ]
    
    # Extract relevant sections
    mda_section = ""
    risk_section = ""
    
    # Find MD&A section
    for keyword in mda_keywords:
        pattern = re.compile(f"(.{{0,300}}{re.escape(keyword.lower())}.{{0,5000}})", re.IGNORECASE | re.DOTALL)
        matches = pattern.findall(pdf_text.lower())
        if matches:
            for match in matches:
                mda_section += match + "\n\n"
            break  # Found a section, no need to search more
    
    # Find Risk Factors section
    for keyword in risk_keywords:
        pattern = re.compile(f"(.{{0,300}}{re.escape(keyword.lower())}.{{0,5000}})", re.IGNORECASE | re.DOTALL)
        matches = pattern.findall(pdf_text.lower())
        if matches:
            for match in matches:
                risk_section += match + "\n\n"
            break  # Found a section, no need to search more
    
    # Limit text to avoid token limits
    mda_section = mda_section[:15000] if mda_section else pdf_text[:15000]
    risk_section = risk_section[:15000] if risk_section else ""
    
    prompt = f"""
    From the following 10-K report excerpt, extract and summarize:

    1. Management's Discussion and Analysis (MD&A) key points:
       - Company performance overview
       - Major operational developments
       - Financial condition summary
       - Forward-looking statements

    2. Key Risk Factors (if present):
       - Enumerate the top risks mentioned
       - Briefly explain each risk's potential impact

    Return your analysis as JSON with these keys: "summary" (for MD&A) and "risk_factors" (an array of objects with "risk" and "impact" keys).

    Text from the 10-K MD&A section:
    {mda_section}

    Text from the Risk Factors section (if available):
    {risk_section}
    """
    
    if api_choice == 'openrouter':
        return _call_openrouter_api(prompt, "deepseek/deepseek-chat-v3-0324:free")
    else:
        return _call_gemini_api(prompt)

def extract_financial_data_directly(pdf_data: Dict[str, Any]) -> dict:
    """
    Extract financial data by having the LLM analyze the entire PDF content directly.
    This approach avoids parsing/extraction issues by letting the LLM find and identify
    the financial metrics within the full context.

    Args:
        pdf_data (Dict[str, Any]): The extracted data from the PDF including text,
                                   tables, and financial sections

    Returns:
        dict: Extracted financial data or error message
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}

    # Configure the Gemini model
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
    
    # Collect relevant content from the PDF
    financial_text = pdf_data.get('financial_sections', '')
    
    # If no financial sections were detected, try to find relevant terms in the chunks
    if not financial_text or len(financial_text) < 1000:
        financial_keywords = [
            "consolidated statements",
            "balance sheet", 
            "income statement",
            "statement of operations",
            "statement of cash flows",
            "stockholders' equity",
            "financial position",
            "financial highlights"
        ]
        
        # Search through chunks for relevant financial content
        for chunk in pdf_data.get('chunks', []):
            for keyword in financial_keywords:
                if keyword.lower() in chunk.lower():
                    financial_text += chunk + "\n\n"
                    break
    
    # If we still don't have enough financial text, use tables
    if len(financial_text) < 5000:
        # Convert tables to text format for analysis
        tables_text = ""
        for table in pdf_data.get('tables', []):
            table_content = table.get('content', [])
            if table_content:
                table_text = "\n".join([" | ".join([str(cell) if cell else "" for cell in row]) for row in table_content])
                tables_text += f"\n--- Table on Page {table.get('page', '?')} ---\n{table_text}\n\n"
        
        financial_text += tables_text
    
    # Create a comprehensive prompt for the LLM
    prompt = f"""
    FINANCIAL DATA EXTRACTION TASK

    You are analyzing a 10-K annual report to extract key financial metrics.
    
    Step 1: Carefully examine the provided text from the 10-K report and identify the most recent fiscal year's financial data.
    
    Step 2: Extract the following financial metrics for the MOST RECENT FISCAL YEAR ONLY:
    
    Basic Information:
    - Company Name
    - Fiscal Year End Date
    - Fiscal Period (Annual)
    
    Income Statement:
    - Revenue / Net Sales
    - Cost of Goods Sold (COGS)
    - Gross Profit
    - Operating Expenses
    - Operating Income / EBIT
    - Interest Expense
    - Net Income
    
    Balance Sheet:
    - Cash and Cash Equivalents
    - Accounts Receivable
    - Inventory
    - Total Current Assets
    - Property, Plant and Equipment (PP&E)
    - Total Assets
    - Accounts Payable
    - Short-Term Debt
    - Total Current Liabilities
    - Long-Term Debt
    - Total Liabilities
    - Total Stockholders' Equity
    - Total Outstanding Shares
    
    Cash Flow:
    - Cash Flow from Operating Activities
    - Capital Expenditures (CapEx)
    - Cash Flow from Investing Activities
    - Cash Flow from Financing Activities
    - Free Cash Flow
    
    Step 3: When you find a value, note whether it's in thousands, millions, billions, etc. and convert to the raw number.
    For example, if you see "$123.4 million", record this as 123400000.
    
    Step 4: If you can't find a specific metric, use null. Do not guess values.
    
    Step 5: Respond ONLY with a valid JSON object with the exact keys listed below, properly using numbers, not strings, for numeric values.
    
    Expected JSON keys:
    "company_name", "fiscal_year", "fiscal_period", "revenue", "cogs", "gross_profit", "operating_expenses", 
    "operating_income", "interest_expense", "net_income", "cash_and_equivalents", "accounts_receivable", 
    "inventory", "total_current_assets", "ppe", "total_assets", "accounts_payable", "short_term_debt", 
    "total_current_liabilities", "long_term_debt", "total_liabilities", "stockholders_equity", 
    "outstanding_shares", "operating_cash_flow", "capex", "investing_cash_flow", "financing_cash_flow", "free_cash_flow"
    
    Here is the 10-K content to analyze:
    {financial_text[:50000]}
    """
    
    # Call the Gemini API
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        try:
            content = response.text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # If we couldn't extract JSON, log the response for debugging
                print(f"LLM response did not contain valid JSON: {content[:500]}...")
                return {"error": "Could not extract JSON data from Gemini API response"}
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM response: {content[:500]}...")
            return {"error": "Failed to parse JSON from Gemini API response"}
            
    except Exception as e:
        return {"error": f"Gemini API request failed: {str(e)}"}
