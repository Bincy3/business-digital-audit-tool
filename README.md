# Business Digital Audit Tool

A Python CLI tool that reviews a business website for basic digital readiness. It checks SEO, contact information, social presence, technical setup, and conversion signals, then generates both a terminal/TXT summary and a clean visual HTML report.

## Features

- Validates URLs and handles unreachable, invalid, blocked, and HTTP error responses.
- Runs 13 audit checks:
  - Page title
  - Meta description
  - H1 heading
  - Images without alt text
  - Mobile viewport tag
  - HTTPS
  - `sitemap.xml`
  - `robots.txt`
  - Email contact
  - Phone contact
  - Social links
  - Open Graph tags
  - Conversion call-to-action
- Scores the website across five categories:
  - SEO
  - Contact Readiness
  - Social Presence
  - Technical Basics
  - Conversion Readiness
- Generates `sample_report.txt` for quick sharing.
- Generates `sample_report.html` with score cards, checklist results, details, and recommendations.

## Setup

1. Clone the project and open the folder.

```powershell
git clone https://github.com/Bincy3/business-digital-audit-tool.git
cd business-digital-audit-tool
```

2. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

## Usage

Run the app and answer the prompts.

```powershell
python app.py
```

Example input:

```text
Business Name : B Socio
Industry      : Digital Marketing
Website URL   : https://example.com
```

The tool saves the latest reports in the project folder:

- `sample_report.txt`
- `sample_report.html`

Open `sample_report.html` in a browser to view the visual report.

## Output Sample

```text
BUSINESS DIGITAL AUDIT REPORT
============================================================

Business Name : B Socio
Industry      : Digital Marketing
Website       : https://example.com
Status        : Reachable
HTTPS         : Enabled
Audit Score   : 73/100

Category Scores:
- SEO: 23/30
- Contact Readiness: 10/20
- Social Presence: 15/15
- Technical Basics: 25/25
- Conversion Readiness: 0/10

Audit Checks:
- Pass: Page title (Example Domain)
- Needs work: Email contact (Not Found)
- Needs work: Open Graph tags (Missing: og:title, og:description, og:image)
```

The HTML report includes:

- Overall score bar
- Category score cards
- Full audit checklist table
- SEO and contact details
- Prioritized recommendations

## Project Structure

```text
app.py              CLI entry point
audit.py            Audit workflow and scoring checks
utils.py            Website fetching, parsing helpers, and score constants
report.py           TXT and HTML report generation
requirements.txt    Python dependencies
.gitignore          Ignored local and generated files
```

## Notes

- This tool performs a public-page audit only. It does not log in, crawl private areas, or bypass website protections.
- Some websites block automated requests. In that case, the tool returns a clear blocked/error status instead of crashing.
- Results are heuristic and should be used as a starting point for a manual digital audit.
