"""
Claude AI enrichment module for CRM data analysis.

Uses the Anthropic API to generate intelligent summaries and insights.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

import anthropic

from config import ClaudeConfig
from salesforce_client import CRMData

logger = logging.getLogger(__name__)


@dataclass
class EnrichedReport:
    """Container for AI-enriched report content."""
    executive_summary: str
    pipeline_analysis: str
    client_insights: str
    staffing_overview: str
    margin_analysis: str
    recommendations: str
    raw_data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "executive_summary": self.executive_summary,
            "pipeline_analysis": self.pipeline_analysis,
            "client_insights": self.client_insights,
            "staffing_overview": self.staffing_overview,
            "margin_analysis": self.margin_analysis,
            "recommendations": self.recommendations,
        }


class ClaudeEnrichment:
    """Claude AI client for CRM data enrichment."""

    def __init__(self, config: ClaudeConfig):
        """Initialize the Claude client."""
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)

    def enrich_crm_data(self, data: CRMData) -> EnrichedReport:
        """Generate enriched report from CRM data."""
        logger.info("Generating AI-enriched analysis with Claude...")

        data_dict = data.to_dict()

        # Generate each section
        executive_summary = self._generate_executive_summary(data_dict)
        pipeline_analysis = self._generate_pipeline_analysis(data_dict)
        client_insights = self._generate_client_insights(data_dict)
        staffing_overview = self._generate_staffing_overview(data_dict)
        margin_analysis = self._generate_margin_analysis(data_dict)
        recommendations = self._generate_recommendations(data_dict)

        logger.info("AI enrichment complete")

        return EnrichedReport(
            executive_summary=executive_summary,
            pipeline_analysis=pipeline_analysis,
            client_insights=client_insights,
            staffing_overview=staffing_overview,
            margin_analysis=margin_analysis,
            recommendations=recommendations,
            raw_data=data_dict,
        )

    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Make a call to Claude API."""
        try:
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return message.content[0].text
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            return f"[Analysis unavailable due to API error: {e}]"

    def _generate_executive_summary(self, data: dict[str, Any]) -> str:
        """Generate executive summary."""
        system_prompt = """You are a senior business analyst for a Salesforce consulting firm.
Your role is to provide clear, actionable executive summaries of CRM data.
Focus on key metrics, trends, and business-critical insights.
Write in a professional, concise style suitable for managing partners."""

        user_prompt = f"""Analyze this CRM data and provide an executive summary (3-5 paragraphs).

Focus on:
- Overall business health
- Key client relationships
- Revenue pipeline status
- Staffing utilization
- Any concerns or highlights

CRM Data Summary:
- Total Accounts: {data['summary']['total_accounts']}
- Total Contacts: {data['summary']['total_contacts']}
- Total Opportunities: {data['summary']['total_opportunities']}
- Total Projects: {data['summary']['total_projects']}
- Total Contractor Engagements: {data['summary']['total_engagements']}

Accounts:
{json.dumps(data['accounts'][:10], indent=2)}

Opportunities:
{json.dumps(data['opportunities'][:10], indent=2)}

Projects:
{json.dumps(data['projects'][:10], indent=2)}

Engagements:
{json.dumps(data['engagements'][:10], indent=2)}
"""
        return self._call_claude(system_prompt, user_prompt)

    def _generate_pipeline_analysis(self, data: dict[str, Any]) -> str:
        """Generate pipeline analysis."""
        system_prompt = """You are a sales operations analyst for a consulting firm.
Analyze sales pipeline data to identify trends, risks, and opportunities.
Provide specific, data-driven insights."""

        # Calculate pipeline metrics
        opportunities = data["opportunities"]
        total_pipeline = sum(o.get("amount") or 0 for o in opportunities)

        stages = {}
        for opp in opportunities:
            stage = opp.get("stage", "Unknown")
            stages[stage] = stages.get(stage, 0) + (opp.get("amount") or 0)

        user_prompt = f"""Analyze this sales pipeline and provide insights (2-3 paragraphs).

Pipeline Metrics:
- Total Pipeline Value: ${total_pipeline:,.2f}
- Opportunities by Stage: {json.dumps(stages, indent=2)}

All Opportunities:
{json.dumps(opportunities, indent=2)}

Focus on:
- Pipeline health and velocity
- Stage distribution analysis
- Deals requiring attention
- Expected close timeline
"""
        return self._call_claude(system_prompt, user_prompt)

    def _generate_client_insights(self, data: dict[str, Any]) -> str:
        """Generate client relationship insights."""
        system_prompt = """You are a client success manager for a consulting firm.
Analyze client accounts and contacts to identify relationship health and opportunities.
Provide actionable recommendations for relationship management."""

        # Organize data by account
        accounts = data["accounts"]
        contacts = data["contacts"]

        # Group contacts by account
        contacts_by_account = {}
        for contact in contacts:
            acc_name = contact.get("account_name", "No Account")
            if acc_name not in contacts_by_account:
                contacts_by_account[acc_name] = []
            contacts_by_account[acc_name].append(contact)

        user_prompt = f"""Analyze client relationships and provide insights (2-3 paragraphs).

Accounts ({len(accounts)} total):
{json.dumps(accounts[:15], indent=2)}

Contacts by Account:
{json.dumps({k: len(v) for k, v in contacts_by_account.items()}, indent=2)}

Key Contacts:
{json.dumps([c for c in contacts if c.get('contact_role') in ['Decision Maker', 'Client Stakeholder']][:10], indent=2)}

Focus on:
- Client relationship depth
- Key stakeholder coverage
- Contract status (NDA/MSA)
- Relationship risks or gaps
"""
        return self._call_claude(system_prompt, user_prompt)

    def _generate_staffing_overview(self, data: dict[str, Any]) -> str:
        """Generate staffing and contractor overview."""
        system_prompt = """You are a resource manager for a consulting firm that staffs contractors.
Analyze contractor engagements to understand utilization, capacity, and staffing health.
Provide operational insights for managing delivery resources."""

        engagements = data["engagements"]
        contractors = [c for c in data["contacts"] if c.get("contact_role") == "Contractor"]

        # Analyze engagement status
        status_counts = {}
        for eng in engagements:
            status = eng.get("engagement_status", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        user_prompt = f"""Analyze staffing and provide an overview (2-3 paragraphs).

Contractor Pool: {len(contractors)} contractors
Active Engagements: {len(engagements)}

Engagement Status Distribution:
{json.dumps(status_counts, indent=2)}

Current Engagements:
{json.dumps(engagements[:15], indent=2)}

Available Contractors:
{json.dumps([c for c in contractors if c.get('contractor_status') == 'Available'][:10], indent=2)}

Focus on:
- Current utilization rates
- Contractor availability
- Upcoming engagement changes
- Capacity for new work
"""
        return self._call_claude(system_prompt, user_prompt)

    def _generate_margin_analysis(self, data: dict[str, Any]) -> str:
        """Generate margin and profitability analysis."""
        system_prompt = """You are a financial analyst for a consulting firm.
Analyze billing rates, cost rates, and margins to assess profitability.
Provide insights on margin health and improvement opportunities."""

        engagements = data["engagements"]

        # Calculate margin statistics
        margins = [e.get("margin_percent") for e in engagements if e.get("margin_percent") is not None]
        avg_margin = sum(margins) / len(margins) if margins else 0

        bill_rates = [e.get("bill_rate") for e in engagements if e.get("bill_rate") is not None]
        avg_bill_rate = sum(bill_rates) / len(bill_rates) if bill_rates else 0

        cost_rates = [e.get("cost_rate") for e in engagements if e.get("cost_rate") is not None]
        avg_cost_rate = sum(cost_rates) / len(cost_rates) if cost_rates else 0

        user_prompt = f"""Analyze margins and profitability (2-3 paragraphs).

Key Metrics:
- Average Margin: {avg_margin:.1f}%
- Average Bill Rate: ${avg_bill_rate:.2f}/hr
- Average Cost Rate: ${avg_cost_rate:.2f}/hr
- Engagements with margin data: {len(margins)}

Engagement Details (with rates):
{json.dumps([e for e in engagements if e.get('bill_rate') or e.get('cost_rate')][:15], indent=2)}

Focus on:
- Overall margin health
- High/low margin engagements
- Rate benchmarking insights
- Margin improvement opportunities
"""
        return self._call_claude(system_prompt, user_prompt)

    def _generate_recommendations(self, data: dict[str, Any]) -> str:
        """Generate strategic recommendations."""
        system_prompt = """You are a strategic advisor for a consulting firm.
Based on comprehensive CRM data, provide actionable recommendations.
Prioritize recommendations by impact and urgency.
Be specific and practical."""

        user_prompt = f"""Based on all CRM data, provide 5-7 prioritized recommendations.

Data Summary:
- Accounts: {data['summary']['total_accounts']}
- Contacts: {data['summary']['total_contacts']}
- Opportunities: {data['summary']['total_opportunities']}
- Projects: {data['summary']['total_projects']}
- Engagements: {data['summary']['total_engagements']}

Key Data Points:
Accounts: {json.dumps(data['accounts'][:5], indent=2)}
Opportunities: {json.dumps(data['opportunities'][:5], indent=2)}
Engagements: {json.dumps(data['engagements'][:5], indent=2)}

Format each recommendation as:
[Priority: High/Medium/Low] - Recommendation title
Brief explanation and specific action steps.
"""
        return self._call_claude(system_prompt, user_prompt)
