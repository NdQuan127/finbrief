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
export default {
  name: 'Results',
  data() {
    return {
      results: null
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
  background-color: #E0E0E0; /* Grey for N/A */
}

.recommendation-action {
  font-size: 1.75rem;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
  font-weight: bold;
}

.recommendation-text {
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.average-score-badge {
  display: inline-block;
  background: rgba(0, 0, 0, 0.8); /* Darker badge */
  color: #FFFFFF; /* White text */
  padding: 0.5rem 1rem;
  font-weight: bold;
  border: 2px solid #000000;
  /* border-radius: 0; /* No rounded corners, consistent with theme */
}

.data-card .data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.data-point {
  background-color: #FFFDE7; /* Light yellow background */
  border: 2px solid #000000;
  padding: 0.75rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.data-label {
  font-weight: bold;
  margin-right: 0.5rem;
}

.data-value {
  font-size: 1.1rem;
  font-family: 'Courier New', Courier, monospace; /* Monospace for numbers */
}

.ratios-card .ratios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.ratio-detail-item {
  border: 2px solid #000;
  padding: 1rem;
  background-color: #FFFFFF;
}

.ratio-name {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  text-transform: capitalize; /* Nicer formatting for ratio names */
}

.ratio-value-display {
  font-size: 1.5rem; /* Larger ratio value */
  font-weight: bold;
  color: #0000FF; /* Blue accent for values */
  margin-bottom: 0.75rem;
  font-family: 'Courier New', Courier, monospace; /* Monospace for numbers */
}

.interpretation-badge {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
  font-weight: bold;
  border: 2px solid #000;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.score-strong {
  background-color: #A5D6A7; /* Softer Green */
  color: #1B5E20;
}

.score-average {
  background-color: #FFF59D; /* Softer Yellow */
  color: #F57F17;
}

.score-weak {
  background-color: #EF9A9A; /* Softer Red */
  color: #B71C1C;
}

.qualitative-card .qualitative-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px dashed #ccc; /* Dashed separator */
}
.qualitative-card .qualitative-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-subtitle {
  font-size: 1.2rem;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  color: #333;
}

.risk-list {
  list-style: square inside; /* Simple list style */
  padding-left: 0.5rem;
}
.risk-list li {
  margin-bottom: 0.3rem;
}

.swot-card .swot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.swot-category {
  border: 2px solid #000;
  padding: 1rem;
}
.swot-category ul {
  list-style: none; /* Remove default bullets */
  padding-left: 0;
}
.swot-category li {
  padding: 0.25rem;
  border-bottom: 1px dotted #ccc;
}
.swot-category li:last-child {
  border-bottom: none;
}

.swot-title {
  font-size: 1.1rem;
  text-transform: uppercase;
  font-weight: bold;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #000;
}

.swot-strengths { background-color: #E8F5E9; } /* Light green */
.swot-weaknesses { background-color: #FFEBEE; } /* Light red */
.swot-opportunities { background-color: #E3F2FD; } /* Light blue */
.swot-threats { background-color: #FFFDE7; } /* Light yellow */

.actions-footer {
  margin-top: 2rem;
  text-align: center;
}

.no-data-message {
  font-style: italic;
  color: #555;
  padding: 1rem;
  text-align: center;
  border: 2px dashed #ccc;
  background-color: #f9f9f9;
}

</style>
