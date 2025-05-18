<template>
  <div class="home">
    <div class="card upload-card">
      <h2 class="card-title">Upload & Analyze 10-K Report</h2>
      <p class="subtitle">Provide a 10-K PDF and select your analysis options below.</p>

      <div v-if="error" class="alert alert-danger">
        <strong>Error:</strong> {{ error }}
      </div>

      <div v-if="disclaimer" class="ai-disclaimer">
        <p><strong>AI Disclaimer:</strong> {{ disclaimer.disclaimer }}</p>
        <ul v-if="showFullDisclaimer" class="limitations-list">
          <li v-for="(limitation, index) in disclaimer.limitations" :key="index">
            {{ limitation }}
          </li>
        </ul>
        <button class="btn-link" @click="showFullDisclaimer = !showFullDisclaimer">
          {{ showFullDisclaimer ? 'Hide Details' : 'Show Limitations' }}
        </button>
      </div>

      <form @submit.prevent="uploadFile" enctype="multipart/form-data">
        <fieldset class="form-section">
          <legend class="section-title">1. Report File</legend>
          <div class="form-group">
            <label for="fileUpload" class="form-label">10-K PDF Document:</label>
            <input
              type="file"
              id="fileUpload"
              ref="fileInput"
              @change="handleFileChange"
              accept=".pdf"
              class="form-control file-input"
              required
            />
            <small class="input-hint">Ensure the PDF is text-selectable for best results.</small>
          </div>
        </fieldset>

        <fieldset class="form-section">
          <legend class="section-title">2. Analysis Options</legend>
          <div class="form-group">
            <label for="stockPrice" class="form-label">Current Stock Price (Optional):</label>
            <input
              type="number"
              id="stockPrice"
              v-model="stockPrice"
              class="form-control"
              step="0.01"
              min="0"
              placeholder="e.g., 150.25"
            />
            <small class="input-hint">Needed for P/E, P/B, P/S ratio calculations.</small>
          </div>

          <div class="form-group">
            <label class="form-label">AI Model for Extraction:</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="apiChoice" value="gemini" />
                <span>Gemini (Recommended)</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="apiChoice" value="openrouter" />
                <span>OpenRouter</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label for="analysisDetail" class="form-label">Analysis Detail Level:</label>
            <select id="analysisDetail" v-model="analysisDetail" class="form-control">
              <option value="standard">Standard (Key ratios & recommendation)</option>
              <option value="detailed">Detailed (Includes MD&A, risks, SWOT, etc.)</option>
            </select>
          </div>

          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="includeMda" />
              <span>Include MD&A / Risk Factors Summary</span>
            </label>
            <small class="input-hint">Overrides detail level for this specific section.</small>
          </div>
          
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="includeLlmAnalysis" checked />
              <span>Include Advanced AI Analysis</span>
            </label>
            <small class="input-hint">Uses AI to interpret ratios, predict earnings, and generate narratives.</small>
          </div>
        </fieldset>

        <button type="submit" class="btn btn-primary btn-analyze" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else>Analyze Report</span>
        </button>
      </form>
    </div>

    <div class="card info-card">
      <h2 class="card-title">How It Works</h2>
      <div class="process-steps">
        <div class="step">
          <div class="step-icon">📤</div>
          <div class="step-info">
            <h3>1. Upload PDF</h3>
            <p>Submit a company's 10-K report.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-icon">🤖</div>
          <div class="step-info">
            <h3>2. AI Extraction</h3>
            <p>AI extracts key financial data.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-icon">📊</div>
          <div class="step-info">
            <h3>3. Analysis</h3>
            <p>Ratios calculated & scored.</p>
          </div>
        </div>
        <div class="step">
          <div class="step-icon">💡</div>
          <div class="step-info">
            <h3>4. Insights</h3>
            <p>Get recommendations & narratives.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Home',
  data() {
    return {
      file: null,
      stockPrice: '',
      apiChoice: 'gemini',
      analysisDetail: 'standard',
      includeMda: false,
      includeLlmAnalysis: true,
      isLoading: false,
      error: null,
      disclaimer: null,
      showFullDisclaimer: false
    }
  },
  methods: {
    handleFileChange(e) {
      this.file = e.target.files[0];
      this.error = null;
    },
    async uploadFile() {
      if (!this.file) {
        this.error = 'Please select a PDF file to upload.';
        return;
      }

      this.isLoading = true;
      this.error = null;

      try {
        const formData = new FormData();
        formData.append('file', this.file);

        if (this.stockPrice) {
          formData.append('stock_price', this.stockPrice);
        }

        formData.append('api_choice', this.apiChoice);
        formData.append('analysis_detail', this.analysisDetail);
        formData.append('include_mda', this.includeMda ? 'true' : 'false');
        formData.append('include_llm_analysis', this.includeLlmAnalysis ? 'true' : 'false');

        const response = await axios.post('http://localhost:5000/api/analyze', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        localStorage.setItem('analysisResults', JSON.stringify(response.data));
        this.$router.push({ name: 'Results', params: { id: Date.now() } });
      } catch (err) {
        console.error('Error uploading file:', err);
        this.error = err.response?.data?.error || 'Error processing file. Please try again.';
      } finally {
        this.isLoading = false;
      }
    },
    async fetchDisclaimer() {
      try {
        const response = await axios.get('http://localhost:5000/api/disclaimer');
        this.disclaimer = response.data;
      } catch (err) {
        console.error('Error fetching disclaimer:', err);
      }
    }
  },
  mounted() {
    this.fetchDisclaimer();
  }
}
</script>

<style scoped>
.home {
  /* Styles for the main home container can be minimal as global styles handle the page structure */
}

.subtitle {
  margin-bottom: 1.5rem;
  font-size: 1rem;
  color: #333; /* Slightly softer for subtitle */
}

.ai-disclaimer {
  margin: 1rem 0;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.ai-disclaimer p {
  margin: 0 0 0.5rem 0;
}

.limitations-list {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.btn-link {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0;
  text-decoration: underline;
}

.btn-link:hover {
  color: #0056b3;
}

.upload-card {
  /* Specific styles for the upload card if needed, beyond global .card */
}

.info-card {
  margin-top: 3rem; /* More separation for the info card */
}

.form-section {
  border: 2px solid #000000;
  padding: 1.5rem;
  margin-bottom: 2rem;
  position: relative; /* For legend positioning */
}

.section-title {
  font-size: 1.2rem;
  font-weight: bold;
  text-transform: uppercase;
  background-color: #FFFFFF; /* Match card background */
  color: #000000;
  padding: 0.25rem 0.75rem;
  position: absolute;
  top: -0.8em; /* Position legend on top of the border */
  left: 1rem;
  border: 2px solid #000000;
}

.file-input {
  /* Can add specific styling for file input if needed */
  /* For Neo Brutalism, the default browser styling with .form-control is often fine */
}

.input-hint {
  display: block;
  font-size: 0.85rem;
  color: #555;
  margin-top: 0.3rem;
}

.radio-group, .checkbox-group {
  display: flex;
  flex-direction: column; /* Stack options vertically for clarity */
  gap: 0.5rem;
}

.radio-label, .checkbox-label {
  display: flex;
  align-items: center;
  font-size: 1rem;
  cursor: pointer;
}

.radio-label span, .checkbox-label span {
  margin-left: 0.5rem;
}

.btn-analyze {
  width: 100%;
  padding: 1rem;
  font-size: 1.2rem;
}

.loading-spinner {
  /* Using global .loading style from App.vue */
  display: inline-block;
  width: 24px; /* Adjust size as needed */
  height: 24px;
  border-width: 3px; /* Adjust border as needed */
  /* Colors are inherited from global .loading */
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); /* Responsive grid */
  gap: 1.5rem;
}

.step {
  display: flex;
  flex-direction: column; /* Stack icon and text vertically */
  align-items: center; /* Center items */
  text-align: center;
  padding: 1rem;
  border: 2px solid #000000;
  background-color: #FFFDE7; /* Light yellow background for steps */
}

.step-icon {
  font-size: 2.5rem; /* Larger icons */
  margin-bottom: 0.75rem;
  line-height: 1;
}

.step-info h3 {
  font-size: 1.1rem;
  font-weight: bold;
  margin-bottom: 0.3rem;
  color: #000000;
  text-transform: uppercase;
}

.step-info p {
  font-size: 0.9rem;
  color: #333;
}
</style>
