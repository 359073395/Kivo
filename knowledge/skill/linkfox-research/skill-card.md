## Description: <br>
LinkFoxAgent helps agents run cross-border e-commerce research and reporting across marketplaces, covering product discovery, competitor and keyword analysis, review insights, patents, trends, sourcing, image/PDF analysis, web search, and optional Lingxing ERP data access. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[linkfox-ai](https://clawhub.ai/user/linkfox-ai) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External marketplace sellers, e-commerce operators, analysts, and developers use this skill to delegate product research, competitor analysis, keyword and review mining, patent and compliance checks, marketplace trend research, sourcing, and report generation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Prompts, product images, PDFs, and optional ERP data may be sent to LinkFox or related services. <br>
Mitigation: Avoid secrets, credentials, sensitive personal data, and confidential business material in prompts or uploaded files; use only data approved for the selected service. <br>
Risk: Successful runs may publish a public read-only ShareURL containing task traces, outputs, and downloadable artifacts. <br>
Mitigation: Review outputs before forwarding links, keep sensitive work in segregated environments, and avoid submitting material that should not appear in shared traces. <br>
Risk: The Lingxing ERP helper can access broad business APIs, including sensitive and potentially state-changing endpoints. <br>
Mitigation: Use least-privileged Lingxing credentials, prefer read-only/reporting workflows, and verify parameters before running ERP actions. <br>
Risk: Marketplace, patent, policy, image, PDF, and trend analyses may be incomplete or misleading. <br>
Mitigation: Confirm important business, legal, compliance, and purchasing decisions against authoritative marketplace, legal, supplier, or internal sources. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/linkfox-ai/skills/linkfoxagent) <br>
- [LinkFoxAgent homepage](https://agent.linkfox.com/) <br>
- [Amazon frontend tools](references/amazon-frontend.md) <br>
- [Amazon data insight tools](references/amazon-data-insight.md) <br>
- [Keepa tools](references/keepa.md) <br>
- [Seller Sprite tools](references/seller-sprite.md) <br>
- [Jimu tools](references/jimu.md) <br>
- [TikTok e-commerce tools](references/tiktok.md) <br>
- [Walmart frontend tools](references/walmart.md) <br>
- [eBay frontend tools](references/ebay.md) <br>
- [Shopee tools](references/youying.md) <br>
- [Ozon tools](references/mpstats-ozon.md) <br>
- [1688 sourcing tools](references/1688.md) <br>
- [Google Trends tools](references/google-trends.md) <br>
- [Web search tools](references/web-search.md) <br>
- [Patent search tools](references/patent.md) <br>
- [AI tools](references/ai-tools.md) <br>
- [Sandbox and file analysis tools](references/sandbox.md) <br>
- [Lingxing ERP OpenAPI workflow](references/lingxing-erp.md) <br>
- [Sif analysis tools](references/sif.md) <br>
- [Sorftime tools](references/sorftime.md) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Shell commands, API Calls, Markdown, JSON, Files] <br>
**Output Format:** [Markdown instructions with shell commands, status text, CSV/JSON files, and public share URLs] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires LINKFOXAGENT_API_KEY; long-running tasks are dispatched to sub-agents; successful runs may expose a public read-only ShareURL and downloadable artifacts.] <br>

## Skill Version(s): <br>
1.1.4 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
