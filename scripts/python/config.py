"""
Configuration module for CRM Summary Report Generator.

Loads configuration from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


@dataclass
class SalesforceConfig:
    """Salesforce connection configuration."""
    username: Optional[str] = None
    password: Optional[str] = None
    security_token: Optional[str] = None
    domain: str = "login"
    use_cli_session: bool = False
    cli_target_org: str = "FMCDev"

    @classmethod
    def from_env(cls) -> "SalesforceConfig":
        """Load configuration from environment variables."""
        return cls(
            username=os.getenv("SF_USERNAME"),
            password=os.getenv("SF_PASSWORD"),
            security_token=os.getenv("SF_SECURITY_TOKEN", ""),
            domain=os.getenv("SF_DOMAIN", "login"),
            use_cli_session=os.getenv("SF_USE_CLI_SESSION", "false").lower() == "true",
            cli_target_org=os.getenv("SF_CLI_TARGET_ORG", "FMCDev"),
        )


@dataclass
class ClaudeConfig:
    """Claude API configuration."""
    api_key: str
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

    @classmethod
    def from_env(cls) -> "ClaudeConfig":
        """Load configuration from environment variables."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        return cls(
            api_key=api_key,
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=int(os.getenv("CLAUDE_MAX_TOKENS", "4096")),
        )


@dataclass
class OutputConfig:
    """Output configuration."""
    output_dir: Path
    report_filename: str

    @classmethod
    def from_env(cls) -> "OutputConfig":
        """Load configuration from environment variables."""
        output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        return cls(
            output_dir=output_dir,
            report_filename=os.getenv("REPORT_FILENAME", "crm_summary_report.pdf"),
        )

    @property
    def report_path(self) -> Path:
        """Full path to the output report."""
        return self.output_dir / self.report_filename


@dataclass
class AppConfig:
    """Main application configuration."""
    salesforce: SalesforceConfig
    claude: ClaudeConfig
    output: OutputConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load all configuration from environment variables."""
        return cls(
            salesforce=SalesforceConfig.from_env(),
            claude=ClaudeConfig.from_env(),
            output=OutputConfig.from_env(),
        )


def get_config() -> AppConfig:
    """Get the application configuration."""
    return AppConfig.from_env()
