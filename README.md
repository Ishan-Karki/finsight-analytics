# FinSight-Pro: A Privacy-First Financial Intelligence Dashboard

## Core Vision

FinSight-Pro is a local-only, privacy-first tool designed for users who want deep financial insights without exposing their sensitive transaction data. By keeping all computations and processing local to your machine, FinSight-Pro ensures that your personal financial data is never uploaded to third-party cloud servers or external databases.

## Key Features

* **AI-Powered Data Extraction:** Intelligently parses and categorizes financial data from various formats including CSV, TXT, PDF, and images using Gemini AI.
* **SQLite Persistence:** Maintains a seamless local history of your transactions using an embedded SQLite database for quick access and tracking.
* **Interactive Plotly Visualizations:** Discover trends effortlessly with high-fidelity, market-style interactive charts, including smoothed gradient area charts and categorization donuts.
* **Modular UI:** A modern and highly responsive user interface built with specialized Streamlit components.

## Privacy Architecture

FinSight-Pro was built from the ground up prioritizing security and privacy:

* **No External Database Connections:** All data is persisted exclusively via local SQLite files or maintained in-memory.
* **`.gitignore` Protection:** Personal files, raw transaction data, database instances, and environment variables are strictly ignored from commits out-of-the-box.
* **In-Memory Processing:** Sensitive documents are processed entirely in-memory upon upload during active sessions, preserving your data footprint.

## Tech Stack

* **Python**
* **Streamlit**
* **Pandas**
* **Plotly**
* **SQLite**
* **Gemini AI**

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ishan-Karki/finsight-analytics.git
   cd finsight-analytics
   ```

2. **Install requirements:**
   Make sure you have Python installed, then install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the environment:**
   Create a `.env` file in the project's root directory and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the Dashboard:**
   Launch the Streamlit application:
   ```bash
   streamlit run FinSight-Pro/app.py
   ```

## Future Roadmap

* **Multi-currency support:** Handle global transactions with real-time conversion rates.
* **Advanced PDF parsing:** Enhanced tabular data extraction from complex banking statement structures.
* **Budgeting alerts:** Proactive notifications and threshold tracking to keep spending habits in check.
