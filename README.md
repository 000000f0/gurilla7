# Gorilla7 - Intelligent Lead Generation System

## Project Overview
An intelligent system for automated lead generation and outreach, featuring industry data collection, target company identification, and automated communication.

## Current Phase: 2B
- ✅ Phase 1: Client Onboarding (Completed)
- ✅ Phase 2A: Industry Data Collection (Completed)
- 🚧 Phase 2B: Target Company Identification (In Progress)

## Features
- **Client Management**
  - Per-client database isolation
  - Campaign parameter customization
  - Progress tracking

- **Industry Data Collection**
  - Advanced web scraping with anti-detection
  - Dynamic content support
  - Metadata extraction (title, tags, timestamps)
  - Tag-based content organization

- **Database Structure**
  - `clients`: Configuration and onboarding
  - `industry_data`: Scraped industry insights
  - `lead_bucket`: Potential target companies
  - `tailored_solutions`: Generated solution dossiers
  - `outreach_log`: Communication tracking

## Project Structure
```
/gorilla7
├── database/
│   ├── db_manager.py      # Database operations
│   └── test_db.py         # Database tests
├── src/
│   ├── config/
│   │   └── settings.py    # Configuration
│   ├── onboarding/        # Client onboarding
│   └── scraping/
│       ├── industry/      # Industry data collection
│       └── company/       # Company targeting
└── requirements.txt
```

## Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

4. Create `.env` file with required environment variables:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   OPENAI_API_KEY=your_openai_key
   ```

## Running Tests
```bash
python -m unittest tests/test_industry_crawler.py -v
```

## Security Notes
- Never commit `.env` files or API tokens
- Use environment variables for sensitive data
- Database files are automatically excluded via .gitignore

## Contributing
1. Create a feature branch
2. Make your changes
3. Run the test suite
4. Submit a pull request

## License
This project is proprietary and confidential.
