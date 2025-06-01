# Advanced Business Intelligence Dashboard: A Portfolio Showcase
## Integrating Data Analysis (SQL & Python), AI-Powered Insights (Gemini), Local NLP (VADER), Web-Sourced Commodity Data, and Power BI Storytelling

This portfolio project demonstrates a comprehensive, end-to-end business intelligence solution, showcasing a sophisticated blend of technical skills. It features an interactive **Microsoft Power BI** dashboard built upon a foundation of robust data practices, including:

*   **Data Generation & Management:** Utilizing **Python** for the creation of complex, relational mock datasets that emulate real-world business scenarios (marketing, user interactions, supplier information). This simulates a data pipeline where data could originate from various sources, potentially managed and queried using **SQL** in a real-world database environment.
*   **Advanced AI Integration (Google Gemini API):** Leveraging the power of Large Language Models (LLMs) for:
    *   **Complex Text Analysis:** Parsing and understanding unstructured text from simulated Request for Quotations (RFQs) and supplier capability descriptions.
    *   **Autonomous Insight Generation:** Synthesizing aggregated data to autonomously identify strategic business insights.
    *   **Automated Task Assignment:** Deriving and prioritizing actionable tasks directly from the AI-generated insights, demonstrating a closed-loop analytical system.
*   **Local NLP & Machine Learning Techniques (VADER):** Employing the **VADER (Valence Aware Dictionary and sEntiment Reasoner)** library, a lexicon and rule-based sentiment analysis tool attuned to expressions in social media and general text, to perform efficient, local sentiment scoring on user feedback without relying on external APIs for this specific task.
*   **Near Real-Time Data Acquisition (Web Scraping Context):** Incorporating commodity price data (e.g., steel, aluminum, oil) sourced from public web data (via `yfinance` library, simulating a web scraping or API data feed). This adds a layer of external market context to the internal business data, enabling analysis of potential correlations and impacts.
*   **Data Storytelling & Dashboard Design (Power BI):** Culminating in a meticulously designed Power BI dashboard that not only visualizes data but also tells a compelling story, guiding the user through key performance indicators, user funnels, sentiment trends, and market-driven insights. Emphasis is placed on clear communication, intuitive navigation, and actionable visual outputs.

**Disclaimer:** The data presented is entirely **mock data**, programmatically generated for demonstration and skill-showcasing purposes. It does **not** represent real data, operational metrics, or performance of Thomasnet (A Xometry Company). The company logo is used for illustrative context only. This project serves as a preview of technical skills in integrating Power BI with advanced AI models like Gemini for enhanced data storytelling.
---

## Table of Contents
1.  [Project Overview](#1-project-overview)
2.  [Key Skills Demonstrated](#2-key-skills-demonstrated)
3.  [Technical Stack](#3-technical-stack)
4.  [Dashboard Showcase & Features](#4-dashboard-showcase--features)
    *   [4.1 Home / Overview Page](#41-home--overview-page)
    *   [4.2 User Funnel Page](#42-user-funnel-page)
    *   [4.3 User Feedback Page](#43-user-feedback-page)
    *   [4.4 Supplier Info / Commodities Page](#44-supplier-info--commodities-page)
5.  [Project Structure](#5-project-structure)
6.  [Setup & Usage](#6-setup--usage)
7.  [AI-Powered Insights Examples](#7-ai-powered-insights-examples)
8.  [Contact](#8-contact)

---

## 1. Project Overview
This project simulates a business intelligence solution for a B2B platform, providing insights into marketing effectiveness, user behavior, and overall platform health. It highlights the ability to:
*   Generate and manage complex relational datasets.
*   Perform NLP tasks like sentiment analysis locally using Python libraries.
*   Integrate with powerful Large Language Models (LLMs) like Google Gemini for deeper contextual understanding and insight generation.
*   Present complex data in an intuitive, interactive, and actionable Power BI dashboard.

## 2. Key Skills Demonstrated
*   **Data Pipeline & ETL:** Python scripting for mock data generation; data cleaning and transformation.
*   **AI/NLP Integration:**
    *   Sentiment Analysis: Using the VADER library for English text.
    *   Advanced Text Analysis (via Gemini): RFQ categorization, supplier capability summarization, strategic insight generation, actionable task suggestion.
    *   Prompt Engineering for LLMs.
    *   JSON parsing from API/model outputs.
*   **Business Intelligence & Data Visualization (Power BI):**
    *   Interactive dashboard development with multiple pages and drill-down capabilities.
    *   DAX for creating measures and calculated columns.
    *   Power Query for data ingestion and transformation.
    *   Data modeling and relationship management.
*   **Python for Data Science:** `pandas`, `nltk`, `vaderSentiment`, (optional) `google-generativeai`.
*   **Version Control:** Git & GitHub.

## 3. Technical Stack
*   **Dashboarding:** Microsoft Power BI Desktop
*   **Sentiment Analysis (Local):** Python (VADER library)
*   **Advanced AI (Optional):** Google Gemini API (e.g., `gemini-1.5-flash-latest` or `gemma` series)
*   **Data Generation & API Interaction:** Python 3.x
*   **Version Control:** Git, GitHub

---

## 4. Dashboard Showcase & Features

The Power BI dashboard is organized into several pages, each focusing on a different aspect of the business:

### 4.1 Home / Overview Page
![Overview Page](https://i.imgur.com/0ZZKWbI.png)
*   **Objective:** Provide a high-level summary of key performance indicators (KPIs) and strategic insights.
*   **Key Visuals & Functions:**
    *   **Date Slicer & Filters:** Allows users to select time periods (Last N months, custom range) and filter by Campaign ID, Campaign Name, Segment, Conversion, Insight ID, and Task ID. Technologies: Power BI Slicers.
    *   **KPI Cards:**
        *   **Leads:** Total number of leads generated.
        *   **Campaign Spend:** Total marketing expenditure.
        *   **CPL (Cost Per Lead):** Average cost to acquire a lead.
        *   **ROAS (Return on Ad Spend):** Measures a campaign's revenue generation efficiency.
        *   **Distinct Users:** Total unique users interacting with the platform.
        *   **Conv. Rate:** Overall conversion rate.
        *   Technologies: Power BI Cards, DAX Measures.
    *   **ROI by Campaign (Bar Chart):** Displays the Return on Investment for the top N campaigns, allowing quick identification of high and low performers. Technologies: Power BI Bar Chart.
    *   **User Sentiment Overview (Pie Chart):** Shows the distribution of user feedback sentiment (Positive, Neutral, Negative) based on VADER analysis. Technologies: Power BI Pie Chart, VADER Sentiment data.
    *   **Strategic Insights Table:** Lists AI-generated strategic insights from Gemini with `Insight ID`, `Insight Title`, and `Explanation`. Technologies: Power BI Table, AI-generated text.
    *   **Actionable Tasks Table:** Lists AI-generated actionable tasks with `Task ID`, `Description`, and `Severity` (importance). Technologies: Power BI Table, AI-generated text, Conditional Formatting for severity.
    *   **Leads vs CPL (Line and Clustered Column Chart):** Tracks the trend of Leads generated and CPL over time (e.g., monthly). Technologies: Power BI Combo Chart.
    *   **Conversion by Channel (Bar Chart):** Compares conversion performance across different marketing channels. Technologies: Power BI Bar Chart.

### 4.2 User Funnel Page
![User Funnel Page](https://i.imgur.com/fTWdjin.png)
*   **Objective:** Visualize the user journey through key engagement and conversion steps, and understand user demographics and acquisition channels.
*   **Key Visuals & Functions:**
    *   **Date Slicer & Filters:** Similar to the Overview page, allowing filtering by Campaign, Objective, etc.
    *   **Requests for Quotation Funnel (Funnel Chart):** Displays the drop-off rates at each stage of the RFQ submission process: Site Visits -> Content Views -> Searches -> RFQs Submitted. Technologies: Power BI Funnel Chart.
    *   **New Users by FT (First Touch) Channel (Stacked Bar Chart):** Shows the number of new users acquired through different first-touch marketing channels, broken down quarterly. Technologies: Power BI Stacked Bar Chart.
    *   **Access by Device (Pie Chart):** Illustrates the distribution of user access by device type (Smartphones, Tablets, PCs). Technologies: Power BI Pie Chart.
    *   **Interaction Details (Table):** Provides a detailed log of user interactions, including `Session ID`, `User ID`, `Interaction ID`, and `Page URL`. Useful for drill-down analysis. Technologies: Power BI Table.
    *   **Leads by Country (Map Visual):** Displays the geographic distribution of leads. Technologies: Power BI Map Visual.

### 4.3 User Feedback Page
![User Feedback Page](https://i.imgur.com/snadLjY.png)
*   **Objective:** Analyze user sentiment in detail, linking it to campaigns and user types.
*   **Key Visuals & Functions:**
    *   **Date Slicer & Filters:** Filter by Campaign and a dedicated "Sentiment" slicer (Negative, Neutral, Positive).
    *   **KPI Cards (Feedback Specific):**
        *   **Total Campaigns, Users, User Feedback:** Counts of relevant entities.
        *   **Positive, Neutral, Negative Feedback Counts:** Quantifies feedback by sentiment category.
        *   Technologies: Power BI Cards, DAX Measures based on VADER sentiment labels.
    *   **Sentiment by Quarter (100% Stacked Bar Chart):** Shows the trend of sentiment distribution (Positive, Neutral, Negative) across different quarters. Technologies: Power BI 100% Stacked Bar Chart.
    *   **Sentiment by Campaign (Stacked Bar Chart):** Displays the sentiment breakdown for individual campaigns, helping to identify campaigns associated with particularly positive or negative feedback. Technologies: Power BI Stacked Bar Chart.
    *   **Details by Campaign and User (Table):** A detailed table showing `User ID`, `User Type`, `User Role`, the VADER-derived `Sentiment` label, sentiment scores (`Positive`, `Neutral`, `Negative` components from VADER), and the original `Feedback` text. Icons and conditional formatting highlight the sentiment. Technologies: Power BI Table, VADER sentiment data, Conditional Formatting.

### 4.4 Supplier Info / Commodities Page
![Supplier Info / Commodities Page](https://i.imgur.com/pcu0Ous.png)
*   **Objective:** Provide information related to suppliers and contextualize market conditions by displaying commodity price trends.
*   **Key Visuals & Functions:**
    *   **Date Slicer & Filters:** Filter by Commodity type and "Supplier Category".
    *   **Commodity Price Trends (Line Chart):** Displays the historical price trends for selected commodities (e.g., Aluminum, Copper, Crude Oil, Steel ETFs). Multiple commodities can be overlaid for comparison. Technologies: Power BI Line Chart, `yfinance` data.
    *   **Commodity Price Cards (KPI Cards with Icons):** Shows the latest price for key commodities, each with a relevant icon. Technologies: Power BI Cards.
    *   *(Potential Future Visuals for "Supplier Info" not shown but implied by page name):*
        *   Table of suppliers with their AI-analyzed capabilities (`gemini_supplier_capability_json`).
        *   Map of supplier locations.
        *   Charts showing distribution of suppliers by capability category.

---

## 5. Project Structure

```
ThomasnetProject/
├── .env.example # Example environment file
├── .gitignore # Specifies intentionally untracked files
├── README.md # This file
├── generate_mock_data_en.py # Script to generate mock CSV data in English
├── enrich_data_nlp_en.py # Script for NLP (VADER/Gemini) and insights/tasks
├── list_gemini_models.py # Utility to list available Gemini models
├── download_commodity_data.py # Script to download commodity prices
├── campaign_details_en.csv # Generated mock campaign data
├── user_details_enriched_en.csv # Enriched user data
├── marketing_interactions_enriched_en.csv # Enriched interaction data
├── commodity_prices_en.csv # Downloaded commodity price data
├── strategic_insights_mock_en.csv # Mocked strategic insights
├── actionable_tasks_mock_en.csv # Mocked actionable tasks
└── screenshots/ # Folder for dashboard images
├── overview_dashboard.png
├── user_funnel_dashboard.png
├── user_feedback_dashboard.png
└── supplier_commodities_dashboard.png
```

## 6. Setup & Usage
### Prerequisites
*   Python 3.8+
*   Microsoft Power BI Desktop
*   Git
*   (Optional) Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/) if using Gemini features.

### Local Setup
1.  **Clone:** `git clone https://github.com/https://github.com/lmoraes9/powerbi-gemini-portfolio.git`
2.  **Navigate:** `cd powerbi-gemini-portfolio`
3.  **Install dependencies:** `pip install pandas faker vaderSentiment nltk yfinance python-dotenv google-generativeai`
4.  **API Key (if using Gemini):** Rename `.env.example` to `.env` and add your `GOOGLE_API_KEY`.
5.  **Run Data Generation:** `python generate_mock_data_en.py`
6.  **Run Commodity Data Download:** `python download_commodity_data.py`
7.  **Run NLP Enrichment & Insight Generation:** `python enrich_data_nlp_en.py`
    *   (Set `USE_GEMINI_FOR_ADVANCED_ANALYSIS = True/False` inside the script as needed).
8.  **Power BI:** Open Power BI Desktop, connect to the generated `*_en.csv` and `*_enriched_en.csv` files. Apply necessary transformations (like JSON parsing) in Power Query and build/refresh the dashboard.

## 7. AI-Powered Insights Examples
*   **VADER Sentiment:** User feedback text is processed locally by VADER to determine if it's Positive, Negative, or Neutral, along with a compound sentiment score.
*   **(Gemini) RFQ Analysis:** Parses RFQ text to identify service/product type, implied urgency, and key specifications.
*   **(Gemini) Supplier Capabilities:** Summarizes supplier capability descriptions and extracts main service categories.
*   **(Gemini) Strategic Insights & Tasks:** Synthesizes aggregated data to suggest strategic insights and actionable tasks with priority levels.

## 8. Contact

Leonardo Moraes - (https://www.linkedin.com/in/moraesleo/)

---
