# Local SEO Intelligence OS — Cloud-ready MVP

A simple, professional Streamlit dashboard inspired by common SEO and AI visibility platforms. It includes a client dashboard and printable PDF report builder.

## What works now
- Clean dashboard and client register
- Basic public-page HTML SEO audit
- Keyword records and CSV import/export
- Google Business Profile checklist
- Competitor register
- AI visibility evidence log
- Client PDF report generation for printing/emailing
- Sample client rows, clearly labeled as sample data

## Important limitations
This package is ready to deploy, but **it is not already hosted on a public URL**. A public cloud URL must be created through a hosting account (for example, Streamlit Community Cloud) and connected to a GitHub repository. This chat cannot create or operate that external hosting account for you.

Not connected yet:
- Live Google Maps/geogrid rank tracking
- Google Business Profile API sync
- Google Search Console OAuth (CSV import is available)
- Live keyword volumes/rank-tracking/backlink database
- Automated AI engine prompt monitoring
- Production login, client-specific permissions, persistent database, billing, scheduled jobs

Do not treat sample rows as live measurements. Client and app state is session-based and may reset. Do not use for confidential client data until authentication, database storage and tenant separation are implemented.

## Deploy to a public URL
1. Download and extract this ZIP.
2. Create a GitHub repository and upload `app.py`, `requirements.txt`, `.streamlit/config.toml`, and `README.md`.
3. In Streamlit Community Cloud, create a new app and select that repository, branch, and `app.py`.
4. Deploy. Streamlit will provide a public URL that can be opened from anywhere with an internet connection.

The hosting provider may change its policies, account requirements, availability, and limits. Keep the repository private if appropriate and review hosting/privacy settings before adding client information.

## Run locally on macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Suggested architecture for production
- UI/API: Streamlit MVP, later migrate to a full web app if needed
- Persistent database: PostgreSQL
- Auth: secure login, role-based access and tenant isolation
- Integrations: Google Search Console API, authorized GBP API access, authorized rank-data provider, controlled AI visibility measurement
- Reports: current ReportLab PDF builder
- Deployment: managed cloud hosting with HTTPS, secrets, backups, monitoring and privacy controls

## Data integrity
Every metric should preserve source, timestamp, query, location and measurement method. Never call a rank or AI mention "live" unless it came from a connected provider or verified source.
