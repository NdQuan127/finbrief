import os
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pdfplumber
from dotenv import load_dotenv
import tempfile
import requests
import base64
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Setup API keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# Enable CORS
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_data_with_openrouter(pdf_text):
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
        "model": "deepseek/deepseek-coder-v2:free",  # Using DeepSeek Coder for better structured output
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

def extract_data_with_gemini(pdf_text):
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
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

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

def calculate_financial_ratios(data, stock_price=None):
    """
    Calculate financial ratios based on extracted data from financial reports

    Args:
        data (dict): Extracted financial data
        stock_price (float, optional): Current stock price

    Returns:
        dict: Financial ratios, scores, and recommendations
    """
    results = {
        "company_name": data.get("company_name", "Unknown"),
        "fiscal_year": data.get("fiscal_year", "Unknown"),
        "fiscal_period": data.get("fiscal_period", "Annual"),
        "extracted_data": {},
        "ratios": {},
        "scores": {},
        "trend_analysis": {},
        "qualitative_summary": {}
    }

    # Helper function to safely convert financial values to float
    def safe_float(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            # Remove currency symbols and commas
            clean_value = str(value).replace("$", "").replace(",", "").strip()
            # Handle parentheses notation for negative numbers
            if clean_value.startswith("(") and clean_value.endswith(")"):
                return -float(clean_value[1:-1])
            return float(clean_value)
        except (ValueError, TypeError):
            return None

    # Extract and clean all financial data
    financial_metrics = [
        "revenue", "cogs", "gross_profit", "operating_expenses", "operating_income",
        "interest_expense", "net_income", "cash_and_equivalents", "accounts_receivable",
        "inventory", "total_current_assets", "ppe", "total_assets", "accounts_payable",
        "short_term_debt", "total_current_liabilities", "long_term_debt", "total_liabilities",
        "stockholders_equity", "outstanding_shares", "operating_cash_flow", "capex",
        "investing_cash_flow", "financing_cash_flow", "free_cash_flow"
    ]

    # Convert all financial data to float and store in extracted_data
    for metric in financial_metrics:
        value = safe_float(data.get(metric))
        results["extracted_data"][metric] = value

    # For backward compatibility, handle old field names
    if "total_debt" in data and results["extracted_data"].get("short_term_debt") is None and results["extracted_data"].get("long_term_debt") is None:
        total_debt = safe_float(data.get("total_debt"))
        results["extracted_data"]["total_debt"] = total_debt
    else:
        # Calculate total debt
        short_term_debt = results["extracted_data"].get("short_term_debt", 0) or 0
        long_term_debt = results["extracted_data"].get("long_term_debt", 0) or 0
        results["extracted_data"]["total_debt"] = short_term_debt + long_term_debt

    try:
        # Get key values for calculations
        revenue = results["extracted_data"].get("revenue")
        net_income = results["extracted_data"].get("net_income")
        outstanding_shares = results["extracted_data"].get("outstanding_shares")
        stockholders_equity = results["extracted_data"].get("stockholders_equity")
        total_debt = results["extracted_data"].get("total_debt")
        total_assets = results["extracted_data"].get("total_assets")
        operating_income = results["extracted_data"].get("operating_income")
        interest_expense = results["extracted_data"].get("interest_expense")
        total_current_assets = results["extracted_data"].get("total_current_assets")
        total_current_liabilities = results["extracted_data"].get("total_current_liabilities")
        inventory = results["extracted_data"].get("inventory")
        gross_profit = results["extracted_data"].get("gross_profit")
        operating_cash_flow = results["extracted_data"].get("operating_cash_flow")
        capex = results["extracted_data"].get("capex")

        # 1. PROFITABILITY RATIOS

        # Calculate EPS
        if outstanding_shares and outstanding_shares > 0 and net_income is not None:
            eps = net_income / outstanding_shares
            results["ratios"]["eps"] = eps

            # Calculate P/E Ratio if stock price is provided
            if stock_price and eps != 0:
                pe_ratio = float(stock_price) / eps
                results["ratios"]["pe_ratio"] = pe_ratio

                # Score P/E Ratio
                if pe_ratio < 15:
                    pe_score = 3  # Undervalued
                    results["scores"]["pe_ratio"] = {"score": pe_score, "interpretation": "Undervalued"}
                elif pe_ratio <= 25:
                    pe_score = 2  # Fairly valued
                    results["scores"]["pe_ratio"] = {"score": pe_score, "interpretation": "Fairly Valued"}
                else:
                    pe_score = 1  # Overvalued
                    results["scores"]["pe_ratio"] = {"score": pe_score, "interpretation": "Overvalued"}

        # Calculate ROE (Return on Equity)
        if stockholders_equity and stockholders_equity != 0 and net_income is not None:
            roe = (net_income / stockholders_equity) * 100
            results["ratios"]["roe"] = roe

            # Score ROE
            if roe > 15:
                roe_score = 3  # Strong
                results["scores"]["roe"] = {"score": roe_score, "interpretation": "Strong"}
            elif roe >= 10:
                roe_score = 2  # Acceptable
                results["scores"]["roe"] = {"score": roe_score, "interpretation": "Acceptable"}
            else:
                roe_score = 1  # Weak
                results["scores"]["roe"] = {"score": roe_score, "interpretation": "Weak"}

        # Calculate ROA (Return on Assets)
        if total_assets and total_assets != 0 and net_income is not None:
            roa = (net_income / total_assets) * 100
            results["ratios"]["roa"] = roa

            # Score ROA
            if roa > 5:
                roa_score = 3  # Strong
                results["scores"]["roa"] = {"score": roa_score, "interpretation": "Strong"}
            elif roa >= 2:
                roa_score = 2  # Acceptable
                results["scores"]["roa"] = {"score": roa_score, "interpretation": "Acceptable"}
            else:
                roa_score = 1  # Weak
                results["scores"]["roa"] = {"score": roa_score, "interpretation": "Weak"}

        # Calculate Profit Margins
        if revenue and revenue != 0:
            # Net Profit Margin
            if net_income is not None:
                net_margin = (net_income / revenue) * 100
                results["ratios"]["net_profit_margin"] = net_margin

                # Score Net Profit Margin
                if net_margin > 10:
                    net_margin_score = 3  # Strong
                    results["scores"]["net_profit_margin"] = {"score": net_margin_score, "interpretation": "Strong"}
                elif net_margin >= 5:
                    net_margin_score = 2  # Acceptable
                    results["scores"]["net_profit_margin"] = {"score": net_margin_score, "interpretation": "Acceptable"}
                else:
                    net_margin_score = 1  # Weak
                    results["scores"]["net_profit_margin"] = {"score": net_margin_score, "interpretation": "Weak"}

            # Gross Profit Margin
            if gross_profit is not None:
                gross_margin = (gross_profit / revenue) * 100
                results["ratios"]["gross_profit_margin"] = gross_margin

                # Score Gross Profit Margin
                if gross_margin > 40:
                    gross_margin_score = 3  # Strong
                    results["scores"]["gross_profit_margin"] = {"score": gross_margin_score, "interpretation": "Strong"}
                elif gross_margin >= 20:
                    gross_margin_score = 2  # Acceptable
                    results["scores"]["gross_profit_margin"] = {"score": gross_margin_score, "interpretation": "Acceptable"}
                else:
                    gross_margin_score = 1  # Weak
                    results["scores"]["gross_profit_margin"] = {"score": gross_margin_score, "interpretation": "Weak"}

            # Operating Profit Margin
            if operating_income is not None:
                operating_margin = (operating_income / revenue) * 100
                results["ratios"]["operating_profit_margin"] = operating_margin

                # Score Operating Profit Margin
                if operating_margin > 15:
                    op_margin_score = 3  # Strong
                    results["scores"]["operating_profit_margin"] = {"score": op_margin_score, "interpretation": "Strong"}
                elif operating_margin >= 8:
                    op_margin_score = 2  # Acceptable
                    results["scores"]["operating_profit_margin"] = {"score": op_margin_score, "interpretation": "Acceptable"}
                else:
                    op_margin_score = 1  # Weak
                    results["scores"]["operating_profit_margin"] = {"score": op_margin_score, "interpretation": "Weak"}

        # 2. LEVERAGE RATIOS

        # Calculate D/E Ratio (Debt to Equity)
        if stockholders_equity and stockholders_equity != 0 and total_debt is not None:
            de_ratio = total_debt / stockholders_equity
            results["ratios"]["de_ratio"] = de_ratio

            # Score D/E Ratio
            if de_ratio < 0.5:
                de_score = 3  # Low leverage
                results["scores"]["de_ratio"] = {"score": de_score, "interpretation": "Low Leverage"}
            elif de_ratio <= 1.0:
                de_score = 2  # Moderate leverage
                results["scores"]["de_ratio"] = {"score": de_score, "interpretation": "Moderate Leverage"}
            else:
                de_score = 1  # High leverage
                results["scores"]["de_ratio"] = {"score": de_score, "interpretation": "High Leverage"}

        # Calculate Debt Ratio (Debt to Assets)
        if total_assets and total_assets != 0 and total_debt is not None:
            debt_ratio = total_debt / total_assets
            results["ratios"]["debt_ratio"] = debt_ratio

            # Score Debt Ratio
            if debt_ratio < 0.3:
                debt_ratio_score = 3  # Low debt
                results["scores"]["debt_ratio"] = {"score": debt_ratio_score, "interpretation": "Low Debt"}
            elif debt_ratio <= 0.6:
                debt_ratio_score = 2  # Moderate debt
                results["scores"]["debt_ratio"] = {"score": debt_ratio_score, "interpretation": "Moderate Debt"}
            else:
                debt_ratio_score = 1  # High debt
                results["scores"]["debt_ratio"] = {"score": debt_ratio_score, "interpretation": "High Debt"}

        # Calculate Interest Coverage Ratio
        if interest_expense and interest_expense != 0 and operating_income is not None:
            interest_coverage = operating_income / abs(interest_expense)
            results["ratios"]["interest_coverage"] = interest_coverage

            # Score Interest Coverage
            if interest_coverage > 5:
                interest_coverage_score = 3  # Strong
                results["scores"]["interest_coverage"] = {"score": interest_coverage_score, "interpretation": "Strong"}
            elif interest_coverage >= 2:
                interest_coverage_score = 2  # Acceptable
                results["scores"]["interest_coverage"] = {"score": interest_coverage_score, "interpretation": "Acceptable"}
            else:
                interest_coverage_score = 1  # Weak
                results["scores"]["interest_coverage"] = {"score": interest_coverage_score, "interpretation": "Weak"}

        # 3. LIQUIDITY RATIOS

        # Calculate Current Ratio
        if total_current_liabilities and total_current_liabilities != 0 and total_current_assets is not None:
            current_ratio = total_current_assets / total_current_liabilities
            results["ratios"]["current_ratio"] = current_ratio

            # Score Current Ratio
            if current_ratio > 2:
                current_ratio_score = 3  # Strong
                results["scores"]["current_ratio"] = {"score": current_ratio_score, "interpretation": "Strong"}
            elif current_ratio >= 1:
                current_ratio_score = 2  # Acceptable
                results["scores"]["current_ratio"] = {"score": current_ratio_score, "interpretation": "Acceptable"}
            else:
                current_ratio_score = 1  # Weak
                results["scores"]["current_ratio"] = {"score": current_ratio_score, "interpretation": "Weak"}

        # Calculate Quick Ratio
        if total_current_liabilities and total_current_liabilities != 0 and total_current_assets is not None and inventory is not None:
            quick_ratio = (total_current_assets - inventory) / total_current_liabilities
            results["ratios"]["quick_ratio"] = quick_ratio

            # Score Quick Ratio
            if quick_ratio > 1.5:
                quick_ratio_score = 3  # Strong
                results["scores"]["quick_ratio"] = {"score": quick_ratio_score, "interpretation": "Strong"}
            elif quick_ratio >= 1:
                quick_ratio_score = 2  # Acceptable
                results["scores"]["quick_ratio"] = {"score": quick_ratio_score, "interpretation": "Acceptable"}
            else:
                quick_ratio_score = 1  # Weak
                results["scores"]["quick_ratio"] = {"score": quick_ratio_score, "interpretation": "Weak"}

        # 4. CASH FLOW INDICATORS

        # Calculate FCF/Net Income ratio (quality of earnings)
        if net_income and net_income != 0 and operating_cash_flow is not None and capex is not None:
            fcf = operating_cash_flow - (capex if capex else 0)
            if fcf != 0 and net_income != 0:
                fcf_net_income_ratio = fcf / net_income
                results["ratios"]["fcf_net_income_ratio"] = fcf_net_income_ratio

                # Score FCF/Net Income
                if fcf_net_income_ratio > 1.2:
                    fcf_score = 3  # Strong
                    results["scores"]["fcf_net_income_ratio"] = {"score": fcf_score, "interpretation": "Strong (High-quality earnings)"}
                elif fcf_net_income_ratio >= 0.8:
                    fcf_score = 2  # Acceptable
                    results["scores"]["fcf_net_income_ratio"] = {"score": fcf_score, "interpretation": "Acceptable (Reliable earnings)"}
                else:
                    fcf_score = 1  # Weak
                    results["scores"]["fcf_net_income_ratio"] = {"score": fcf_score, "interpretation": "Weak (Poor earnings quality)"}

        # 5. VALUATION RATIOS

        # Calculate P/B Ratio (if stock price is provided)
        if stock_price and stockholders_equity and outstanding_shares and outstanding_shares > 0:
            book_value_per_share = stockholders_equity / outstanding_shares
            if book_value_per_share > 0:
                pb_ratio = float(stock_price) / book_value_per_share
                results["ratios"]["pb_ratio"] = pb_ratio

                # Score P/B Ratio
                if pb_ratio < 1.5:
                    pb_score = 3  # Undervalued
                    results["scores"]["pb_ratio"] = {"score": pb_score, "interpretation": "Undervalued"}
                elif pb_ratio <= 3:
                    pb_score = 2  # Fairly valued
                    results["scores"]["pb_ratio"] = {"score": pb_score, "interpretation": "Fairly Valued"}
                else:
                    pb_score = 1  # Overvalued
                    results["scores"]["pb_ratio"] = {"score": pb_score, "interpretation": "Overvalued"}

        # Calculate P/S Ratio (if stock price is provided)
        if stock_price and revenue and outstanding_shares and outstanding_shares > 0:
            revenue_per_share = revenue / outstanding_shares
            if revenue_per_share > 0:
                ps_ratio = float(stock_price) / revenue_per_share
                results["ratios"]["ps_ratio"] = ps_ratio

                # Score P/S Ratio (thresholds vary by industry, using general ones)
                if ps_ratio < 1:
                    ps_score = 3  # Undervalued
                    results["scores"]["ps_ratio"] = {"score": ps_score, "interpretation": "Undervalued"}
                elif ps_ratio <= 3:
                    ps_score = 2  # Fairly valued
                    results["scores"]["ps_ratio"] = {"score": ps_score, "interpretation": "Fairly Valued"}
                else:
                    ps_score = 1  # Overvalued
                    results["scores"]["ps_ratio"] = {"score": ps_score, "interpretation": "Overvalued"}

        # 6. QUALITATIVE ANALYSIS

        # Quality of Earnings Assessment
        if net_income is not None and operating_cash_flow is not None:
            if operating_cash_flow >= net_income * 0.9:
                results["qualitative_summary"]["earnings_quality"] = "High - Operating cash flow supports or exceeds reported earnings"
            elif operating_cash_flow >= net_income * 0.7:
                results["qualitative_summary"]["earnings_quality"] = "Medium - Moderate discrepancy between earnings and cash flow"
            else:
                results["qualitative_summary"]["earnings_quality"] = "Low - Significant disconnect between reported earnings and cash generation"

        # Balance Sheet Strength
        if de_ratio is not None and current_ratio is not None:
            if de_ratio < 0.5 and current_ratio > 2:
                results["qualitative_summary"]["balance_sheet"] = "Very Strong - Low debt levels and strong liquidity"
            elif de_ratio < 1 and current_ratio > 1.5:
                results["qualitative_summary"]["balance_sheet"] = "Strong - Manageable debt and good liquidity"
            elif de_ratio < 2 and current_ratio > 1:
                results["qualitative_summary"]["balance_sheet"] = "Adequate - Moderate debt and acceptable liquidity"
            else:
                results["qualitative_summary"]["balance_sheet"] = "Weak - High debt burden or liquidity concerns"

        # Overall Profitability Assessment
        if roe is not None and net_margin is not None:
            if roe > 15 and net_margin > 10:
                results["qualitative_summary"]["profitability"] = "Excellent - High returns on equity and strong profit margins"
            elif roe > 10 and net_margin > 5:
                results["qualitative_summary"]["profitability"] = "Good - Solid returns and acceptable margins"
            elif roe > 5 and net_margin > 2:
                results["qualitative_summary"]["profitability"] = "Moderate - Adequate but not outstanding performance"
            else:
                results["qualitative_summary"]["profitability"] = "Poor - Low returns and thin margins"

        # Calculate average score and detailed recommendation
        valid_scores = [score_data["score"] for category, score_data in results["scores"].items() if "score" in score_data]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            results["average_score"] = avg_score

            # Generate SWOT analysis
            swot = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": []
            }

            # Analyze scores to build SWOT
            for category, score_data in results["scores"].items():
                if score_data.get("score") == 3:
                    swot["strengths"].append(f"Strong {category.replace('_', ' ')}")
                elif score_data.get("score") == 1:
                    swot["weaknesses"].append(f"Weak {category.replace('_', ' ')}")

            # Add qualitative insights to SWOT
            if results["qualitative_summary"].get("earnings_quality", "").startswith("High"):
                swot["strengths"].append("High quality earnings")
            elif results["qualitative_summary"].get("earnings_quality", "").startswith("Low"):
                swot["weaknesses"].append("Poor earnings quality")

            if results["qualitative_summary"].get("balance_sheet", "").startswith(("Very Strong", "Strong")):
                swot["strengths"].append("Strong balance sheet")
            elif results["qualitative_summary"].get("balance_sheet", "").startswith("Weak"):
                swot["weaknesses"].append("Weak balance sheet")
                swot["threats"].append("Financial distress risk if economic conditions worsen")

            # Add general SWOT items
            if avg_score > 2.5:
                swot["opportunities"].append("Potential for favorable valuation rerating")
            elif avg_score < 1.5:
                swot["threats"].append("Continued underperformance may lead to valuation decline")

            # Formulate detailed recommendation
            if avg_score > 2.5:
                recommendation = "Buy"
                investor_type = "Value and Growth Investors"
                explanation = "The company demonstrates strong financial health with favorable valuation metrics."
                key_factors = [
                    "Solid profitability indicators",
                    "Healthy balance sheet",
                    "Reasonable valuation"
                ]
                if "Strong balance sheet" in swot["strengths"]:
                    key_factors.append("Strong balance sheet provides financial flexibility")

                risk_factors = []
                for weakness in swot["weaknesses"]:
                    risk_factors.append(weakness)

            elif avg_score >= 1.8:
                recommendation = "Hold"
                investor_type = "Current Shareholders and Moderate-Risk Investors"
                explanation = "The company shows moderate financial health with a reasonable valuation profile."
                key_factors = [
                    "Adequate financial metrics",
                    "Some strengths offset by weaknesses"
                ]

                risk_factors = []
                for weakness in swot["weaknesses"]:
                    risk_factors.append(weakness)

            else:
                recommendation = "Sell"
                investor_type = "Risk-Averse Investors"
                explanation = "The company exhibits significant financial weaknesses or excessive valuation."
                key_factors = []

                for weakness in swot["weaknesses"]:
                    key_factors.append(weakness)

                risk_factors = [
                    "Continued financial deterioration possible",
                    "Potential for further valuation decline"
                ]

            # Format the detailed recommendation
            results["recommendation"] = {
                "action": recommendation,
                "suitable_for": investor_type,
                "explanation": explanation,
                "key_factors": key_factors,
                "risk_factors": risk_factors if risk_factors else ["No significant risk factors identified"],
                "watch_list": [
                    "Changes in profit margins",
                    "Debt level trends",
                    "Cash flow quality vs. reported earnings",
                    "Industry-specific dynamics"
                ]
            }

            # Add SWOT analysis
            results["swot_analysis"] = swot

    except Exception as e:
        results["error"] = f"Error calculating ratios: {str(e)}"

    return results

def extract_mda_summary(pdf_text, api_choice="gemini"):
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
            model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_report():
    """
    API endpoint to analyze 10-K financial reports

    Accepts a PDF file upload of a 10-K report, extracts financial data using AI,
    calculates financial ratios, and provides investment recommendations.

    Returns:
        JSON response with financial analysis or error message
    """
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    stock_price = request.form.get('stock_price')
    api_choice = request.form.get('api_choice', 'gemini')  # Default to Gemini
    analysis_detail = request.form.get('analysis_detail', 'standard')  # standard or detailed
    include_mda = request.form.get('include_mda', 'false').lower() == 'true'

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract text from PDF
            pdf_text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"

            # Extract data using selected API
            if api_choice == 'openrouter':
                extracted_data = extract_data_with_openrouter(pdf_text)
            else:  # default to gemini
                extracted_data = extract_data_with_gemini(pdf_text)

            if "error" in extracted_data:
                return jsonify(extracted_data), 400

            # Calculate financial ratios
            results = calculate_financial_ratios(extracted_data, stock_price)

            # Clean up the temporary file
            os.remove(filepath)

            # Add MD&A summary if detailed analysis requested
            if analysis_detail == 'detailed' and pdf_text:
                try:
                    mda_summary = extract_mda_summary(pdf_text, api_choice)
                    if mda_summary and "summary" in mda_summary:
                        results["qualitative_summary"]["mda_highlights"] = mda_summary["summary"]
                        if "risk_factors" in mda_summary:
                            results["qualitative_summary"]["key_risks"] = mda_summary["risk_factors"]
                except Exception as e:
                    results["qualitative_summary"]["mda_error"] = f"Could not extract MD&A summary: {str(e)}"

            return jsonify(results)

        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
