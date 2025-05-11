import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup API keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_data_with_openrouter(pdf_text: str) -> dict:
    """
    Extract financial data using OpenRouter API

    Args:
        pdf_text (str): The text content extracted from the PDF

    Returns:
        dict: Extracted financial data or error message
    """
    if not OPENROUTER_API_KEY:
        return {"error": "OpenRouter API key not configured"}

    prompt = f"""
    Extract the following financial data from this 10-K report in as much detail as possible:

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

    Return ONLY a valid JSON object with the following keys (use null for any values you cannot find):
    {{
        "company_name": "",
        "fiscal_year": "",
        "fiscal_period": "",
        "revenue": null,
        "cogs": null,
        "gross_profit": null,
        "operating_expenses": null,
        "operating_income": null,
        "interest_expense": null,
        "net_income": null,
        "cash_and_equivalents": null,
        "accounts_receivable": null,
        "inventory": null,
        "total_current_assets": null,
        "ppe": null,
        "total_assets": null,
        "accounts_payable": null,
        "short_term_debt": null,
        "total_current_liabilities": null,
        "long_term_debt": null,
        "total_liabilities": null,
        "stockholders_equity": null,
        "outstanding_shares": null,
        "operating_cash_flow": null,
        "capex": null,
        "investing_cash_flow": null,
        "financing_cash_flow": null,
        "free_cash_flow": null
    }}

    Here is the 10-K text:
    {pdf_text[:15000]}  # Limiting text length for API
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",  # Using DeepSeek Coder for better structured output
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(data)
    )

    try:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']

            # Extract JSON from response if it's embedded in text
            try:
                # Try to find JSON in the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                else:
                    return {"error": "Could not extract JSON data from API response"}
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON from API response"}
        else:
            return {"error": "No valid response from OpenRouter API"}
    except Exception as e:
        return {"error": f"API request failed: {str(e)}"}

def extract_data_with_gemini(pdf_text: str) -> dict:
    """
    Extract financial data using Google's Gemini API

    Args:
        pdf_text (str): The text content extracted from the PDF

    Returns:
        dict: Extracted financial data or error message
    """
    if not GEMINI_API_KEY:
        return {"error": "Gemini API key not configured"}

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # model = genai.GenerativeModel('gemini-1.5-flash-latest') # Original model
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # Trying a preview model as per original code

        prompt = f"""
        Extract the following financial data from this 10-K report in as much detail as possible:

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

        Return ONLY a valid JSON object with the following keys (use null for any values you cannot find):
        {{
            "company_name": "",
            "fiscal_year": "",
            "fiscal_period": "",
            "revenue": null,
            "cogs": null,
            "gross_profit": null,
            "operating_expenses": null,
            "operating_income": null,
            "interest_expense": null,
            "net_income": null,
            "cash_and_equivalents": null,
            "accounts_receivable": null,
            "inventory": null,
            "total_current_assets": null,
            "ppe": null,
            "total_assets": null,
            "accounts_payable": null,
            "short_term_debt": null,
            "total_current_liabilities": null,
            "long_term_debt": null,
            "total_liabilities": null,
            "stockholders_equity": null,
            "outstanding_shares": null,
            "operating_cash_flow": null,
            "capex": null,
            "investing_cash_flow": null,
            "financing_cash_flow": null,
            "free_cash_flow": null
        }}

        Here is the 10-K text:
        {pdf_text[:30000]}  # Limiting text length for API
        """

        response = model.generate_content(prompt)

        # Extract JSON from response
        try:
            content = response.text
            # Try to find JSON in the response
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
    if api_choice == 'openrouter':
        if not OPENROUTER_API_KEY:
            return {"error": "OpenRouter API key not configured"}

        prompt = f"""
        From the following 10-K report, extract and summarize:
        1. The key points from the "Management's Discussion and Analysis" (MD&A) section
        2. The most significant risk factors mentioned in the report

        Provide a concise summary of the company's performance, financial condition, future outlook,
        and the most important risks it faces.

        Format your response as JSON with these keys:
        {{
            "summary": "The MD&A summary...",
            "risk_factors": ["Risk 1", "Risk 2", "Risk 3", "Risk 4", "Risk 5"]
        }}

        Here is the 10-K text:
        {pdf_text[:20000]}  # Limiting text length for API
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "anthropic/claude-3-opus:free",  # Using Claude for better text understanding
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )

        try:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']

                # Extract JSON from response
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
    else:  # Use Gemini API
        if not GEMINI_API_KEY:
            return {"error": "Gemini API key not configured"}

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # model = genai.GenerativeModel('gemini-1.5-flash-latest') # Original model
            model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17') # Preview model from original code

            prompt = f"""
            From the following 10-K report, extract and summarize:
            1. The key points from the "Management's Discussion and Analysis" (MD&A) section
            2. The most significant risk factors mentioned in the report

            Provide a concise summary of the company's performance, financial condition, future outlook,
            and the most important risks it faces.

            Format your response as JSON with these keys:
            {{
                "summary": "The MD&A summary...",
                "risk_factors": ["Risk 1", "Risk 2", "Risk 3", "Risk 4", "Risk 5"]
            }}

            Here is the 10-K text:
            {pdf_text[:30000]}  # Limiting text length for API
            """

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
