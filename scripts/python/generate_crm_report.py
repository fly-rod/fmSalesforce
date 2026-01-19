#!/usr/bin/env python3
"""
Force Multiply CRM Intelligence Report Generator

This script extracts CRM data from Salesforce, enriches it with Claude AI analysis,
and generates a professional PDF report.

Usage:
    python generate_crm_report.py [--cli] [--org ORG_ALIAS] [--output PATH]

Arguments:
    --cli           Use SF CLI session instead of username/password auth
    --org           SF CLI org alias (default: FMCDev)
    --output        Output path for the PDF report
    --skip-ai       Skip AI enrichment (generate report with raw data only)
    --verbose       Enable verbose logging

Environment Variables (if not using --cli):
    SF_USERNAME         Salesforce username
    SF_PASSWORD         Salesforce password
    SF_SECURITY_TOKEN   Salesforce security token
    SF_DOMAIN           Salesforce domain (login or test)
    ANTHROPIC_API_KEY   Claude API key

Example:
    # Using SF CLI session
    python generate_crm_report.py --cli --org FMCDev

    # Using username/password
    python generate_crm_report.py

    # Custom output path
    python generate_crm_report.py --cli --output ./reports/weekly_report.pdf
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the script directory to the path for imports
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

from config import AppConfig, ClaudeConfig, OutputConfig, SalesforceConfig
from salesforce_client import CRMData, SalesforceClient
from claude_enrichment import ClaudeEnrichment, EnrichedReport
from pdf_generator import PDFReportGenerator


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AI-enriched CRM intelligence report from Salesforce data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Use SF CLI session for authentication",
    )
    parser.add_argument(
        "--org",
        type=str,
        default="FMCDev",
        help="SF CLI org alias (default: FMCDev)",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for the PDF report",
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI enrichment and generate report with raw data summaries",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def create_placeholder_report(data: CRMData) -> EnrichedReport:
    """Create a placeholder report when AI is skipped."""
    data_dict = data.to_dict()
    summary = data_dict["summary"]

    return EnrichedReport(
        executive_summary=f"""This report provides a summary of Force Multiply CRM data as of {datetime.now().strftime('%B %d, %Y')}.

The system currently tracks {summary['total_accounts']} accounts, {summary['total_contacts']} contacts, {summary['total_opportunities']} opportunities, {summary['total_projects']} projects, and {summary['total_engagements']} contractor engagements.

AI analysis was skipped for this report. Run without --skip-ai flag to generate intelligent insights.""",
        pipeline_analysis="AI analysis skipped. Enable AI enrichment for pipeline insights.",
        client_insights="AI analysis skipped. Enable AI enrichment for client insights.",
        staffing_overview="AI analysis skipped. Enable AI enrichment for staffing analysis.",
        margin_analysis="AI analysis skipped. Enable AI enrichment for margin analysis.",
        recommendations="AI analysis skipped. Enable AI enrichment for strategic recommendations.",
        raw_data=data_dict,
    )


def main() -> int:
    """Main entry point for the report generator."""
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Force Multiply CRM Intelligence Report Generator")
    logger.info("=" * 60)

    try:
        # Configure Salesforce connection
        if args.cli:
            sf_config = SalesforceConfig(
                use_cli_session=True,
                cli_target_org=args.org,
            )
            logger.info(f"Using SF CLI session for org: {args.org}")
        else:
            sf_config = SalesforceConfig.from_env()
            logger.info(f"Using credentials for: {sf_config.username}")

        # Configure output
        output_config = OutputConfig.from_env()
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            output_path = output_config.report_path

        # Step 1: Extract CRM data from Salesforce
        logger.info("-" * 40)
        logger.info("Step 1: Extracting CRM data from Salesforce")
        logger.info("-" * 40)

        sf_client = SalesforceClient(sf_config)
        crm_data = sf_client.extract_all_data()

        logger.info(f"  Accounts: {len(crm_data.accounts)}")
        logger.info(f"  Contacts: {len(crm_data.contacts)}")
        logger.info(f"  Opportunities: {len(crm_data.opportunities)}")
        logger.info(f"  Projects: {len(crm_data.projects)}")
        logger.info(f"  Engagements: {len(crm_data.engagements)}")

        # Step 2: Enrich data with Claude AI
        logger.info("-" * 40)
        logger.info("Step 2: Generating AI-enriched analysis")
        logger.info("-" * 40)

        if args.skip_ai:
            logger.info("AI enrichment skipped (--skip-ai flag)")
            enriched_report = create_placeholder_report(crm_data)
        else:
            try:
                claude_config = ClaudeConfig.from_env()
                enrichment = ClaudeEnrichment(claude_config)
                enriched_report = enrichment.enrich_crm_data(crm_data)
                logger.info("AI analysis complete")
            except ValueError as e:
                logger.warning(f"Claude API not configured: {e}")
                logger.warning("Generating report without AI enrichment")
                enriched_report = create_placeholder_report(crm_data)

        # Step 3: Generate PDF report
        logger.info("-" * 40)
        logger.info("Step 3: Generating PDF report")
        logger.info("-" * 40)

        pdf_generator = PDFReportGenerator(output_config)
        final_path = pdf_generator.generate_report(enriched_report, output_path)

        logger.info("=" * 60)
        logger.info("Report generation complete!")
        logger.info(f"Output: {final_path.absolute()}")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
