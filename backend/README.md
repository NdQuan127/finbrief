# 10-K Financial Analysis Backend

This is the backend API for the 10-K Financial Analysis application. It provides endpoints to analyze uploaded 10-K PDF files, extract financial data (including tables and scanned PDFs), calculate comprehensive financial ratios, and generate investment recommendations.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── utils.py                # File helpers and safe conversion
│   ├── pdf_processor.py        # PDF text/table/OCR extraction
│   ├── llm_clients.py          # LLM API clients (Gemini, OpenRouter)
│   ├── financial_analyzer.py   # Financial ratio calculations
│   └── routes.py               # (If present) Flask route definitions
├── requirements.txt
├── README.md
├── templates/
├── static/
```

## Setup Instructions

1. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env-example` to `.env` (if provided)
   - Add your API keys:
     - `OPENROUTER_API_KEY` (from [OpenRouter](https://openrouter.ai/))
     - `GEMINI_API_KEY` (from [Google AI Studio](https://makersuite.google.com/app/apikey))

4. **Run the application:**
   ```bash
   python -m flask run
   # or, if you have a new minimal app.py entrypoint:
   python app.py
   ```

5. The API will be accessible at: `http://localhost:5000`

## API Endpoints

### POST /api/analyze

Upload a 10-K PDF file for comprehensive financial analysis.

**Request Parameters (multipart/form-data):**
- `file` - PDF file (10-K report)
- `stock_price` - Current stock price (optional)
- `api_choice` - API to use for extraction (`openrouter` or `gemini`, default: `gemini`)
- `analysis_detail` - Level of analysis detail (`standard` or `detailed`, default: `standard`)
- `include_mda` - Whether to include MD&A summary (`true` or `false`)

**Response:**
A JSON object with extracted financial data, calculated ratios, scores, MD&A summary (if requested), and detailed recommendations.

## Features

- **Modular Python Backend**: All logic is organized into clear modules for maintainability.
- **PDF Text/Table/OCR Extraction**: Extracts text and tables from uploaded 10-K PDF files. (Scanned PDF support via OCR is planned or in progress.)
- **Comprehensive Financial Data Extraction**: Uses AI to extract key financial metrics from Income Statement, Balance Sheet, and Cash Flow Statement.
- **Advanced Financial Ratio Calculation**:
  - Profitability, Leverage, Liquidity, Cash Flow, and Valuation Ratios
- **Qualitative Analysis**:
  - Earnings Quality, Balance Sheet Strength, Profitability, MD&A Summary, Key Risk Factors
- **SWOT Analysis**: Automated identification of Strengths, Weaknesses, Opportunities, and Threats
- **Detailed Investment Recommendations**: Buy/Hold/Sell, investor suitability, key/risk factors, and watch list
- **Security & Error Handling**: Input validation, file type checking, secure filename handling, and comprehensive error reporting

## Contributing

Contributions are welcome! Please submit a Pull Request.
