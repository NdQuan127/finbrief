<template>
  <div class="results-page">
    <div v-if="!results" class="no-results card">
      <h2 class="card-title">No Results Found</h2>
      <p>It seems no analysis data is available. Please go back and upload a 10-K report first.</p>
      <router-link to="/" class="btn btn-primary">Go Back to Upload</router-link>
    </div>

    <div v-else class="results-content">
      <div class="card company-overview-card">
        <h2 class="card-title company-name">{{ results.company_name || 'Company Analysis' }}</h2>
        <p class="fiscal-info">Fiscal Year: <strong>{{ results.fiscal_year || 'N/A' }}</strong> | Period: <strong>{{ results.fiscal_period || 'N/A' }}</strong></p>

        <div class="recommendation-highlight card" :class="recommendationClass">
          <h3 class="recommendation-action">
            Recommendation: {{ results.recommendation?.action || 'N/A' }}
          </h3>
          <p class="recommendation-text">
            {{ results.recommendation?.explanation || 'No detailed explanation provided.' }}
          </p>
          <div v-if="results.average_score" class="average-score-badge">
            Avg. Score: {{ averageScoreFormatted }}
          </div>
        </div>
        
        <!-- LLM Reasoning Steps Toggle -->
        <div v-if="hasReasoningSteps" class="reasoning-steps-toggle-container">
          <button @click="toggleReasoningSteps" class="reasoning-steps-toggle">
            {{ reasoningStepsVisible ? 'Hide AI Reasoning Steps' : 'Show AI Reasoning Steps' }}
          </button>
          <div v-if="reasoningStepsVisible" class="reasoning-steps-container">
            <div v-for="(steps, analysisType) in results.analysis_reasoning_steps" :key="analysisType" class="reasoning-steps-section">
              <h4>{{ formatAnalysisType(analysisType) }}</h4>
              <div v-if="Array.isArray(steps)" class="reasoning-steps-list">
                <div v-for="(step, index) in steps" :key="index" class="reasoning-step">
                  <span class="step-number">Step {{ index + 1 }}:</span>
                  {{ step }}
                </div>
              </div>
              <div v-else class="reasoning-step">
                {{ steps }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card data-card">
        <h2 class="card-title">Key Financial Data</h2>
        <div class="data-grid" v-if="results.extracted_data">
          <div class="data-point">
            <span class="data-label">Net Income:</span>
            <span class="data-value">${{ formatNumber(results.extracted_data.net_income) }}</span>
          </div>
          <div class="data-point">
            <span class="data-label">Revenue:</span>
            <span class="data-value">${{ formatNumber(results.extracted_data.revenue) }}</span>
          </div>
          <div class="data-point">
            <span class="data-label">Total Assets:</span>
            <span class="data-value">${{ formatNumber(results.extracted_data.total_assets) }}</span>
          </div>
          <div class="data-point">
            <span class="data-label">Total Liabilities:</span>
            <span class="data-value">${{ formatNumber(results.extracted_data.total_liabilities) }}</span>
          </div>
          <div class="data-point">
            <span class="data-label">Equity:</span>
            <span class="data-value">${{ formatNumber(results.extracted_data.stockholders_equity) }}</span>
          </div>
          <div class="data-point">
            <span class="data-label">Shares Out:</span>
            <span class="data-value">{{ formatNumber(results.extracted_data.outstanding_shares) }}</span>
          </div>
        </div>
        <p v-else class="no-data-message">Extracted financial data is not available.</p>
      </div>

      <div class="card ratios-card">
        <h2 class="card-title">Financial Ratios & Scores</h2>
        <div class="ratios-grid" v-if="results.ratios && Object.keys(results.ratios).length">
          <div v-for="(value, key) in results.ratios" :key="key" class="ratio-detail-item">
            <h4 class="ratio-name">{{ formatRatioName(key) }}</h4>
            <p class="ratio-value-display">{{ formatRatioValue(key, value) }}</p>
            <div v-if="results.scores && results.scores[key]"
                 class="interpretation-badge"
                 :class="getScoreClass(results.scores[key].score)">
              {{ results.scores[key].interpretation }}
            </div>
          </div>
        </div>
        <p v-else class="no-data-message">Financial ratios are not available.</p>
      </div>

      <div v-if="results.qualitative_summary && (results.qualitative_summary.mda_highlights || results.qualitative_summary.key_risks || results.qualitative_summary.earnings_quality)" class="card qualitative-card">
        <h2 class="card-title">Qualitative Analysis</h2>
        <div v-if="results.qualitative_summary.mda_highlights" class="qualitative-section">
          <h4 class="section-subtitle">MD&A Summary</h4>
          <p>{{ results.qualitative_summary.mda_highlights }}</p>
        </div>
        <div v-if="results.qualitative_summary.key_risks && results.qualitative_summary.key_risks.length" class="qualitative-section">
          <h4 class="section-subtitle">Key Risk Factors</h4>
          <ul class="risk-list">
            <li v-for="(risk, idx) in results.qualitative_summary.key_risks" :key="idx">{{ risk }}</li>
          </ul>
        </div>
         <div v-if="results.qualitative_summary.earnings_quality" class="qualitative-section">
          <h4 class="section-subtitle">Earnings Quality</h4>
          <p>{{ results.qualitative_summary.earnings_quality }}</p>
        </div>
        <div v-if="results.qualitative_summary.balance_sheet" class="qualitative-section">
          <h4 class="section-subtitle">Balance Sheet Strength</h4>
          <p>{{ results.qualitative_summary.balance_sheet }}</p>
        </div>
        <div v-if="results.qualitative_summary.profitability" class="qualitative-section">
          <h4 class="section-subtitle">Overall Profitability</h4>
          <p>{{ results.qualitative_summary.profitability }}</p>
        </div>
        <div v-if="results.qualitative_summary.mda_error" class="alert alert-warning">
          MD&A Summary Error: {{ results.qualitative_summary.mda_error }}
        </div>
      </div>

      <!-- New Narrative Insights Section -->
      <div v-if="results.financial_story && hasNarrativeInsights" class="card narrative-card">
        <h2 class="card-title">
          Narrative Insights
          <span class="ai-badge">AI Generated</span>
        </h2>
        
        <div v-if="results.financial_story.executive_summary" class="narrative-section executive-summary">
          <h4 class="section-subtitle">Executive Summary</h4>
          <p>{{ results.financial_story.executive_summary }}</p>
        </div>
        
        <div v-if="results.financial_story.profitability_narrative" class="narrative-section">
          <h4 class="section-subtitle">Profitability Story</h4>
          <p>{{ results.financial_story.profitability_narrative }}</p>
          <div class="interaction-controls">
            <button @click="askFollowUp('profitability_narrative')" class="btn btn-sm btn-outline-primary">
              <i class="icon-question"></i> Ask Follow-up
            </button>
            <div class="feedback-controls">
              <button @click="submitFeedback('profitability_narrative', 'positive')" class="btn-icon positive">
                <i class="icon-thumbs-up"></i>
              </button>
              <button @click="submitFeedback('profitability_narrative', 'negative')" class="btn-icon negative">
                <i class="icon-thumbs-down"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="results.financial_story.financial_health_narrative" class="narrative-section">
          <h4 class="section-subtitle">Financial Health Story</h4>
          <p>{{ results.financial_story.financial_health_narrative }}</p>
          <div class="interaction-controls">
            <button @click="askFollowUp('financial_health_narrative')" class="btn btn-sm btn-outline-primary">
              <i class="icon-question"></i> Ask Follow-up
            </button>
            <div class="feedback-controls">
              <button @click="submitFeedback('financial_health_narrative', 'positive')" class="btn-icon positive">
                <i class="icon-thumbs-up"></i>
              </button>
              <button @click="submitFeedback('financial_health_narrative', 'negative')" class="btn-icon negative">
                <i class="icon-thumbs-down"></i>
              </button>
            </div>
          </div>
        </div>
        
        <div v-if="results.financial_story.future_outlook_narrative" class="narrative-section">
          <h4 class="section-subtitle">Future Outlook</h4>
          <p>{{ results.financial_story.future_outlook_narrative }}</p>
          <div class="interaction-controls">
            <button @click="askFollowUp('future_outlook_narrative')" class="btn btn-sm btn-outline-primary">
              <i class="icon-question"></i> Ask Follow-up
            </button>
            <div class="feedback-controls">
              <button @click="submitFeedback('future_outlook_narrative', 'positive')" class="btn-icon positive">
                <i class="icon-thumbs-up"></i>
              </button>
              <button @click="submitFeedback('future_outlook_narrative', 'negative')" class="btn-icon negative">
                <i class="icon-thumbs-down"></i>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Follow-up Question Dialog -->
        <div v-if="showFollowUpDialog" class="follow-up-dialog">
          <div class="dialog-content">
            <h4>Ask a Follow-up Question</h4>
            <p class="context-preview">{{ getContextPreview() }}</p>
            <input 
              v-model="followUpQuestion" 
              placeholder="Type your question here..." 
              class="form-control"
              @keyup.enter="submitFollowUpQuestion"
            />
            <div class="dialog-actions">
              <button @click="cancelFollowUp" class="btn btn-sm btn-outline-secondary">Cancel</button>
              <button @click="submitFollowUpQuestion" :disabled="!followUpQuestion || isLoading" class="btn btn-sm btn-primary">
                <span v-if="isLoading" class="loading-spinner-sm"></span>
                <span v-else>Submit</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Follow-up Answer Display -->
        <div v-if="followUpAnswer" class="follow-up-answer">
          <h5>Answer to your question:</h5>
          <p>{{ followUpAnswer }}</p>
          <button @click="clearFollowUpAnswer" class="btn btn-sm btn-outline-secondary">Close</button>
        </div>
      </div>
      
      <!-- Earnings Outlook Card -->
      <div v-if="results.llm_earnings_outlook && hasEarningsOutlook" class="card earnings-outlook-card">
        <h2 class="card-title">
          Earnings Outlook
          <span class="ai-badge">AI Prediction</span>
        </h2>
        
        <div class="earnings-prediction">
          <div class="prediction-header">
            <h4 class="prediction-direction" :class="getPredictionClass()">
              {{ results.llm_earnings_outlook.direction || 'Unknown' }}
              <span class="prediction-magnitude">{{ results.llm_earnings_outlook.magnitude }}</span>
            </h4>
            <div class="confidence-indicator">
              Confidence: {{ formatConfidence(results.llm_earnings_outlook.confidence) }}
            </div>
          </div>
          
          <div class="prediction-rationale">
            <h5>Rationale:</h5>
            <p>{{ results.llm_earnings_outlook.rationale }}</p>
          </div>
          
          <div class="interaction-controls">
            <button @click="askFollowUp('earnings_outlook')" class="btn btn-sm btn-outline-primary">
              <i class="icon-question"></i> Ask Follow-up
            </button>
            <div class="feedback-controls">
              <button @click="submitFeedback('earnings_outlook', 'positive')" class="btn-icon positive">
                <i class="icon-thumbs-up"></i>
              </button>
              <button @click="submitFeedback('earnings_outlook', 'negative')" class="btn-icon negative">
                <i class="icon-thumbs-down"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="results.swot_analysis" class="card swot-card">
        <h2 class="card-title">SWOT Analysis</h2>
        <div class="swot-grid">
          <div class="swot-category swot-strengths">
            <h4 class="swot-title">Strengths</h4>
            <ul><li v-for="(item, i) in results.swot_analysis.strengths" :key="`s-${i}`">{{ item }}</li></ul>
          </div>
          <div class="swot-category swot-weaknesses">
            <h4 class="swot-title">Weaknesses</h4>
            <ul><li v-for="(item, i) in results.swot_analysis.weaknesses" :key="`w-${i}`">{{ item }}</li></ul>
          </div>
          <div class="swot-category swot-opportunities">
            <h4 class="swot-title">Opportunities</h4>
            <ul><li v-for="(item, i) in results.swot_analysis.opportunities" :key="`o-${i}`">{{ item }}</li></ul>
          </div>
          <div class="swot-category swot-threats">
            <h4 class="swot-title">Threats</h4>
            <ul><li v-for="(item, i) in results.swot_analysis.threats" :key="`t-${i}`">{{ item }}</li></ul>
          </div>
        </div>
      </div>

      <div class="actions-footer">
        <router-link to="/" class="btn btn-secondary">Analyze Another Report</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Results',
  data() {
    return {
      results: null,
      showFollowUpDialog: false,
      followUpQuestion: '',
      followUpAnswer: '',
      currentContext: '',
      currentContextType: '',
      isLoading: false,
      feedbackSubmitted: {},
      reasoningStepsVisible: false
    }
  },
  computed: {
    averageScoreFormatted() {
      return this.results && typeof this.results.average_score === 'number'
        ? this.results.average_score.toFixed(2)
        : 'N/A';
    },
    recommendationClass() {
      if (!this.results || !this.results.recommendation || !this.results.recommendation.action) return 'recommendation-neutral';
      const action = this.results.recommendation.action.toLowerCase();
      if (action === 'buy') return 'recommendation-buy';
      if (action === 'sell') return 'recommendation-sell';
      return 'recommendation-hold';
    },
    hasNarrativeInsights() {
      if (!this.results || !this.results.financial_story) return false;
      const story = this.results.financial_story;
      return !!(story.profitability_narrative || story.financial_health_narrative || 
                story.future_outlook_narrative || story.executive_summary);
    },
    hasEarningsOutlook() {
      if (!this.results || !this.results.llm_earnings_outlook) return false;
      return !!(this.results.llm_earnings_outlook.direction || 
                this.results.llm_earnings_outlook.rationale);
    },
    hasReasoningSteps() {
      return !!(this.results && this.results.analysis_reasoning_steps && 
                Object.keys(this.results.analysis_reasoning_steps).length > 0);
    }
  },
  methods: {
    formatNumber(value) {
      if (typeof value !== 'number') return 'N/A';
      return new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
    },
    formatDecimal(value) {
      if (typeof value !== 'number') return 'N/A';
      return Number(value).toFixed(2);
    },
    formatRatioName(key) {
      const name = key.replace(/_/g, ' ');
      return name.charAt(0).toUpperCase() + name.slice(1);
    },
    formatRatioValue(key, value) {
      if (typeof value !== 'number') return 'N/A';
      const percentageRatios = ['roe', 'roa', 'net_profit_margin', 'gross_profit_margin', 'operating_profit_margin'];
      if (percentageRatios.includes(key)) {
        return `${value.toFixed(2)}%`;
      }
      if (key === 'eps') {
         return `$${value.toFixed(2)}`;
      }
      return value.toFixed(2);
    },
    getScoreClass(score) {
      if (score === 3) return 'score-strong';
      if (score === 2) return 'score-average';
      if (score === 1) return 'score-weak';
      return '';
    },
    formatConfidence(confidence) {
      if (typeof confidence !== 'number') return 'N/A';
      // Convert confidence to percentage
      return `${(confidence * 100).toFixed(0)}%`;
    },
    getPredictionClass() {
      if (!this.results || !this.results.llm_earnings_outlook) return '';
      const direction = this.results.llm_earnings_outlook.direction;
      if (!direction) return '';
      
      const directionLower = direction.toLowerCase();
      if (directionLower.includes('increase')) return 'prediction-increase';
      if (directionLower.includes('decrease')) return 'prediction-decrease';
      return 'prediction-stable';
    },
    askFollowUp(contextType) {
      this.followUpAnswer = ''; // Clear any previous answer
      this.showFollowUpDialog = true;
      this.currentContextType = contextType;
      
      // Set the appropriate context based on the type
      if (contextType === 'earnings_outlook' && this.results.llm_earnings_outlook) {
        this.currentContext = this.results.llm_earnings_outlook.rationale;
      } else if (this.results.financial_story && this.results.financial_story[contextType]) {
        this.currentContext = this.results.financial_story[contextType];
      }
    },
    getContextPreview() {
      if (!this.currentContext) return '';
      // Return a shortened version of the context for the UI
      return this.currentContext.length > 100 
        ? this.currentContext.substring(0, 100) + '...' 
        : this.currentContext;
    },
    cancelFollowUp() {
      this.showFollowUpDialog = false;
      this.followUpQuestion = '';
    },
    clearFollowUpAnswer() {
      this.followUpAnswer = '';
    },
    async submitFollowUpQuestion() {
      if (!this.followUpQuestion || !this.currentContext) {
        return;
      }
      
      this.isLoading = true;
      
      try {
        const response = await axios.post('http://localhost:5000/api/explain_further', {
          context: this.currentContext,
          question: this.followUpQuestion,
          api_choice: 'gemini' // Could make this configurable
        });
        
        if (response.data && response.data.explanation) {
          this.followUpAnswer = response.data.explanation;
        } else {
          this.followUpAnswer = "Sorry, I couldn't generate a clear answer to your question.";
        }
        
        // Close the dialog and show the answer
        this.showFollowUpDialog = false;
        
      } catch (error) {
        console.error('Error submitting follow-up question:', error);
        this.followUpAnswer = "An error occurred while processing your question. Please try again.";
      } finally {
        this.isLoading = false;
      }
    },
    async submitFeedback(analysisType, feedbackType) {
      // Check if feedback was already submitted for this analysis type
      const feedbackKey = `${analysisType}_${feedbackType}`;
      if (this.feedbackSubmitted[feedbackKey]) {
        return; // Already submitted this feedback
      }
      
      try {
        await axios.post('http://localhost:5000/api/feedback', {
          feedback_type: feedbackType,
          analysis_part: analysisType,
          rating: feedbackType === 'positive' ? 1 : 0,
          comments: ''
        });
        
        // Mark this feedback as submitted
        this.$set(this.feedbackSubmitted, feedbackKey, true);
        
        // Could show a temporary confirmation message here
        
      } catch (error) {
        console.error('Error submitting feedback:', error);
      }
    },
    toggleReasoningSteps() {
      this.reasoningStepsVisible = !this.reasoningStepsVisible;
    },
    formatAnalysisType(analysisType) {
      const formattedType = analysisType.replace(/_/g, ' ');
      return formattedType.charAt(0).toUpperCase() + formattedType.slice(1);
    }
  },
  mounted() {
    try {
      const savedResults = localStorage.getItem('analysisResults');
      if (savedResults) {
        this.results = JSON.parse(savedResults);
        console.log(this.results); // For debugging
      }
    } catch (error) {
      console.error('Error loading results:', error);
      this.results = null; // Ensure results is null on error
    }
  }
}
</script>

<style scoped>
.results-page {
  /* Uses global styles for max-width and margin from App.vue main tag */
}

.no-results {
  text-align: center;
  padding: 2rem;
  border: 3px dashed #000; /* Dashed border for emphasis */
}
.no-results p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.results-content {
  display: flex;
  flex-direction: column;
  gap: 2rem; /* Consistent gap between cards */
}

.company-overview-card .company-name {
  font-size: 2rem; /* Larger company name */
  border-bottom: none; /* Remove default card title border if not desired here */
  margin-bottom: 0.25rem;
}

.fiscal-info {
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.recommendation-highlight {
  padding: 1.5rem;
  border: 3px solid #000000;
  color: #000000; /* Black text for all recommendation cards */
  box-shadow: 4px 4px 0px #000000; /* Consistent shadow */
  margin-top: 1rem;
}

.recommendation-buy {
  background-color: #A5D6A7; /* Softer Green */
}

.recommendation-hold {
  background-color: #FFF59D; /* Softer Yellow */
}

.recommendation-sell {
  background-color: #EF9A9A; /* Softer Red */
}

.recommendation-neutral {
  background-color: #E0E0E0; /* Neutral Gray */
}

.recommendation-action {
  font-size: 1.35rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.recommendation-text {
  margin-bottom: 0;
  font-size: 1.1rem;
}

.average-score-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #000000;
  color: #FFFFFF;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.75rem;
}

.data-card, .ratios-card, .qualitative-card, .swot-card, .narrative-card, .earnings-outlook-card {
  border: 3px solid #000000;
  box-shadow: 4px 4px 0px #000000;
  background-color: #FFFFFF;
  border-radius: 8px;
  overflow: hidden;
}

.card-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 1.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #000000;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-subtitle {
  font-weight: bold;
  margin-top: 0;
  font-size: 1.15rem;
  margin-bottom: 0.5rem;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.data-point {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  border: 1px solid #EEEEEE;
  border-radius: 4px;
  background-color: #FAFAFA;
}

.data-label {
  font-weight: 500;
  font-size: 0.85rem;
  color: #333;
  margin-bottom: 0.25rem;
}

.data-value {
  font-weight: bold;
  font-size: 1.25rem;
}

.ratios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.ratio-detail-item {
  padding: 0.75rem;
  border: 1px solid #EEEEEE;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  background-color: #FAFAFA;
}

.ratio-name {
  margin: 0 0 0.25rem 0;
  font-weight: 600;
  font-size: 0.9rem;
}

.ratio-value-display {
  font-weight: bold;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.interpretation-badge {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 50px;
  color: #FFFFFF;
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
}

.qualitative-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #EEEEEE;
}

.qualitative-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.risk-list {
  margin: 0;
  padding-left: 1.5rem;
}

.risk-list li {
  margin-bottom: 0.5rem;
}

.score-strong {
  background-color: #66BB6A; /* Green */
}

.score-average {
  background-color: #FFCA28; /* Amber */
}

.score-weak {
  background-color: #EF5350; /* Red */
}

.no-data-message {
  padding: 1rem;
  background-color: #F5F5F5;
  border-radius: 4px;
  text-align: center;
  color: #666;
  font-style: italic;
}

.swot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.swot-category {
  padding: 1rem;
  border-radius: 6px;
}

.swot-strengths {
  background-color: #E8F5E9; /* Light Green */
  border-left: 4px solid #66BB6A;
}

.swot-weaknesses {
  background-color: #FFEBEE; /* Light Red */
  border-left: 4px solid #EF5350;
}

.swot-opportunities {
  background-color: #E3F2FD; /* Light Blue */
  border-left: 4px solid #42A5F5;
}

.swot-threats {
  background-color: #FFF3E0; /* Light Orange */
  border-left: 4px solid #FFA726;
}

.swot-title {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-weight: bold;
  color: #333;
}

.swot-category ul {
  margin: 0;
  padding-left: 1.5rem;
}

.swot-category li {
  margin-bottom: 0.4rem;
}

.swot-category li:last-child {
  margin-bottom: 0;
}

.actions-footer {
  margin-top: 2.5rem;
  text-align: center;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background-color: #E0E0E0;
  color: #000000;
  border: 2px solid #000000;
  border-radius: 4px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
  box-shadow: 2px 2px 0 #000000;
}

.btn-secondary:hover {
  background-color: #D0D0D0;
  transform: translate(2px, 2px);
  box-shadow: 0 0 0 #000000;
}

/* New styles for narrative insights */
.narrative-card, .earnings-outlook-card {
  position: relative;
}

.ai-badge {
  font-size: 0.75rem;
  background-color: #7B1FA2;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: normal;
  margin-left: 0.5rem;
}

.executive-summary {
  background-color: #F5F5F5;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #000000;
  margin-bottom: 1.5rem;
}

.narrative-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px dashed #CCCCCC;
  position: relative;
}

.narrative-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.interaction-controls {
  display: flex;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.feedback-controls {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 0.25rem;
  color: #757575;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon.positive {
  color: #388E3C;
}

.btn-icon.positive:hover {
  background-color: #E8F5E9;
}

.btn-icon.negative {
  color: #D32F2F;
}

.btn-icon.negative:hover {
  background-color: #FFEBEE;
}

.follow-up-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog-content {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.dialog-content h4 {
  margin-top: 0;
  margin-bottom: 1rem;
}

.context-preview {
  background-color: #F5F5F5;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  color: #666;
  font-style: italic;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.follow-up-answer {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #E8F5E9;
  border-radius: 6px;
}

.follow-up-answer h5 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #388E3C;
}

.follow-up-answer p {
  margin-bottom: 1rem;
}

.earnings-prediction {
  padding: 1rem;
  border-radius: 6px;
  background-color: #F5F5F5;
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.prediction-direction {
  font-size: 1.35rem;
  margin: 0;
  display: flex;
  align-items: center;
}

.prediction-direction.prediction-increase {
  color: #388E3C;
}

.prediction-direction.prediction-decrease {
  color: #D32F2F;
}

.prediction-direction.prediction-stable {
  color: #FFA000;
}

.prediction-magnitude {
  font-size: 0.9rem;
  background-color: #F5F5F5;
  border: 1px solid #DDDDDD;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  margin-left: 0.5rem;
  color: #333;
}

.confidence-indicator {
  background-color: #000000;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.prediction-rationale {
  margin-bottom: 1rem;
}

.prediction-rationale h5 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.prediction-rationale p {
  margin: 0;
}

.loading-spinner-sm {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #FFFFFF;
  animation: spin 1s linear infinite;
}

.reasoning-steps-container {
  background-color: #F5F5F5;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.reasoning-steps-toggle {
  background: none;
  border: none;
  color: #1976D2;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: underline;
  padding: 0;
  display: flex;
  align-items: center;
}

.reasoning-step {
  margin-bottom: 0.75rem;
  padding-left: 1rem;
  border-left: 2px solid #BDBDBD;
}

.reasoning-step:last-child {
  margin-bottom: 0;
}

.step-number {
  font-weight: bold;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .swot-grid {
    grid-template-columns: 1fr;
  }
  
  .ratios-grid, .data-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .prediction-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .confidence-indicator {
    margin-top: 0.5rem;
  }
}
</style>
