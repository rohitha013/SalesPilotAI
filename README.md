# 🚀 SalesPilot AI

### AI-Powered Sales Pipeline Assistant

SalesPilot AI is an intelligent sales management prototype that combines customer enquiry management, CRM tracking, and AI-assisted email drafting into one interactive platform.

## Problem Statement
Businesses receive numerous customer enquiries and often struggle to manage leads, prioritize opportunities, and respond efficiently.

## Our Solution
SalesPilot AI simplifies sales workflows by organizing customer enquiries and using Google's Gemini AI to assist with personalized sales communication.

## Key Features
- **Sales Inbox:** View and manage sample customer enquiries.
- **AI Email Generation:** Generate personalized email drafts using Gemini AI.
- **CRM Dashboard:** Track lead status, priorities, scores, and estimated pipeline value.
- **Reply Studio:** Edit and improve email drafts using natural-language instructions.
- **CSV Export:** Export lead data for further analysis.
- **Fallback System:** Create basic reply drafts when Gemini is unavailable.

## Technology Stack
- Python
- Streamlit
- Pandas
- Google Gemini API

## How to Run

1. Install dependencies:

   `pip install -r requirements.txt`

2. Set the `GEMINI_API_KEY` environment variable with your own API key.

3. Run the application:

   `python -m streamlit run app.py`

4. Open the local URL displayed in the terminal.

## Future Enhancements
- Real email integration
- Automated follow-up reminders
- Persistent database storage
- Predictive lead scoring
- Cloud deployment

## Note
This is a hackathon prototype using fictional customer data. It does not access real email accounts or send emails automatically.
