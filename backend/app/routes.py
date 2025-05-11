from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

from .utils import allowed_file
from .pdf_processor import extract_text_from_pdf
from .llm_clients import extract_data_with_openrouter, extract_data_with_gemini, extract_mda_summary
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

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(tempfile.gettempdir(), filename)
            file.save(filepath)

            try:
                # Extract text from PDF
                pdf_text = extract_text_from_pdf(filepath)

                # Extract data using selected API
                if api_choice == 'openrouter':
                    extracted_data = extract_data_with_openrouter(pdf_text)
                else:
                    extracted_data = extract_data_with_gemini(pdf_text)

                if "error" in extracted_data:
                    return jsonify(extracted_data), 400

                # Calculate financial ratios
                results = calculate_financial_ratios(extracted_data, stock_price)

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
