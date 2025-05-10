# 10-K Financial Analysis Tool

A web application for analyzing company 10-K annual reports, extracting key financial data, and providing investment recommendations based on calculated financial ratios.

## Project Overview

This application allows users to upload a 10-K annual report PDF, extracts important financial metrics using AI, calculates key financial ratios, and generates investment recommendations based on predefined benchmarks.

### Core Features

1. **File Upload**: Upload 10-K annual report PDFs
2. **AI-Powered Data Extraction**: Extract financial data using Gemini or OpenRouter AI
3. **Financial Ratio Calculation**: Calculate P/E Ratio, ROE, and D/E Ratio
4. **Investment Recommendations**: Get Buy/Hold/Sell recommendations based on financial analysis

## Project Structure

The project is divided into two main components:

- **Frontend (Vue.js)**: User interface for uploading files and viewing analysis results
- **Backend (Python Flask)**: API for processing PDFs, extracting data with AI, and calculating ratios

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env-example` to `.env`
   - Add your API keys:
     - For OpenRouter API: Get an API key from [OpenRouter](https://openrouter.ai/)
     - For Gemini API: Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

5. Run the backend server:
   ```
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run serve
   ```

## Using the Application

1. Access the application at `http://localhost:8080`
2. Upload a 10-K PDF file
3. Optionally enter the current stock price (for P/E ratio calculation)
4. Select the AI model to use for data extraction (Gemini or OpenRouter)
5. Click "Analyze Report" to process the file
6. View the extracted data, calculated ratios, and investment recommendation

## Financial Analysis Metrics

The application calculates and scores the following financial ratios:

- **P/E Ratio (Price-to-Earnings)**:
  - Undervalued: < 15 (Score: 3)
  - Fairly Valued: 15-25 (Score: 2)
  - Overvalued: > 25 (Score: 1)

- **ROE (Return on Equity)**:
  - Strong: > 15% (Score: 3)
  - Acceptable: 10-15% (Score: 2)
  - Weak: < 10% (Score: 1)

- **D/E Ratio (Debt-to-Equity)**:
  - Low Leverage: < 0.5 (Score: 3)
  - Moderate Leverage: 0.5-1.0 (Score: 2)
  - High Leverage: > 1.0 (Score: 1)

Based on the average score, the application provides an overall recommendation:
- Buy: Average Score > 2.5
- Hold: 1.5 <= Average Score <= 2.5
- Sell: Average Score < 1.5

## Technologies Used

- **Frontend**: Vue 3, Vue Router, Axios
- **Backend**: Python, Flask, OpenAI API/Gemini API
- **PDF Processing**: PDFPlumber

## Note on Stock Price Data

For P/E ratio calculation, the application requires the current stock price. This can be:
1. Manually entered by the user
2. In a future enhancement, integrated with a stock price API like Alpha Vantage or Yahoo Finance
