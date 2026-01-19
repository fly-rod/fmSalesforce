"""
Salesforce client module for CRM data extraction.

Supports both username/password and SF CLI session authentication.
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from simple_salesforce import Salesforce

from config import SalesforceConfig

logger = logging.getLogger(__name__)


@dataclass
class Account:
    """Represents a Salesforce Account."""
    id: str
    name: str
    account_type: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    nda_signed: bool = False
    msa_signed: bool = False
    notes: Optional[str] = None


@dataclass
class Contact:
    """Represents a Salesforce Contact."""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    contact_role: Optional[str] = None
    contractor_status: Optional[str] = None
    primary_skill: Optional[str] = None
    location: Optional[str] = None
    default_cost_rate: Optional[float] = None


@dataclass
class Opportunity:
    """Represents a Salesforce Opportunity."""
    id: str
    name: str
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[str] = None
    close_date: Optional[str] = None
    probability: Optional[float] = None
    description: Optional[str] = None


@dataclass
class Project:
    """Represents a Salesforce Project."""
    id: str
    name: str
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    opportunity_id: Optional[str] = None
    opportunity_name: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ContractorEngagement:
    """Represents a Salesforce Contractor Engagement."""
    id: str
    name: str
    contractor_id: Optional[str] = None
    contractor_name: Optional[str] = None
    opportunity_id: Optional[str] = None
    opportunity_name: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    client_account_id: Optional[str] = None
    client_account_name: Optional[str] = None
    engagement_role: Optional[str] = None
    engagement_status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    cost_rate: Optional[float] = None
    bill_rate: Optional[float] = None
    hours_per_week: Optional[float] = None
    margin_percent: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class CRMData:
    """Container for all CRM data."""
    accounts: list[Account] = field(default_factory=list)
    contacts: list[Contact] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)
    engagements: list[ContractorEngagement] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "accounts": [vars(a) for a in self.accounts],
            "contacts": [vars(c) for c in self.contacts],
            "opportunities": [vars(o) for o in self.opportunities],
            "projects": [vars(p) for p in self.projects],
            "engagements": [vars(e) for e in self.engagements],
            "extracted_at": self.extracted_at.isoformat(),
            "summary": {
                "total_accounts": len(self.accounts),
                "total_contacts": len(self.contacts),
                "total_opportunities": len(self.opportunities),
                "total_projects": len(self.projects),
                "total_engagements": len(self.engagements),
            },
        }


class SalesforceClient:
    """Client for extracting CRM data from Salesforce."""

    def __init__(self, config: SalesforceConfig):
        """Initialize the Salesforce client."""
        self.config = config
        self._sf: Optional[Salesforce] = None

    def connect(self) -> Salesforce:
        """Establish connection to Salesforce."""
        if self._sf is not None:
            return self._sf

        if self.config.use_cli_session:
            self._sf = self._connect_via_cli()
        else:
            self._sf = self._connect_via_credentials()

        logger.info("Successfully connected to Salesforce")
        return self._sf

    def _connect_via_credentials(self) -> Salesforce:
        """Connect using username/password/security token."""
        if not self.config.username or not self.config.password:
            raise ValueError(
                "SF_USERNAME and SF_PASSWORD are required when not using CLI session"
            )

        logger.info(f"Connecting to Salesforce as {self.config.username}")
        return Salesforce(
            username=self.config.username,
            password=self.config.password,
            security_token=self.config.security_token or "",
            domain=self.config.domain,
        )

    def _connect_via_cli(self) -> Salesforce:
        """Connect using SF CLI session token."""
        logger.info(f"Connecting to Salesforce via CLI ({self.config.cli_target_org})")

        try:
            # Get org info from SF CLI
            result = subprocess.run(
                [
                    "sf",
                    "org",
                    "display",
                    "--target-org",
                    self.config.cli_target_org,
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            org_info = json.loads(result.stdout)["result"]

            instance_url = org_info["instanceUrl"]
            access_token = org_info["accessToken"]

            return Salesforce(instance_url=instance_url, session_id=access_token)

        except subprocess.CalledProcessError as e:
            logger.error(f"SF CLI command failed: {e.stderr}")
            raise RuntimeError(
                f"Failed to get Salesforce session from CLI. "
                f"Make sure you're authenticated: sf org login web -a {self.config.cli_target_org}"
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse SF CLI output: {e}")
            raise RuntimeError("Failed to parse Salesforce CLI response")

    def extract_all_data(self) -> CRMData:
        """Extract all CRM data from Salesforce."""
        sf = self.connect()

        logger.info("Extracting CRM data from Salesforce...")

        data = CRMData(
            accounts=self._extract_accounts(sf),
            contacts=self._extract_contacts(sf),
            opportunities=self._extract_opportunities(sf),
            projects=self._extract_projects(sf),
            engagements=self._extract_engagements(sf),
        )

        logger.info(
            f"Extracted: {len(data.accounts)} accounts, {len(data.contacts)} contacts, "
            f"{len(data.opportunities)} opportunities, {len(data.projects)} projects, "
            f"{len(data.engagements)} engagements"
        )

        return data

    def _extract_accounts(self, sf: Salesforce) -> list[Account]:
        """Extract Account records."""
        query = """
            SELECT Id, Name, Account_Type__c, Industry, Website,
                   NDA_Signed__c, MSA_Signed__c, Notes__c
            FROM Account
            ORDER BY Name
        """
        results = sf.query_all(query)

        return [
            Account(
                id=r["Id"],
                name=r["Name"],
                account_type=r.get("Account_Type__c"),
                industry=r.get("Industry"),
                website=r.get("Website"),
                nda_signed=r.get("NDA_Signed__c", False),
                msa_signed=r.get("MSA_Signed__c", False),
                notes=r.get("Notes__c"),
            )
            for r in results["records"]
        ]

    def _extract_contacts(self, sf: Salesforce) -> list[Contact]:
        """Extract Contact records."""
        query = """
            SELECT Id, Name, Email, Phone, Title,
                   AccountId, Account.Name,
                   Contact_Role__c, Contractor_Status__c,
                   Primary_Skill_Area__c, Location__c, Default_Cost_Rate__c
            FROM Contact
            ORDER BY Name
        """
        results = sf.query_all(query)

        return [
            Contact(
                id=r["Id"],
                name=r["Name"],
                email=r.get("Email"),
                phone=r.get("Phone"),
                title=r.get("Title"),
                account_id=r.get("AccountId"),
                account_name=r.get("Account", {}).get("Name") if r.get("Account") else None,
                contact_role=r.get("Contact_Role__c"),
                contractor_status=r.get("Contractor_Status__c"),
                primary_skill=r.get("Primary_Skill_Area__c"),
                location=r.get("Location__c"),
                default_cost_rate=r.get("Default_Cost_Rate__c"),
            )
            for r in results["records"]
        ]

    def _extract_opportunities(self, sf: Salesforce) -> list[Opportunity]:
        """Extract Opportunity records."""
        query = """
            SELECT Id, Name, AccountId, Account.Name,
                   Amount, StageName, CloseDate, Probability, Description
            FROM Opportunity
            ORDER BY CloseDate DESC
        """
        results = sf.query_all(query)

        return [
            Opportunity(
                id=r["Id"],
                name=r["Name"],
                account_id=r.get("AccountId"),
                account_name=r.get("Account", {}).get("Name") if r.get("Account") else None,
                amount=r.get("Amount"),
                stage=r.get("StageName"),
                close_date=r.get("CloseDate"),
                probability=r.get("Probability"),
                description=r.get("Description"),
            )
            for r in results["records"]
        ]

    def _extract_projects(self, sf: Salesforce) -> list[Project]:
        """Extract Project__c records."""
        query = """
            SELECT Id, Name,
                   Account__c, Account__r.Name,
                   Opportunity__c, Opportunity__r.Name,
                   Project_Status__c, Budget__c,
                   Start_Date__c, End_Date__c,
                   Description__c, Notes__c
            FROM Project__c
            ORDER BY Start_Date__c DESC
        """
        results = sf.query_all(query)

        return [
            Project(
                id=r["Id"],
                name=r["Name"],
                account_id=r.get("Account__c"),
                account_name=r.get("Account__r", {}).get("Name") if r.get("Account__r") else None,
                opportunity_id=r.get("Opportunity__c"),
                opportunity_name=r.get("Opportunity__r", {}).get("Name") if r.get("Opportunity__r") else None,
                status=r.get("Project_Status__c"),
                budget=r.get("Budget__c"),
                start_date=r.get("Start_Date__c"),
                end_date=r.get("End_Date__c"),
                description=r.get("Description__c"),
                notes=r.get("Notes__c"),
            )
            for r in results["records"]
        ]

    def _extract_engagements(self, sf: Salesforce) -> list[ContractorEngagement]:
        """Extract Contractor_Engagement__c records."""
        query = """
            SELECT Id, Name,
                   Contractor__c, Contractor__r.Name,
                   Opportunity__c, Opportunity__r.Name,
                   Project__c, Project__r.Name,
                   Client_Account__c, Client_Account__r.Name,
                   Engagement_Role__c, Engagement_Status__c,
                   Start_Date__c, End_Date__c,
                   Cost_Rate__c, Bill_Rate__c,
                   Hours_Per_Week__c, Margin_Percent__c,
                   Notes__c
            FROM Contractor_Engagement__c
            ORDER BY Start_Date__c DESC
        """
        results = sf.query_all(query)

        return [
            ContractorEngagement(
                id=r["Id"],
                name=r["Name"],
                contractor_id=r.get("Contractor__c"),
                contractor_name=r.get("Contractor__r", {}).get("Name") if r.get("Contractor__r") else None,
                opportunity_id=r.get("Opportunity__c"),
                opportunity_name=r.get("Opportunity__r", {}).get("Name") if r.get("Opportunity__r") else None,
                project_id=r.get("Project__c"),
                project_name=r.get("Project__r", {}).get("Name") if r.get("Project__r") else None,
                client_account_id=r.get("Client_Account__c"),
                client_account_name=r.get("Client_Account__r", {}).get("Name") if r.get("Client_Account__r") else None,
                engagement_role=r.get("Engagement_Role__c"),
                engagement_status=r.get("Engagement_Status__c"),
                start_date=r.get("Start_Date__c"),
                end_date=r.get("End_Date__c"),
                cost_rate=r.get("Cost_Rate__c"),
                bill_rate=r.get("Bill_Rate__c"),
                hours_per_week=r.get("Hours_Per_Week__c"),
                margin_percent=r.get("Margin_Percent__c"),
                notes=r.get("Notes__c"),
            )
            for r in results["records"]
        ]
