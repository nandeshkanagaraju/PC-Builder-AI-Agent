# PC Builder AI Agent

Your Intelligent Conversational Assistant for Personalized PC Builds.

## Project Description

Navigating the complex world of PC components, ensuring compatibility, staying within budget, and tracking fluctuating prices can be a daunting task for anyone, from first-time builders to seasoned enthusiasts. The **PC Builder AI Agent** aims to revolutionize this experience by providing a highly personalized, intelligent, and proactive conversational assistant that simplifies the entire PC building process.

This project goes beyond traditional static configurators by understanding your unique requirements through natural language, recommending optimal builds, and continuously monitoring prices to ensure you get the best deal.

## Problem Solved

*   **Complexity & Compatibility:** Overwhelming number of components and intricate compatibility rules (CPU sockets, RAM types, PSU wattage, case sizes, etc.).
*   **Budget Optimization:** Difficulty in finding the best performance/value within a strict budget, often leading to overspending or under-speccing.
*   **Price Volatility:** PC component prices fluctuate constantly, making it hard to buy at the right time.
*   **Lack of Personalization:** Existing tools often offer generic builds or require extensive manual input without truly understanding the user's nuanced needs (e.g., aesthetic preferences).
*   **Post-Recommendation Value:** Current platforms typically end their utility after the initial recommendation.

## Key Features (MVP Focused, with Future Vision)

*   **Intelligent Requirement Gathering:** Utilizes advanced Natural Language Understanding (NLU) powered by OpenAI GPT to converse with users, asking clarifying questions to extract detailed preferences like:
    *   **Budget:** Exact or approximate spending limit.
    *   **Primary Use Case:** Gaming (specific titles/genres), professional work (video editing, CAD, programming), streaming, general productivity, etc.
    *   **Aesthetic Preferences:** RGB lighting, minimalist design, specific color schemes (e.g., white build).
    *   **Peripherals:** Inclusion of monitors, keyboards, mice, headphones, etc., with specific requirements (e.g., monitor resolution/refresh rate).
*   **Personalized Build Recommendations:** Generates optimized PC builds that balance performance, aesthetics, and strict budget adherence. Recommendations cover all core components (CPU, GPU, Motherboard, RAM, Storage, PSU, Case) and specified peripherals.
*   **Best Under Budget & Alternatives:** Focuses on delivering the best possible outcome within the user's budget. The recommendation engine can also be extended to suggest components that offer a near-perfect outcome at a reduced cost, or slight upgrades for a minimal budget increase.
*   **Live Price Tracking & Comparison:** Continuously monitors real-time prices for recommended components across multiple trusted online retailers. It identifies the lowest available price for each part.
*   **Website Trustability Indicator:** Provides a basic indication of retailer trust, helping users make informed purchasing decisions.
*   **Proactive Price Drop Notifications:** Users can opt-in to provide their name and email to receive automatic email alerts if any component in their recommended build drops below its initial quoted price (or a significant threshold).
*   **Superior User Experience:** Aims to surpass existing platforms by offering a truly conversational, personalized, and proactive approach to PC building.

---

## Technical Stack

The project is built primarily with Python, leveraging a robust set of libraries and tools:

*   **Backend Framework:** `Flask` (for building the RESTful API)
*   **Natural Language Understanding (NLU) & Dialogue:** `OpenAI GPT` (for conversational intelligence, intent recognition, entity extraction, and response generation)
*   **Database ORM:** `SQLAlchemy` (for object-relational mapping)
*   **Database:** `MySQL` (for storing product data, prices, user information, and saved builds)
*   **Web Scraping:** `BeautifulSoup4` and `Requests` (for fetching and parsing live price data from e-commerce sites)
*   **Environment Management:** `python-dotenv` (for secure configuration)
*   **Email Notifications:** `smtplib` (Python's built-in SMTP client, potentially combined with a service like Mailgun/SendGrid in production)
*   **Task Scheduling:** System `cron` jobs (for periodic execution of price scraping and notification checks)

## Project Structure

```
pc_agent/
├── app.py                      # Main Flask application and API endpoints
├── config.py                   # Configuration settings and environment variable loading
├── database.py                 # SQLAlchemy engine, session management, and Base definition
├── models.py                   # SQLAlchemy ORM models for all database tables
├── api/
│   ├── chat.py                 # (Conceptual) Chat/NLU related API routes
│   └── builds.py               # (Conceptual) Build management API routes
├── services/
│   ├── nlu_service.py          # Handles OpenAI GPT interactions
│   ├── scraper_service.py      # Contains web scraping logic for price tracking
│   ├── recommendation_service.py # Core logic for generating PC builds
│   └── notification_service.py # Logic for sending price drop emails
├── tasks/
│   └── scheduled_tasks.py      # Script for cron jobs (price updates, notifications)
├── scripts/
│   └── seed_data.py            # (Optional) Script for populating initial product data
├── .env.example                # Example .env file for configuration
├── requirements.txt            # Python dependency list
└── README.md                   # This file
```

## Getting Started

To get this project up and running locally, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/pc_agent.git
    cd pc_agent
    ```

2.  **Set Up Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file in the root directory of the project.
    *   Populate it with your database credentials, OpenAI API key, and email settings. Refer to `.env.example` (or the previous instructions) for required variables.
    ```
    # .env
    DATABASE_URL="mysql+pymysql://your_mysql_user:your_mysql_password@127.0.0.1:3306/your_database_name"
    OPENAI_API_KEY="your_openai_api_key_here"
    EMAIL_HOST="smtp.your_email_provider.com"
    EMAIL_PORT="587"
    EMAIL_USER="your_email@example.com"
    EMAIL_PASSWORD="your_email_password"
    FROM_EMAIL="noreply@youragent.com"
    ```
    **Important:** Ensure your MySQL server is running and the database specified in `DATABASE_URL` (e.g., `your_database_name`) has been created.

5.  **Initialize Database:**
    ```bash
    python database.py
    ```
    This will create all the necessary tables in your MySQL database.

6.  **(Optional) Seed Initial Product Data:**
    You'll need some initial PC component data in your database for recommendations to work. You can manually add this or create a script in `scripts/seed_data.py`.

7.  **Run the Flask Application:**
    ```bash
    python app.py
    ```
    The API will be accessible at `http://127.0.0.1:5000`.

8.  **Set Up Scheduled Tasks (Cron Job):**
    To enable automatic price tracking and notifications, you'll need to set up a cron job for the `tasks/scheduled_tasks.py` script.
    ```bash
    crontab -e
    ```
    Add a line similar to this (adjusting the absolute path to your project and Python interpreter):
    ```
    0 */6 * * * /usr/bin/python3 /absolute/path/to/your/pc_agent/tasks/scheduled_tasks.py >> /var/log/pc_agent_cron.log 2>&1
    ```
    This example runs the task every 6 hours.

## Future Enhancements (Roadmap)

*   **AI-Powered Aesthetic Matching:** Allow users to upload images or describe visual preferences to get style-matched component recommendations.
*   **Interactive 3D Build Visualizer:** A frontend feature to visually assemble and inspect the recommended PC build.
*   **Advanced "Smart Upgrade" Advisor:** Analyze existing PC specs and recommend the most impactful and cost-effective upgrades.
*   **Community & Expert Build Sharing:** Platform for users to share, rate, and discover curated builds.
*   **Enhanced Retailer Trust Scores:** More sophisticated system combining user reviews, historical data, and public sentiment.
*   **Alternative Recommendations:** Offer multiple alternatives for each component (budget, performance, aesthetic) within the build.


---