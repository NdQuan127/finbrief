from .utils import safe_float # Assuming utils.py is in the same directory

def calculate_financial_ratios(data: dict, stock_price: str | None = None) -> dict:
    """
    Calculate financial ratios based on extracted data from financial reports

    Args:
        data (dict): Extracted financial data
        stock_price (str, optional): Current stock price as a string.
                                    Can be None if not provided.

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
        "trend_analysis": {}, # Placeholder for future trend analysis features
        "qualitative_summary": {}
    }

    # Convert stock_price to float if provided
    _stock_price_float: float | None = None
    if stock_price:
        try:
            _stock_price_float = float(stock_price)
        except ValueError:
            # Handle case where stock_price is not a valid float, perhaps log or return error
            # For now, we'll proceed as if it wasn't provided if conversion fails
            pass

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

    # For backward compatibility, handle old field names if new ones are missing
    if "total_debt" in data and results["extracted_data"].get("short_term_debt") is None and results["extracted_data"].get("long_term_debt") is None:
        total_debt_val = safe_float(data.get("total_debt"))
        results["extracted_data"]["total_debt"] = total_debt_val
    else:
        # Calculate total debt if individual components are present
        short_term_debt_val = results["extracted_data"].get("short_term_debt", 0) or 0
        long_term_debt_val = results["extracted_data"].get("long_term_debt", 0) or 0
        results["extracted_data"]["total_debt"] = short_term_debt_val + long_term_debt_val

    try:
        # Get key values for calculations
        revenue = results["extracted_data"].get("revenue")
        net_income = results["extracted_data"].get("net_income")
        outstanding_shares = results["extracted_data"].get("outstanding_shares")
        stockholders_equity = results["extracted_data"].get("stockholders_equity")
        total_debt = results["extracted_data"].get("total_debt") # This now uses the calculated or backward-compatible value
        total_assets = results["extracted_data"].get("total_assets")
        operating_income = results["extracted_data"].get("operating_income")
        interest_expense = results["extracted_data"].get("interest_expense")
        total_current_assets = results["extracted_data"].get("total_current_assets")
        total_current_liabilities = results["extracted_data"].get("total_current_liabilities")
        inventory = results["extracted_data"].get("inventory")
        gross_profit = results["extracted_data"].get("gross_profit")
        operating_cash_flow = results["extracted_data"].get("operating_cash_flow")
        capex = results["extracted_data"].get("capex")

        # --- 1. PROFITABILITY RATIOS ---
        if outstanding_shares and outstanding_shares > 0 and net_income is not None:
            eps = net_income / outstanding_shares
            results["ratios"]["eps"] = eps
            if _stock_price_float and eps != 0:
                pe_ratio = _stock_price_float / eps
                results["ratios"]["pe_ratio"] = pe_ratio
                if pe_ratio < 15: results["scores"]["pe_ratio"] = {"score": 3, "interpretation": "Undervalued"}
                elif pe_ratio <= 25: results["scores"]["pe_ratio"] = {"score": 2, "interpretation": "Fairly Valued"}
                else: results["scores"]["pe_ratio"] = {"score": 1, "interpretation": "Overvalued"}

        if stockholders_equity and stockholders_equity != 0 and net_income is not None:
            roe = (net_income / stockholders_equity) * 100
            results["ratios"]["roe"] = roe
            if roe > 15: results["scores"]["roe"] = {"score": 3, "interpretation": "Strong"}
            elif roe >= 10: results["scores"]["roe"] = {"score": 2, "interpretation": "Acceptable"}
            else: results["scores"]["roe"] = {"score": 1, "interpretation": "Weak"}

        if total_assets and total_assets != 0 and net_income is not None:
            roa = (net_income / total_assets) * 100
            results["ratios"]["roa"] = roa
            if roa > 5: results["scores"]["roa"] = {"score": 3, "interpretation": "Strong"}
            elif roa >= 2: results["scores"]["roa"] = {"score": 2, "interpretation": "Acceptable"}
            else: results["scores"]["roa"] = {"score": 1, "interpretation": "Weak"}

        if revenue and revenue != 0:
            if net_income is not None:
                net_margin = (net_income / revenue) * 100
                results["ratios"]["net_profit_margin"] = net_margin
                if net_margin > 10: results["scores"]["net_profit_margin"] = {"score": 3, "interpretation": "Strong"}
                elif net_margin >= 5: results["scores"]["net_profit_margin"] = {"score": 2, "interpretation": "Acceptable"}
                else: results["scores"]["net_profit_margin"] = {"score": 1, "interpretation": "Weak"}
            if gross_profit is not None:
                gross_margin = (gross_profit / revenue) * 100
                results["ratios"]["gross_profit_margin"] = gross_margin
                if gross_margin > 40: results["scores"]["gross_profit_margin"] = {"score": 3, "interpretation": "Strong"}
                elif gross_margin >= 20: results["scores"]["gross_profit_margin"] = {"score": 2, "interpretation": "Acceptable"}
                else: results["scores"]["gross_profit_margin"] = {"score": 1, "interpretation": "Weak"}
            if operating_income is not None:
                operating_margin = (operating_income / revenue) * 100
                results["ratios"]["operating_profit_margin"] = operating_margin
                if operating_margin > 15: results["scores"]["operating_profit_margin"] = {"score": 3, "interpretation": "Strong"}
                elif operating_margin >= 8: results["scores"]["operating_profit_margin"] = {"score": 2, "interpretation": "Acceptable"}
                else: results["scores"]["operating_profit_margin"] = {"score": 1, "interpretation": "Weak"}

        # --- 2. LEVERAGE RATIOS ---
        if stockholders_equity and stockholders_equity != 0 and total_debt is not None:
            de_ratio = total_debt / stockholders_equity
            results["ratios"]["de_ratio"] = de_ratio
            if de_ratio < 0.5: results["scores"]["de_ratio"] = {"score": 3, "interpretation": "Low Leverage"}
            elif de_ratio <= 1.0: results["scores"]["de_ratio"] = {"score": 2, "interpretation": "Moderate Leverage"}
            else: results["scores"]["de_ratio"] = {"score": 1, "interpretation": "High Leverage"}

        if total_assets and total_assets != 0 and total_debt is not None:
            debt_ratio = total_debt / total_assets
            results["ratios"]["debt_ratio"] = debt_ratio
            if debt_ratio < 0.3: results["scores"]["debt_ratio"] = {"score": 3, "interpretation": "Low Debt"}
            elif debt_ratio <= 0.6: results["scores"]["debt_ratio"] = {"score": 2, "interpretation": "Moderate Debt"}
            else: results["scores"]["debt_ratio"] = {"score": 1, "interpretation": "High Debt"}

        if interest_expense and interest_expense != 0 and operating_income is not None:
            # Use abs(interest_expense) in case it's reported as negative
            interest_coverage = operating_income / abs(interest_expense)
            results["ratios"]["interest_coverage"] = interest_coverage
            if interest_coverage > 5: results["scores"]["interest_coverage"] = {"score": 3, "interpretation": "Strong"}
            elif interest_coverage >= 2: results["scores"]["interest_coverage"] = {"score": 2, "interpretation": "Acceptable"}
            else: results["scores"]["interest_coverage"] = {"score": 1, "interpretation": "Weak"}

        # --- 3. LIQUIDITY RATIOS ---
        if total_current_liabilities and total_current_liabilities != 0 and total_current_assets is not None:
            current_ratio = total_current_assets / total_current_liabilities
            results["ratios"]["current_ratio"] = current_ratio
            if current_ratio > 2: results["scores"]["current_ratio"] = {"score": 3, "interpretation": "Strong"}
            elif current_ratio >= 1: results["scores"]["current_ratio"] = {"score": 2, "interpretation": "Acceptable"}
            else: results["scores"]["current_ratio"] = {"score": 1, "interpretation": "Weak"}

        if total_current_liabilities and total_current_liabilities != 0 and total_current_assets is not None and inventory is not None:
            quick_ratio = (total_current_assets - inventory) / total_current_liabilities
            results["ratios"]["quick_ratio"] = quick_ratio
            if quick_ratio > 1.5: results["scores"]["quick_ratio"] = {"score": 3, "interpretation": "Strong"}
            elif quick_ratio >= 1: results["scores"]["quick_ratio"] = {"score": 2, "interpretation": "Acceptable"}
            else: results["scores"]["quick_ratio"] = {"score": 1, "interpretation": "Weak"}

        # --- 4. CASH FLOW INDICATORS ---
        if net_income and net_income != 0 and operating_cash_flow is not None:
            # Ensure capex is treated as 0 if None for FCF calculation
            fcf = operating_cash_flow - (capex if capex is not None else 0)
            # Store FCF if calculated
            if operating_cash_flow is not None:
                 results["ratios"]["free_cash_flow_calculated"] = fcf # Storing this calculated FCF

            if fcf != 0: # Check fcf itself, not net_income for division by zero with fcf
                fcf_net_income_ratio = fcf / net_income
                results["ratios"]["fcf_net_income_ratio"] = fcf_net_income_ratio
                if fcf_net_income_ratio > 1.2: results["scores"]["fcf_net_income_ratio"] = {"score": 3, "interpretation": "Strong (High-quality earnings)"}
                elif fcf_net_income_ratio >= 0.8: results["scores"]["fcf_net_income_ratio"] = {"score": 2, "interpretation": "Acceptable (Reliable earnings)"}
                else: results["scores"]["fcf_net_income_ratio"] = {"score": 1, "interpretation": "Weak (Poor earnings quality)"}

        # --- 5. VALUATION RATIOS ---
        if _stock_price_float and stockholders_equity and outstanding_shares and outstanding_shares > 0:
            book_value_per_share = stockholders_equity / outstanding_shares
            if book_value_per_share > 0: # Avoid division by zero or meaningless ratio for negative BVPS
                pb_ratio = _stock_price_float / book_value_per_share
                results["ratios"]["pb_ratio"] = pb_ratio
                if pb_ratio < 1.5: results["scores"]["pb_ratio"] = {"score": 3, "interpretation": "Undervalued"}
                elif pb_ratio <= 3: results["scores"]["pb_ratio"] = {"score": 2, "interpretation": "Fairly Valued"}
                else: results["scores"]["pb_ratio"] = {"score": 1, "interpretation": "Overvalued"}

        if _stock_price_float and revenue and outstanding_shares and outstanding_shares > 0:
            revenue_per_share = revenue / outstanding_shares
            if revenue_per_share > 0: # Avoid division by zero
                ps_ratio = _stock_price_float / revenue_per_share
                results["ratios"]["ps_ratio"] = ps_ratio
                if ps_ratio < 1: results["scores"]["ps_ratio"] = {"score": 3, "interpretation": "Undervalued"}
                elif ps_ratio <= 3: results["scores"]["ps_ratio"] = {"score": 2, "interpretation": "Fairly Valued"}
                else: results["scores"]["ps_ratio"] = {"score": 1, "interpretation": "Overvalued"}

        # --- 6. QUALITATIVE ANALYSIS ---
        # Quality of Earnings Assessment
        if net_income is not None and operating_cash_flow is not None:
            if operating_cash_flow >= net_income * 0.9:
                results["qualitative_summary"]["earnings_quality"] = "High - Operating cash flow supports or exceeds reported earnings"
            elif operating_cash_flow >= net_income * 0.7:
                results["qualitative_summary"]["earnings_quality"] = "Medium - Moderate discrepancy between earnings and cash flow"
            else:
                results["qualitative_summary"]["earnings_quality"] = "Low - Significant disconnect between reported earnings and cash generation"

        # Balance Sheet Strength
        # Use de_ratio from results["ratios"] if available, otherwise skip this part or use a default
        de_ratio_val = results["ratios"].get("de_ratio")
        current_ratio_val = results["ratios"].get("current_ratio")
        if de_ratio_val is not None and current_ratio_val is not None:
            if de_ratio_val < 0.5 and current_ratio_val > 2:
                results["qualitative_summary"]["balance_sheet"] = "Very Strong - Low debt levels and strong liquidity"
            elif de_ratio_val < 1 and current_ratio_val > 1.5:
                results["qualitative_summary"]["balance_sheet"] = "Strong - Manageable debt and good liquidity"
            elif de_ratio_val < 2 and current_ratio_val > 1:
                results["qualitative_summary"]["balance_sheet"] = "Adequate - Moderate debt and acceptable liquidity"
            else:
                results["qualitative_summary"]["balance_sheet"] = "Weak - High debt burden or liquidity concerns"

        # Overall Profitability Assessment
        roe_val = results["ratios"].get("roe")
        net_margin_val = results["ratios"].get("net_profit_margin")
        if roe_val is not None and net_margin_val is not None:
            if roe_val > 15 and net_margin_val > 10:
                results["qualitative_summary"]["profitability"] = "Excellent - High returns on equity and strong profit margins"
            elif roe_val > 10 and net_margin_val > 5:
                results["qualitative_summary"]["profitability"] = "Good - Solid returns and acceptable margins"
            elif roe_val > 5 and net_margin_val > 2:
                results["qualitative_summary"]["profitability"] = "Moderate - Adequate but not outstanding performance"
            else:
                results["qualitative_summary"]["profitability"] = "Poor - Low returns and thin margins"

        # Calculate average score and detailed recommendation
        valid_scores = [score_data["score"] for score_data in results["scores"].values() if isinstance(score_data, dict) and "score" in score_data]
        if valid_scores:
            avg_score = sum(valid_scores) / len(valid_scores)
            results["average_score"] = avg_score

            swot = {
                "strengths": [], "weaknesses": [],
                "opportunities": [], "threats": []
            }

            for category, score_data in results["scores"].items():
                if isinstance(score_data, dict) and "score" in score_data:
                    if score_data.get("score") == 3: swot["strengths"].append(f"Strong {category.replace('_', ' ')}")
                    elif score_data.get("score") == 1: swot["weaknesses"].append(f"Weak {category.replace('_', ' ')}")

            if results["qualitative_summary"].get("earnings_quality", "").startswith("High"):
                swot["strengths"].append("High quality earnings")
            elif results["qualitative_summary"].get("earnings_quality", "").startswith("Low"):
                swot["weaknesses"].append("Poor earnings quality")

            bs_summary = results["qualitative_summary"].get("balance_sheet", "")
            if bs_summary.startswith("Very Strong") or bs_summary.startswith("Strong"):
                swot["strengths"].append("Strong balance sheet")
            elif bs_summary.startswith("Weak"):
                swot["weaknesses"].append("Weak balance sheet")
                swot["threats"].append("Financial distress risk if economic conditions worsen")

            if avg_score > 2.5: swot["opportunities"].append("Potential for favorable valuation rerating")
            elif avg_score < 1.5: swot["threats"].append("Continued underperformance may lead to valuation decline")

            recommendation_details = {}
            if avg_score > 2.5:
                recommendation_details = {
                    "action": "Buy", "suitable_for": "Value and Growth Investors",
                    "explanation": "The company demonstrates strong financial health with favorable valuation metrics.",
                    "key_factors": ["Solid profitability indicators", "Healthy balance sheet", "Reasonable valuation"],
                    "risk_factors": [] # Populated from weaknesses
                }
                if "Strong balance sheet" in swot["strengths"]: recommendation_details["key_factors"].append("Strong balance sheet provides financial flexibility")
            elif avg_score >= 1.8:
                recommendation_details = {
                    "action": "Hold", "suitable_for": "Current Shareholders and Moderate-Risk Investors",
                    "explanation": "The company shows moderate financial health with a reasonable valuation profile.",
                    "key_factors": ["Adequate financial metrics", "Some strengths offset by weaknesses"],
                    "risk_factors": [] # Populated from weaknesses
                }
            else:
                recommendation_details = {
                    "action": "Sell", "suitable_for": "Risk-Averse Investors",
                    "explanation": "The company exhibits significant financial weaknesses or excessive valuation.",
                    "key_factors": [], # Populated from weaknesses
                    "risk_factors": ["Continued financial deterioration possible", "Potential for further valuation decline"]
                }

            # Populate key/risk factors from SWOT
            if "key_factors" in recommendation_details: # For Buy/Hold
                 recommendation_details["key_factors"].extend([w for w in swot["weaknesses"] if w not in recommendation_details["key_factors"]])
            if "risk_factors" in recommendation_details: # For all
                recommendation_details["risk_factors"].extend([w for w in swot["weaknesses"] if w not in recommendation_details["risk_factors"]])
            if not recommendation_details.get("risk_factors"): # Default if empty
                recommendation_details["risk_factors"] = ["No significant immediate risk factors identified from ratios, check qualitative summary."]

            recommendation_details["watch_list"] = [
                "Changes in profit margins", "Debt level trends",
                "Cash flow quality vs. reported earnings", "Industry-specific dynamics"
            ]
            results["recommendation"] = recommendation_details
            results["swot_analysis"] = swot

    except Exception as e:
        results["error"] = f"Error calculating ratios: {str(e)}"

    return results
