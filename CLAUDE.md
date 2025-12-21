# CLAUDE.md

## Project Context
This repository supports Force Multiply internal tooling and Salesforce data modeling for managing **both sales and staffing** within a single Salesforce instance.

The system must support:
- Selling services to financial services clients (sales pipeline, client contacts, relationships)
- Managing third-party contractors and independent consultants
- Staffing those contractors onto client opportunities and engagements
- Tracking rates, margin, delivery, and availability
- Preparing clean, AI- and Data Cloud–ready data structures

This is **not** an ATS or HRIS.  
This is a **services operator CRM** that supports revenue and delivery.

---

## Core Principles (Follow These Always)

1. Salesforce must support **both sales and staffing workflows**
2. Use Salesforce standard objects wherever possible
3. Separate **who someone is** from **what they are doing**
4. Store rates, roles, and dates on engagement-style objects
5. Optimize for reporting, margin visibility, and automation
6. Start lean; extend intentionally
7. Never initialize Git outside the project directory

---

## Salesforce Data Model – High-Level Intent

### Account
Accounts represent **companies**, not roles.
An Account may be:
- A client (buyer of services)
- A contractor firm (vendor)
- Both, in rare cases

Do NOT create separate objects for “Client” vs “Vendor.”

---

### Contact
Contacts represent **people**.
A Contact may be:
- A client-side contact (buyer, stakeholder, decision-maker)
- A contractor / consultant
- Both, over time

Do NOT duplicate people across objects.

Use Record Types and status fields to differentiate behavior and lifecycle.

---

## Standard Objects

### Account
Used for:
- Client companies
- Contractor firms / vendors

Recommended fields:
- Account_Type__c (Picklist)
  - Client
  - Contractor Firm
  - Both
- Vendor_Status__c (Picklist, contractor firms only)
- Preferred_Vendor__c (Checkbox)
- NDA_Signed__c / MSA_Signed__c (Checkbox + Date)

---

### Contact
Used for:
- Client contacts (sales relationships)
- Contractors / consultants (delivery resources)

Recommended Record Types:
- Client Contact
- Contractor

Recommended fields:
- Contact_Role__c (Picklist)
  - Client Stakeholder
  - Decision Maker
  - Contractor
- Contractor_Status__c (for Contractor record type)
- LinkedIn_URL__c
- Location__c / Timezone__c
- Default_Cost_Rate__c (optional fallback)

---

### Opportunity
Represents **revenue-generating work**.
Used for:
- New sales
- Retainers
- Project-based engagements

Opportunities are the **bridge** between sales and staffing.

---

## Custom Objects

### Contractor_Engagement__c
Represents a contractor working on a specific **client Opportunity**.

This object is critical and must remain clean.

Relationships:
- Contractor__c (Lookup → Contact, Required)
- Opportunity__c (Lookup → Opportunity, Required)
- Client_Account__c (Lookup → Account, Optional but recommended)
  - Auto-populated from Opportunity.AccountId

Key fields:
- Engagement_Role__c
- Engagement_Status__c
- Start_Date__c / End_Date__c
- Cost_Rate__c
- Bill_Rate__c
- Hours_Per_Week__c
- Margin_Percent__c (Formula)
- Notes__c

This object enables:
- Staffing visibility
- Margin reporting
- Capacity planning

---

## Optional Extension Objects

### Contractor_Skill__c
Tracks skills per contractor for staffing and search.

### Contractor_Certification__c
Tracks Salesforce and related certifications.

These should be added only when filtering/search needs justify them.

---

## Sales + Staffing Working Together (Critical)

Salesforce must support:
- Tracking **client contacts** and relationship history
- Managing **pipeline and opportunities**
- Staffing contractors onto sold work
- Understanding margin impact before and after close

Design implication:
- Client Contacts stay related to Accounts and Opportunities
- Contractors stay as Contacts but are tied to delivery via Contractor_Engagement__c
- No duplication of people or companies

Ask this question before adding anything:
“Is this about selling the work, or delivering the work?”

---

## Automation & Flow Guidance

- Use Record-Triggered Flows over Apex by default
- Auto-populate Client_Account__c on Contractor_Engagement__c from Opportunity
- Avoid automation on Contact unless lifecycle-driven
- Never hardcode IDs
- Keep automation explainable to a non-developer operator

---

## Deployment Protocol (Critical)

**Always deploy changes to FMCDev immediately after creating or modifying metadata.**

Default deployment command:
```bash
sf project deploy start --source-dir force-app/main/default --target-org FMCDev
```

Specific deployments:
```bash
# Objects only
sf project deploy start --source-dir force-app/main/default/objects --target-org FMCDev

# Permission sets only
sf project deploy start --source-dir force-app/main/default/permissionsets --target-org FMCDev

# Flows only
sf project deploy start --source-dir force-app/main/default/flows --target-org FMCDev
```

Deployment checklist:
- Create or modify metadata files
- Deploy immediately to FMCDev
- Verify deployment success
- Update user if deployment fails

Never leave metadata undeployed. FMCDev is the default target org.

---

## Reporting & Analytics Intent

The system must answer:
- Who are my key client contacts and where are deals stuck?
- Which contractors are active on which clients?
- What is my blended cost and margin by Opportunity?
- Do I have staffing capacity to close new work?
- Which skills are most in demand across clients?

All schema decisions should support these questions.

---

## Git & Repo Hygiene (Mandatory)

- Git must only be initialized at the project root
- Never initialize Git in:
  - Home directory
  - User directory
  - Tooling or config directories
- Add a strict `.gitignore` early

Recommended ignores:
- .DS_Store
- *.log
- .claude/
- .aitk/
- node_modules/
- dist/

---

## How Claude Should Behave

Claude should:
- Treat this as a **sales + delivery system**
- Propose schema changes before implementing them
- Favor declarative Salesforce solutions
- **Always deploy to FMCDev immediately after creating/modifying metadata**
- Keep responses concise and implementation-ready
- Respect that this is an operator-managed system

Claude should NOT:
- Assume this is a recruiting-only or HR system
- Duplicate Accounts or Contacts by role
- Over-model early
- Initialize Git or modify repo structure without instruction

---

## Tone & Style
- Operator-minded
- Practical
- Outcome-driven
- Minimal fluff
- PE-grade clarity

This system should feel like something a managing partner could open and understand.

---
- please also git add . git commit and git push each time you finish up a change