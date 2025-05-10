# 10-K Financial Analysis Backend

This is the backend API for the 10-K Financial Analysis application. It provides functionality to analyze uploaded 10-K PDF files, extract financial data, and calculate comprehensive financial ratios for investment decision-making.

## Setup Instructions

1. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env-example` to `.env`
   - Add your API keys:
     - For OpenRouter API: Get an API key from [OpenRouter](https://openrouter.ai/)
     - For Gemini API: Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Run the application:
   ```
   python app.py
   ```

5. The API will be accessible at: `http://localhost:5000`

## API Endpoints

### POST /api/analyze

Upload a 10-K PDF file for comprehensive financial analysis.

**Request Parameters (multipart/form-data):**
- `file` - PDF file (10-K report)
- `stock_price` - Current stock price (optional)
- `api_choice` - API to use for extraction (openrouter or gemini, default: gemini)
- `analysis_detail` - Level of analysis detail (standard or detailed, default: standard)

**Response:**
A JSON object with extracted financial data, calculated ratios, scores, and detailed recommendations.

## Features

- **PDF Text Extraction**: Extracts text from uploaded 10-K PDF files
- **Comprehensive Financial Data Extraction**: Uses AI to extract key financial metrics from Income Statement, Balance Sheet and Cash Flow Statement
- **Advanced Financial Ratio Calculation**:
  - **Profitability Ratios**: EPS, ROE, ROA, Profit Margins (Gross, Operating, Net)
  - **Leverage Ratios**: D/E Ratio, Debt Ratio, Interest Coverage
  - **Liquidity Ratios**: Current Ratio, Quick Ratio
  - **Cash Flow Indicators**: Free Cash Flow, FCF/Net Income
  - **Valuation Ratios**: P/E, P/B, P/S
- **Qualitative Analysis**:
  - Earnings Quality Assessment
  - Balance Sheet Strength Evaluation
  - Overall Profitability Assessment
  - MD&A Summary (in detailed mode)
  - Key Risk Factors (in detailed mode)
- **SWOT Analysis**: Automated identification of Strengths, Weaknesses, Opportunities, and Threats
- **Detailed Investment Recommendations**:
  - Buy/Hold/Sell recommendations
  - Investor type suitability
  - Key factors supporting the recommendation
  - Risk factors to consider
  - Key metrics to watch

## Technical Details

- **Flask-based API**: Built with Python Flask for robust API service
- **AI Integration**: Uses Gemini API (Google) or OpenRouter API for financial data extraction
- **PDF Processing**: Uses pdfplumber for efficient text extraction
- **Security Features**: Input validation, file type checking, and secure filename handling
- **Error Handling**: Comprehensive error reporting throughout the API

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
