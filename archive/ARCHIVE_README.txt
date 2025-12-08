ARCHIVE METADATA
=================
Created: 2025-12-08_21-42-21_UTC
Source: Google Cloud Apigee Hybrid API Documentation
URL: https://docs.cloud.google.com/apigee/docs/reference/apis/apigee/rest
API Version: v1

PURPOSE
-------
This archive contains comprehensive documentation of Apigee Hybrid REST APIs
for the MCP server implementation. The documentation is timestamped to enable
future delta comparisons and version tracking.

STRUCTURE
---------
00-index.txt                    - Table of contents and overview
01-organizations-api.txt        - Organizations API
02-environments-api.txt         - Environments API
03-api-proxies-api.txt         - API Proxies and Deployments
04-developers-api.txt          - Developers API
05-apps-api.txt                - Apps (Developer and Company/Team)
06-api-products-api.txt        - API Products
07-shared-flows-api.txt        - Shared Flows
08-keystores-api.txt           - Keystores and Truststores with Aliases
09-companies-teams-api.txt     - Companies (Teams) API
10-debug-trace-api.txt         - Debug Sessions (Trace) API

COVERAGE
--------
✓ Organizations management
✓ Environments configuration
✓ API Proxies lifecycle (create, deploy, update, delete)
✓ Developers management
✓ Developer apps with credentials
✓ Company (team) apps with credentials
✓ API Products with quotas and rate limiting
✓ Shared Flows
✓ Keystores and Truststores
✓ Certificate and key management (aliases)
✓ Companies (Teams) with developers
✓ Debug sessions (Trace) for troubleshooting

ADDITIONAL APIS NOT YET DOCUMENTED
-----------------------------------
- Analytics API (queries, reports, custom reports)
- Target Servers
- Virtual Hosts
- Key Value Maps (KVM)
- Caches
- References
- Resource Files
- Flow Hooks
- Data Collectors
- Security Reports
- Instance Attachments
- NAT Addresses
- Environment Groups
- Endpoint Attachments

USAGE
-----
These documentation files serve as:
1. Reference for MCP tool implementation
2. Schema definitions for API requests/responses
3. Examples for testing
4. Error code documentation
5. Best practices guide
6. Baseline for future documentation updates

DELTA TRACKING
--------------
To compare with future documentation versions:
1. Save new documentation with new timestamp
2. Use diff tools to identify changes
3. Update MCP server implementation accordingly
4. Archive historical versions for audit trail

NOTES
-----
- All timestamps are in UTC
- Documentation is based on official Google Cloud docs
- API endpoints may evolve; check for updates quarterly
- Test all implementations against actual API
- Report API discrepancies to Google Cloud support
