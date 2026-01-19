# Force Multiply CRM Intelligence Report Generator

Python automation that extracts CRM data from Salesforce, enriches it with Claude AI analysis, and generates a professional PDF report.

## Overview

This tool provides:
- **Salesforce Data Extraction**: Pulls Accounts, Contacts, Opportunities, Projects, and Contractor Engagements
- **AI-Powered Analysis**: Uses Claude to generate executive summaries, pipeline analysis, client insights, staffing overviews, and margin analysis
- **Professional PDF Output**: Creates a formatted report with data tables and strategic recommendations

## Quick Start

### 1. Install Dependencies

```bash
cd scripts/python
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash
# Option A: Use SF CLI (recommended if already authenticated)
SF_USE_CLI_SESSION=true
SF_CLI_TARGET_ORG=FMCDev

# Option B: Use username/password
SF_USERNAME=your_username@example.com
SF_PASSWORD=your_password
SF_SECURITY_TOKEN=your_security_token
SF_DOMAIN=login  # or 'test' for sandbox

# Claude API (required for AI enrichment)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Output
OUTPUT_DIR=./output
REPORT_FILENAME=crm_summary_report.pdf
```

### 3. Run the Report Generator

Using SF CLI session (recommended):
```bash
python generate_crm_report.py --cli --org FMCDev
```

Using username/password:
```bash
python generate_crm_report.py
```

Skip AI enrichment (faster, no API costs):
```bash
python generate_crm_report.py --cli --skip-ai
```

Custom output path:
```bash
python generate_crm_report.py --cli --output ./reports/weekly_report.pdf
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--cli` | Use SF CLI session instead of username/password |
| `--org ORG_ALIAS` | SF CLI org alias (default: FMCDev) |
| `--output PATH` | Custom output path for the PDF |
| `--skip-ai` | Skip AI enrichment, generate with raw data only |
| `--verbose`, `-v` | Enable verbose logging |

## Architecture

```
generate_crm_report.py    # Main orchestrator script
    |
    +-- config.py             # Configuration management
    +-- salesforce_client.py  # Salesforce data extraction
    +-- claude_enrichment.py  # Claude AI analysis
    +-- pdf_generator.py      # ReportLab PDF generation
```

### Data Flow

1. **Extract**: Connect to Salesforce and query all relevant objects
2. **Transform**: Convert Salesforce records to typed Python dataclasses
3. **Enrich**: Send structured data to Claude for intelligent analysis
4. **Generate**: Create professional PDF with ReportLab

## Salesforce Objects Used

| Object | Purpose |
|--------|---------|
| Account | Client companies and contractor firms |
| Contact | Client contacts and contractors |
| Opportunity | Revenue pipeline and deals |
| Project__c | Delivery projects |
| Contractor_Engagement__c | Contractor staffing assignments |

## Report Sections

The generated PDF includes:

1. **Title Page**: Key metrics summary
2. **Executive Summary**: High-level business health assessment
3. **Pipeline Analysis**: Sales opportunity insights
4. **Client Insights**: Relationship health and coverage
5. **Staffing Overview**: Contractor utilization and capacity
6. **Margin Analysis**: Rate and profitability assessment
7. **Strategic Recommendations**: Prioritized action items
8. **Data Appendix**: Summary tables of key records

## Authentication Options

### SF CLI Session (Recommended)

If you're already authenticated via SF CLI:

```bash
# Authenticate if needed
sf org login web -a FMCDev

# Run report
python generate_crm_report.py --cli --org FMCDev
```

### Username/Password

Set environment variables:
- `SF_USERNAME`: Your Salesforce username
- `SF_PASSWORD`: Your password
- `SF_SECURITY_TOKEN`: Your security token (from Salesforce settings)
- `SF_DOMAIN`: `login` for production, `test` for sandbox

## Customization

### Adding New Data Sources

Edit `salesforce_client.py` to add new SOQL queries and dataclasses.

### Modifying AI Prompts

Edit `claude_enrichment.py` to customize the prompts sent to Claude for each report section.

### Changing PDF Layout

Edit `pdf_generator.py` to modify styles, colors, and layout of the generated PDF.

## Troubleshooting

### "SF CLI command failed"
Make sure you're authenticated: `sf org login web -a FMCDev`

### "ANTHROPIC_API_KEY environment variable is required"
Add your Claude API key to the `.env` file or use `--skip-ai` flag.

### "Query failed: invalid field"
Check that all custom fields exist in your Salesforce org. Some fields may need to be created or the queries adjusted.

## Cost Considerations

- **Salesforce API**: Uses standard REST API with query_all for pagination
- **Claude API**: Approximately 6 API calls per report (one per section)
- **Estimated cost**: ~$0.10-0.50 per report depending on data volume

## Requirements

- Python 3.10+
- Salesforce org with API access
- Anthropic API key (for AI enrichment)
- SF CLI (if using CLI authentication)
