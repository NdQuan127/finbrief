# 10-K Financial Analysis Frontend

This is the Vue.js frontend for the 10-K Financial Analysis application. It provides a user-friendly interface to upload 10-K PDF files, analyze financial data, and view investment recommendations.

## Setup Instructions

1. Install dependencies:
   ```
   npm install
   ```

2. Run the development server:
   ```
   npm run serve
   ```

3. Build for production:
   ```
   npm run build
   ```

## Features

- **File Upload**: Upload 10-K PDF files for analysis
- **Data Visualization**: View extracted financial data and calculated ratios
- **Investment Recommendations**: Get Buy/Hold/Sell recommendations with explanations

## Backend Connection

The frontend connects to the Flask backend API running on `http://localhost:5000`. Make sure the backend server is running before using the application.

## Technologies Used

- Vue 3
- Vue Router
- Axios for API requests
- Modern CSS with Grid and Flexbox layouts
