# System Security Plan (SSP)
## NIST RMF Automated POAM System

**Version:** 1.0  
**Date:** April 19, 2026  
**Status:** Draft  
**Classification:** Unclassified  

---

## 1. System Identification

| Field | Value |
|---|---|
| System Name | NIST RMF Automated POAM System |
| System Abbreviation | APAS |
| System Owner | (GRC Engineer) |
| System Type | Major Application |
| Operating Environment | Amazon Web Services (AWS) - us-east-1 |
| Authorization Boundary | AWS Account YOUR-AWS-ACCOUNT-ID |

---

## 2. System Categorization (FIPS 199)

| Information Type | Confidentiality | Integrity | Availability |
|---|---|---|---|
| Security Findings | Moderate | Moderate | Low |
| POAM Records | Moderate | High | Low |
| Audit Logs | Low | High | Low |
| **System Overall** | **Moderate** | **High** | **Low** |

**Overall System Impact Level: MODERATE**

Rationale: POAM records and security findings contain sensitive vulnerability 
information. Unauthorized disclosure could expose exploitable weaknesses. 
Integrity is High because inaccurate POAM data could lead to missed 
remediation deadlines and failed audits.

---

## 3. System Description

### 3.1 Purpose
The NIST RMF Automated POAM System automatically generates, tracks and 
manages Plans of Action and Milestones (POAMs) by ingesting security 
findings from AWS Security Hub and GuardDuty, mapping them to NIST SP 
800-53 controls, and storing them in a centralized repository accessible 
via REST API and web dashboard.

### 3.2 System Architecture
The system is built entirely on AWS serverless and managed services 
operating within the AWS free tier:

| Component | AWS Service | Purpose |
|---|---|---|
| Finding Ingestion | Amazon EventBridge | Routes Security Hub findings to POAM engine |
| POAM Engine | AWS Lambda (Python 3.12) | Parses findings, maps controls, creates POAMs |
| POAM Storage | Amazon DynamoDB | Stores POAM records with TTL |
| POAM Export | Amazon S3 | Stores CSV exports for ATO packages |
| REST API | Amazon API Gateway | Exposes POAM data via REST endpoints |
| Dashboard | Amazon S3 (Static Site) | Web interface for POAM management |
| Notifications | Amazon SNS | Email alerts for HIGH severity POAMs |
| Threat Detection | Amazon GuardDuty | Generates security findings |
| Compliance Assessment | AWS Security Hub | Aggregates findings, maps to NIST controls |
| Audit Logging | AWS CloudTrail | Records all API activity |
| Access Control | AWS IAM | Enforces least privilege |

### 3.3 Data Flow
1. Security Hub ingests findings from GuardDuty and Config
2. EventBridge rule triggers Lambda on every new ACTIVE finding
3. Lambda maps finding to NIST SP 800-53 control family
4. Lambda assigns risk rating and calculates milestone dates
5. POAM record written to DynamoDB
6. SNS notifies stakeholders of HIGH severity POAMs
7. Dashboard displays open POAMs via API Gateway

---

## 4. System Environment

### 4.1 Network Architecture
- All services operate within AWS managed infrastructure
- API Gateway endpoint is publicly accessible (REGIONAL)
- DynamoDB and Lambda operate within AWS private network
- S3 dashboard bucket is publicly readable (static website)
- No EC2 instances or VPCs required

### 4.2 Interconnections
| Connected System | Direction | Data Exchanged | Agreement |
|---|---|---|---|
| AWS Security Hub | Inbound | Security findings | AWS Service Terms |
| AWS GuardDuty | Inbound | Threat findings | AWS Service Terms |
| AWS Config | Inbound | Compliance findings | AWS Service Terms |

---

## 5. Applicable Laws and Regulations

- NIST SP 800-53 Rev 5 - Security and Privacy Controls
- NIST SP 800-37 Rev 2 - Risk Management Framework
- FIPS 199 - Standards for Security Categorization
- FIPS 200 - Minimum Security Requirements
- OMB Circular A-130 - Managing Federal Information Resources

---

## 6. Security Control Implementation

### 6.1 Access Control (AC)

**AC-2 - Account Management**
- IAM roles follow least privilege principle
- Lambda execution role restricted to specific DynamoDB table and S3 bucket
- API Gateway role restricted to invoking poam-api-handler only
- No shared credentials - all access via IAM roles
- Evidence: `01-iam-roles.yaml`

**AC-3 - Access Enforcement**
- DynamoDB access restricted to Lambda execution role only
- S3 export bucket blocks all public access
- IAM policies enforce allow-list of specific actions
- Evidence: `01-iam-roles.yaml`

**AC-17 - Remote Access**
- API Gateway provides controlled remote access to POAM data
- No direct database access from external systems
- All API calls logged via CloudWatch
- Evidence: `05-api-dashboard.yaml`

### 6.2 Audit and Accountability (AU)

**AU-2 - Event Logging**
- CloudTrail enabled for all management events
- Lambda CloudWatch logs capture all POAM creation events
- DynamoDB Streams capture all record changes
- Evidence: `02-data-sources.yaml`

**AU-9 - Protection of Audit Information**
- CloudTrail log file validation enabled
- CloudTrail logs stored in dedicated S3 bucket
- S3 bucket encryption enabled (AES-256)
- Evidence: `02-data-sources.yaml`

**AU-12 - Audit Record Generation**
- Every POAM creation logged with timestamp, finding ID, control ID
- CloudWatch Logs retention configured
- Evidence: `poam_engine.py`

### 6.3 Security Assessment (CA)

**CA-2 - Control Assessments**
- AWS Security Hub continuously assesses controls against NIST SP 800-53
- Assessment results automatically converted to POAMs
- Evidence: Security Hub NIST standard enabled

**CA-5 - Plan of Action and Milestones**
- Automated POAM generation is the primary function of this system
- POAMs include: control ID, risk rating, milestone dates, responsible party
- Evidence: `poam_engine.py`, DynamoDB `poam-records` table

**CA-7 - Continuous Monitoring**
- EventBridge rule monitors Security Hub in real time
- New findings automatically trigger POAM creation within minutes
- Evidence: `04-poam-engine.yaml`

### 6.4 Configuration Management (CM)

**CM-2 - Baseline Configuration**
- All infrastructure defined as code in CloudFormation templates
- Templates stored in version-controlled Git repository
- Evidence: `root-stack.yaml` and all nested stacks

**CM-6 - Configuration Settings**
- CloudFormation parameters enforce approved configuration values
- Environment parameter restricts deployments to dev/staging/prod
- Evidence: `root-stack.yaml`

**CM-7 - Least Functionality**
- Lambda functions restricted to minimum required permissions
- No unnecessary services enabled
- Evidence: `01-iam-roles.yaml`

**CM-8 - System Component Inventory**
- All components defined and tracked in CloudFormation
- CloudFormation stack provides real-time inventory
- Evidence: CloudFormation console

### 6.5 Identification and Authentication (IA)

**IA-2 - Identification and Authentication**
- All AWS API calls authenticated via IAM
- No anonymous access to sensitive resources
- MFA recommended for all IAM users
- Evidence: AWS IAM configuration

**IA-5 - Authenticator Management**
- IAM roles use temporary credentials via STS
- No long-term access keys used by Lambda functions
- Evidence: `01-iam-roles.yaml`

### 6.6 Incident Response (IR)

**IR-6 - Incident Reporting**
- GuardDuty detects and reports security incidents automatically
- SNS notifications alert security team of HIGH severity findings
- POAMs created automatically for all incidents
- Evidence: `06-notifications.yaml`

### 6.7 Risk Assessment (RA)

**RA-5 - Vulnerability Monitoring and Scanning**
- AWS Security Hub continuously scans for vulnerabilities
- GuardDuty monitors for threats and anomalies
- Findings automatically risk-rated as HIGH/MEDIUM/LOW
- Evidence: `poam_engine.py` — `get_milestone_date()` function

### 6.8 System and Communications Protection (SC)

**SC-7 - Boundary Protection**
- S3 export bucket blocks all public access
- DynamoDB not directly accessible from internet
- API Gateway provides controlled boundary
- Evidence: `03-storage.yaml`, `05-api-dashboard.yaml`

**SC-12 - Cryptographic Key Establishment**
- S3 buckets encrypted with AES-256 at rest
- All data in transit encrypted via TLS (HTTPS)
- Evidence: `03-storage.yaml`

**SC-28 - Protection of Information at Rest**
- DynamoDB data encrypted at rest by default
- S3 buckets use server-side encryption (AES-256)
- Evidence: `03-storage.yaml`

### 6.9 System and Information Integrity (SI)

**SI-4 - System Monitoring**
- GuardDuty provides continuous threat monitoring
- CloudWatch monitors Lambda function health
- EventBridge monitors finding ingestion pipeline
- Evidence: `02-data-sources.yaml`, `04-poam-engine.yaml`

---

## 7. POAMs

Current open POAMs are tracked in the automated POAM system and accessible via:
- **Dashboard:** S3 static website endpoint
- **API:** `GET /dev/poams`
- **Export:** S3 exports bucket (CSV format)

---

## 8. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| System Owner | Overall accountability for system security |
| GRC Engineer | Maintain POAM system, review findings, update controls |
| Security Engineer | Respond to HIGH severity POAMs within 30 days |
| Cloud Engineer | Maintain CloudFormation templates and Lambda functions |

---

## 9. Continuous Monitoring Strategy

| Activity | Frequency | Tool | Evidence |
|---|---|---|---|
| Vulnerability scanning | Continuous | Security Hub | POAM records |
| Threat detection | Continuous | GuardDuty | POAM records |
| POAM review | Weekly | POAM Dashboard | Dashboard screenshot |
| Control assessment | Monthly | Security Hub | Security Hub report |
| SSP review | Annually | Manual | This document |

---

## 10. Authorization

| Role | Name | Date |
|---|---|---|
| Authorizing Official | | |
| System Owner | (GRC Engineer) | April 19, 2026 |
| GRC Engineer | (GRC Engineer) | April 19, 2026 |

**Authorization Decision:** Authorized to Operate (ATO)  
**Authorization Date:** April 19, 2026  
**Authorization Expiration:** April 19, 2027  

---

*This SSP was prepared in accordance with NIST SP 800-18 Guide for 
Developing Security Plans for Federal Information Systems.*
