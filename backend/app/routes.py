from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import datetime

from .utils import allowed_file
from .pdf_processor import extract_text_from_pdf, extract_text_and_tables
from .llm_clients import (
    extract_data_with_openrouter, 
    extract_data_with_gemini,
    extract_financial_data_directly,
    extract_mda_summary,
    analyze_financial_trends_with_llm,
    interpret_financial_ratios_with_llm,
    predict_earnings_outlook_with_llm,
    create_financial_story_with_llm
)
from .financial_analyzer import calculate_financial_ratios

def register_routes(app):
    @app.route('/api/analyze', methods=['POST'])
    def analyze_report():
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        stock_price = request.form.get('stock_price')
        api_choice = request.form.get('api_choice', 'gemini')  # Default to Gemini
        analysis_detail = request.form.get('analysis_detail', 'standard')  # standard or detailed
        include_mda = request.form.get('include_mda', 'false').lower() == 'true'
        include_llm_analysis = request.form.get('include_llm_analysis', 'true').lower() == 'true'
        use_direct_extraction = request.form.get('use_direct_extraction', 'true').lower() == 'true'  # Default to direct extraction

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            file.save(filepath)

            try:
                # Extract text and tables from PDF using improved extraction
                pdf_data = extract_text_and_tables(filepath)
                
                # Also keep the full text for MD&A extraction
                pdf_text = pdf_data.get('text', '')
                
                # Log the extraction stats
                print(f"Extracted PDF data: {len(pdf_data.get('text', ''))} chars of text, "
                      f"{len(pdf_data.get('tables', []))} tables, "
                      f"{len(pdf_data.get('chunks', []))} chunks, "
                      f"{len(pdf_data.get('financial_sections', ''))} chars of financial sections")

                # Extract data using selected API
                if use_direct_extraction:
                    # Use the new direct extraction approach
                    extracted_data = extract_financial_data_directly(pdf_data)
                else:
                    # Use the previous chunk-based approach as fallback
                    if api_choice == 'openrouter':
                        extracted_data = extract_data_with_openrouter(pdf_data)
                    else:
                        extracted_data = extract_data_with_gemini(pdf_data)

                if "error" in extracted_data:
                    return jsonify(extracted_data), 400
                
                # Add timestamp to the data
                extracted_data["analysis_timestamp"] = datetime.datetime.now().isoformat()

                # Calculate financial ratios and get LLM analysis
                results = calculate_financial_ratios(
                    extracted_data, 
                    stock_price, 
                    api_choice, 
                    include_llm_analysis
                )

                # Clean up the temporary file
                os.remove(filepath)

                # Add MD&A summary if detailed analysis requested or include_mda is True
                if (analysis_detail == 'detailed' or include_mda) and pdf_text:
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
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({"error": f"Error processing file: {str(e)}"}), 500

        return jsonify({"error": "File type not allowed"}), 400
    
    @app.route('/api/explain_further', methods=['POST'])
    def explain_further():
        """
        Endpoint for providing additional explanations or answering follow-up questions
        about specific parts of the analysis.
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        context = data.get('context', '')
        question = data.get('question', '')
        api_choice = data.get('api_choice', 'gemini')
        
        if not context or not question:
            return jsonify({"error": "Both 'context' and 'question' are required"}), 400
        
        # Prepare a prompt for the LLM to explain the context further
        prompt = f"""
        You are a financial analyst assistant. A user has asked a follow-up question about 
        a specific part of a financial analysis.
        
        Here is the context from the analysis:
        {context}
        
        The user's question is:
        {question}
        
        Please provide a clear, helpful explanation that addresses the user's question directly.
        Explain financial concepts in simple terms that would be understandable to a non-expert.
        """
        
        # Use the appropriate LLM client based on api_choice
        if api_choice == 'openrouter':
            from .llm_clients import _call_openrouter_api
            response = _call_openrouter_api(prompt, "anthropic/claude-3-opus:free")
        else:
            from .llm_clients import _call_gemini_api
            response = _call_gemini_api(prompt)
        
        # If the LLM returns a JSON with an explanation, extract it
        if isinstance(response, dict) and "explanation" in response:
            return jsonify({"explanation": response["explanation"]})
        elif isinstance(response, dict) and "error" not in response:
            # If we get a valid response but not in the expected format, 
            # the LLM might have returned the explanation directly
            return jsonify({"explanation": str(response)})
        elif isinstance(response, dict) and "error" in response:
            return jsonify({"error": response["error"]}), 400
        else:
            # Convert the response to a string if it's something else
            return jsonify({"explanation": str(response)})
    
    @app.route('/api/feedback', methods=['POST'])
    def submit_feedback():
        """
        Endpoint for collecting user feedback on the quality of LLM analysis.
        This could be used for future improvements.
        """
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        feedback_type = data.get('feedback_type', '')
        analysis_part = data.get('analysis_part', '')
        rating = data.get('rating', 0)
        comments = data.get('comments', '')
        
        if not feedback_type or not analysis_part:
            return jsonify({"error": "Both 'feedback_type' and 'analysis_part' are required"}), 400
        
        # Here you would typically store the feedback in a database
        # For now, we'll just acknowledge receipt
        
        return jsonify({
            "status": "success",
            "message": "Thank you for your feedback. It will help us improve future analyses.",
            "received": {
                "feedback_type": feedback_type,
                "analysis_part": analysis_part,
                "rating": rating,
                "comments": comments
            }
        })
    
    @app.route('/api/disclaimer', methods=['GET'])
    def get_disclaimer():
        """
        Endpoint to provide the AI analysis disclaimer text to display to users.
        """
        return jsonify({
            "disclaimer": "This analysis is generated by a Large Language Model (AI) and is for informational purposes only, not professional investment advice. Accuracy depends on input data quality and AI capabilities. Always consult with a financial professional before making investment decisions.",
            "limitations": [
                "AI may misinterpret complex financial information",
                "Financial analysis requires industry context that AI may lack",
                "Historical data may not predict future performance",
                "AI cannot account for macroeconomic factors unless explicitly provided"
            ],
            "version": "FinBrief AI Analysis v1.0"
        })
