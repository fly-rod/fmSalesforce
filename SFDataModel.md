# Force Multiply – Contractor & Independent Talent Data Model (Salesforce)

## Design Principles
- Use Salesforce standard objects wherever possible
- Separate "who a person is" from "what they are doing right now"
- Store rates/dates/role on an engagement object, not on Contact
- Make reporting easy even when Opportunities change over time

---

## Standard Objects

### Account (Contractor Firm)
Represents a third-party firm, agency, or independent contractor business.

Record Type
- Contractor Firm

Fields (recommended)
- Vendor_Status__c (Picklist)
  - Prospect
  - Approved
  - On Hold
  - Inactive
- Preferred_Vendor__c (Checkbox)
- NDA_Signed__c (Checkbox)
- NDA_Signed_Date__c (Date)
- MSA_Signed__c (Checkbox)
- MSA_Signed_Date__c (Date)
- Notes__c (Long Text Area)

---

### Contact (Contractor / Candidate)
Represents an individual contractor or consultant.

Record Type
- Contractor

Fields (recommended)
- Contractor_Status__c (Picklist)
  - Sourced
  - Vetted
  - Submitted
  - Interviewing
  - Active
  - Inactive
- Primary_Skill_Area__c (Picklist)
  - Data Cloud
  - Salesforce Developer
  - Solution Architect
  - Marketing Cloud
  - Integration
  - AI / Automation
- LinkedIn_URL__c (URL)
- Location__c (Text)
- Timezone__c (Picklist)
- Work_Authorization__c (Picklist)
- Default_Cost_Rate__c (Currency, optional fallback)

---

## Custom Objects

### Contractor_Engagement__c
Represents a specific engagement of a contractor on a specific customer opportunity.
This is where rates, dates, and engagement role belong.

Relationships
- Contractor__c (Lookup → Contact) [Required]
- Contractor_Firm__c (Lookup → Account) [Optional, but recommended]
- Opportunity__c (Lookup → Opportunity) [Required]
- Client_Account__c (Lookup → Account) [Optional safety lookup]
  - Recommendation: auto-populate from Opportunity.AccountId via Flow

Key Fields
- Engagement_Role__c (Picklist)
  - Salesforce Data Cloud Consultant
  - Salesforce Developer
  - Solution Architect
  - Technical Lead
- Engagement_Status__c (Picklist)
  - Proposed
  - Active
  - Paused
  - Completed
  - Cancelled
- Start_Date__c (Date)
- End_Date__c (Date)
- Billing_Type__c (Picklist)
  - Hourly
  - Fixed Fee
- Cost_Rate__c (Currency)
- Bill_Rate__c (Currency)
- Hours_Per_Week__c (Number)
- Margin_Percent__c (Formula)
- Contract_Link__c (URL)
- Notes__c (Long Text Area)

---

## Optional Skill & Certification Objects (Recommended)

### Contractor_Skill__c
Relationships
- Contractor__c (Lookup → Contact)

Fields
- Skill_Name__c (Picklist)
  - Salesforce Data Cloud
  - Identity Resolution
  - Calculated Insights
  - Segmentation
  - MuleSoft
  - Azure
  - SQL
  - AI Enablement
- Skill_Level__c (Picklist)
  - Beginner
  - Intermediate
  - Advanced
  - Expert
- Years_Experience__c (Number)

### Contractor_Certification__c
Relationships
- Contractor__c (Lookup → Contact)

Fields
- Certification_Name__c (Picklist)
  - Salesforce Administrator
  - Platform App Builder
  - Data Cloud Consultant
  - Integration Architecture Designer
  - Data Architect
  - AI Associate
- Date_Earned__c (Date)
- Expiration_Date__c (Date)
- Active__c (Checkbox or Formula)

---

## Activity & Notes Strategy
- Use Tasks/Events for outreach, interviews, follow-ups
- Avoid free-text interaction history fields when Activities will do

---

## Spreadsheet-to-Salesforce Mapping
- Company → Account.Name
- Candidate → Contact.FirstName / Contact.LastName
- Title → Contact.Title or Contractor_Engagement__c.Engagement_Role__c
- Email → Contact.Email
- Phone → Contact.Phone
- LinkedIn → Contact.LinkedIn_URL__c
- Cost Rate → Contractor_Engagement__c.Cost_Rate__c (preferred) or Contact.Default_Cost_Rate__c (fallback)
- Notes → Task/Note related to Contact or Engagement

---

## Reporting Questions This Model Supports
- Who is active right now, by client account, opportunity, and role?
- What is our blended cost rate across active opportunities?
- Which contractors have Data Cloud experience and are available soon?