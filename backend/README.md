# 10-K Financial Analysis Backend

This is the backend API for the 10-K Financial Analysis application. It provides endpoints to analyze uploaded 10-K PDF files, extract financial data (including tables and scanned PDFs), calculate comprehensive financial ratios, and generate investment recommendations using advanced LLM-based analysis.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── utils.py                # File helpers and safe conversion
│   ├── pdf_processor.py        # PDF text/table/OCR extraction
│   ├── llm_clients.py          # LLM API clients (Gemini, OpenRouter) with CoT prompting
│   ├── financial_analyzer.py   # Financial ratio calculations and LLM insights integration
│   └── routes.py               # Flask route definitions & interactive APIs
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
- `include_llm_analysis` - Whether to enable advanced LLM-based insights (`true` or `false`, default: `true`)

**Response:**
A JSON object with extracted financial data, calculated ratios, scores, MD&A summary (if requested), LLM-based analyses, financial narratives, and detailed recommendations.

### POST /api/explain_further

Allows users to ask follow-up questions about specific parts of the analysis.

**Request Body (JSON):**
- `context` - The context from the analysis the user is asking about
- `question` - The user's follow-up question
- `api_choice` - API to use (`openrouter` or `gemini`, default: `gemini`)

**Response:**
A JSON object with the explanation answering the user's question.

### POST /api/feedback

Collects user feedback on the quality of LLM-generated analysis.

**Request Body (JSON):**
- `feedback_type` - The type of feedback (positive/negative)
- `analysis_part` - Which part of the analysis the feedback refers to
- `rating` - Numerical rating (0-1)
- `comments` - Optional user comments

**Response:**
A JSON acknowledgment of the feedback submission.

### GET /api/disclaimer

Provides the AI analysis disclaimer text.

**Response:**
A JSON object containing the disclaimer text and limitations of AI-based analysis.

## Features

- **Modular Python Backend**: All logic is organized into clear modules for maintainability.
- **PDF Text/Table/OCR Extraction**: Extracts text and tables from uploaded 10-K PDF files. (Scanned PDF support via OCR is planned or in progress.)
- **Comprehensive Financial Data Extraction**: Uses AI to extract key financial metrics from Income Statement, Balance Sheet, and Cash Flow Statement.
- **Chain-of-Thought (CoT) LLM Prompting**: Uses sophisticated prompting techniques to get higher quality financial analysis from LLMs.
- **Advanced Financial Ratio Calculation**:
  - Profitability, Leverage, Liquidity, Cash Flow, and Valuation Ratios
  - LLM-enhanced ratio interpretations with economic significance
- **Qualitative Analysis**:
  - Earnings Quality, Balance Sheet Strength, Profitability, MD&A Summary, Key Risk Factors
  - LLM-based future earnings outlook predictions with confidence levels
- **Interactive Analysis Features**:
  - Follow-up questions for deeper understanding
  - User feedback collection for continuous improvement
  - Transparent AI reasoning steps display
- **Narrative Financial Insights**:
  - Profitability narrative that connects key metrics into a coherent story
  - Financial health narrative that explains the balance sheet strength
  - Future outlook narrative explaining predicted earnings trajectory
  - Executive summary providing a comprehensive overview
- **SWOT Analysis**: LLM-enhanced identification of Strengths, Weaknesses, Opportunities, and Threats
- **Detailed Investment Recommendations**: Buy/Hold/Sell, investor suitability, key/risk factors, and watch list
- **Security & Error Handling**: Input validation, file type checking, secure filename handling, and comprehensive error reporting

## Contributing

Contributions are welcome! Please submit a Pull Request.
