"""
VTX Earn Arena — Card Definitions Catalog
===========================================
Contains 305 unique cards across 8 categories.
Each tuple: (code, title, rarity, base_cost, description)

Image URLs are generated automatically from the card code
using picsum.photos CDN (deterministic, always available).

Rarity tiers & profit-per-hour at max stage (15):
  common     → 40,000 – 55,000 PPH
  rare       → 60,000 – 75,000 PPH
  epic       → 80,000 – 90,000 PPH
  legendary  → 90,000 – 100,000 PPH

Upgrade cost formula:
  cost(stage) = base_cost × 3^(stage − 1)
  Each upgrade costs 300% more than the previous one.
"""

from __future__ import annotations


def card_image_url(code: str) -> str:
    """Generate a reliable image URL from picsum.photos seeded by card code."""
    return f"https://picsum.photos/seed/{code}/400/300"


# ---------------------------------------------------------------------------
# RARITY → (stage_profit_min, stage_profit_max)
# These define profit-per-hour at stage 1 and stage 15 respectively.
# ---------------------------------------------------------------------------
RARITY_PROFIT_RANGES: dict[str, tuple[float, float]] = {
    "common":    (40_000.0, 55_000.0),
    "rare":      (60_000.0, 75_000.0),
    "epic":      (80_000.0, 90_000.0),
    "legendary": (90_000.0, 100_000.0),
}

# Type alias for a single card definition tuple
CardTuple = tuple[str, str, str, float, str]


# ===========================================================================
#  CATEGORY 1: MARKETING  (40 cards)
# ===========================================================================
MARKETING_CARDS: list[CardTuple] = [
    # ── Common (16) ───────────────────────────────────────────────────────
    ("mkt_social_mgr", "Social Media Manager", "common", 80, "Hire a social media manager to boost brand awareness"),
    ("mkt_email_camp", "Email Campaign", "common", 95, "Launch targeted email campaigns to engage users"),
    ("mkt_brochure", "Print Brochures", "common", 60, "Design and distribute high-quality brochures"),
    ("mkt_blog_writer", "Blog Content Writer", "common", 110, "Publish engaging blog posts to attract organic traffic"),
    ("mkt_google_ads", "Google Ads Basic", "common", 130, "Run basic Google Ads campaigns for brand visibility"),
    ("mkt_fb_ads", "Facebook Ads Starter", "common", 120, "Set up Facebook advertising for user acquisition"),
    ("mkt_newsletter", "Weekly Newsletter", "common", 70, "Curate and send weekly newsletters to subscribers"),
    ("mkt_landing_pg", "Landing Page Builder", "common", 150, "Create high-converting landing pages"),
    ("mkt_ab_testing", "A/B Testing Tool", "common", 100, "Implement A/B testing for marketing materials"),
    ("mkt_brand_kit", "Brand Identity Kit", "common", 200, "Design complete brand guidelines and assets"),
    ("mkt_content_cal", "Content Calendar", "common", 85, "Organize content strategy with editorial calendar"),
    ("mkt_hashtag", "Hashtag Strategy", "common", 55, "Research and implement trending hashtag strategies"),
    ("mkt_story_ads", "Story Advertisements", "common", 140, "Create vertical story ads for Instagram and TikTok"),
    ("mkt_clickbait", "Viral Headlines Lab", "common", 105, "Craft attention-grabbing headlines for viral reach"),
    ("mkt_podcast_ad", "Podcast Sponsorship", "common", 175, "Sponsor popular podcasts for brand exposure"),
    ("mkt_local_seo", "Local SEO Campaign", "common", 160, "Optimize local search engine presence"),
    # ── Rare (12) ─────────────────────────────────────────────────────────
    ("mkt_influencer", "Influencer Partnership", "rare", 650, "Partner with top influencers for product promotion"),
    ("mkt_viral_vid", "Viral Video Studio", "rare", 800, "Produce viral video content for maximum engagement"),
    ("mkt_seo_pro", "SEO Master Suite", "rare", 950, "Advanced SEO optimization with AI-powered tools"),
    ("mkt_tiktok_mgr", "TikTok Growth Manager", "rare", 700, "Manage TikTok presence with growth hacking"),
    ("mkt_yt_channel", "YouTube Channel Pro", "rare", 1200, "Professional YouTube channel management"),
    ("mkt_affiliate", "Affiliate Network", "rare", 1500, "Build and manage a large affiliate network"),
    ("mkt_retarget", "Retargeting Engine", "rare", 1100, "Advanced retargeting ads across all platforms"),
    ("mkt_brand_amb", "Brand Ambassador Program", "rare", 900, "Recruit and manage brand ambassadors globally"),
    ("mkt_collab", "Cross-Brand Collaboration", "rare", 1300, "Partner with complementary brands for co-marketing"),
    ("mkt_webinar", "Webinar Production Suite", "rare", 750, "Host professional webinars for lead generation"),
    ("mkt_pr_wire", "Press Release Wire", "rare", 600, "Distribute press releases to major news outlets"),
    ("mkt_event_mkt", "Event Marketing", "rare", 1400, "Organize marketing events and trade shows"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("mkt_celeb_deal", "Celebrity Endorsement", "epic", 5000, "Secure celebrity endorsements for massive reach"),
    ("mkt_tv_advert", "Television Ad Campaign", "epic", 8000, "Prime-time TV advertising campaign production"),
    ("mkt_super_bowl", "Super Bowl Ad Spot", "epic", 12000, "Book a Super Bowl commercial slot"),
    ("mkt_ai_target", "AI Audience Targeting", "epic", 6500, "Machine learning driven audience targeting system"),
    ("mkt_global_pr", "Global PR Campaign", "epic", 7500, "Worldwide public relations management"),
    ("mkt_metaverse", "Metaverse Marketing Hub", "epic", 9000, "Establish marketing presence in virtual worlds"),
    ("mkt_growth_hack", "Growth Hacking Lab", "epic", 4500, "Experimental growth hacking strategies"),
    ("mkt_data_studio", "Big Data Analytics Studio", "epic", 10000, "Enterprise analytics for marketing intelligence"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("mkt_monopoly", "Market Monopoly Engine", "legendary", 25000, "Dominate entire market segments with AI-driven strategies"),
    ("mkt_neuro", "Neuromarketing Lab", "legendary", 35000, "Brain-scan based marketing optimization center"),
    ("mkt_quantum", "Quantum Ad Optimizer", "legendary", 50000, "Quantum computing powered advertising system"),
    ("mkt_world_dom", "World Domination PR", "legendary", 75000, "Ultimate global marketing dominance package"),
]


# ===========================================================================
#  CATEGORY 2: DEVELOPMENT  (40 cards)
# ===========================================================================
DEVELOPMENT_CARDS: list[CardTuple] = [
    # ── Common (16) ───────────────────────────────────────────────────────
    ("dev_html_site", "HTML Website", "common", 50, "Build a basic HTML5 website for your business"),
    ("dev_css_design", "CSS Design System", "common", 65, "Create a modern CSS design framework"),
    ("dev_js_vanilla", "Vanilla JavaScript", "common", 75, "Implement core JavaScript functionality"),
    ("dev_python_bot", "Python Bot Script", "common", 90, "Develop a simple automation bot in Python"),
    ("dev_react_comp", "React Components", "common", 120, "Build reusable React UI components library"),
    ("dev_api_basic", "REST API Basics", "common", 100, "Create a basic REST API with CRUD operations"),
    ("dev_database", "Database Setup", "common", 85, "Configure and optimize a production database"),
    ("dev_git_flow", "Git Workflow", "common", 60, "Establish professional Git branching strategy"),
    ("dev_unit_test", "Unit Testing Suite", "common", 110, "Implement comprehensive unit test coverage"),
    ("dev_docker", "Docker Container", "common", 130, "Containerize applications with Docker"),
    ("dev_cicd_pipe", "CI/CD Pipeline", "common", 150, "Set up automated build and deployment pipeline"),
    ("dev_debug_tool", "Debug Toolkit", "common", 70, "Advanced debugging and profiling tools"),
    ("dev_code_review", "Code Review Bot", "common", 95, "Automated code review and quality checks"),
    ("dev_npm_pkg", "NPM Package", "common", 80, "Publish and maintain open source NPM package"),
    ("dev_mobile_app", "Mobile App MVP", "common", 200, "Ship a minimum viable mobile application"),
    ("dev_linter", "Code Linter Setup", "common", 55, "Configure linting rules for code quality"),
    # ── Rare (12) ─────────────────────────────────────────────────────────
    ("dev_k8s", "Kubernetes Cluster", "rare", 800, "Deploy and manage a Kubernetes production cluster"),
    ("dev_microserv", "Microservices Architecture", "rare", 1200, "Design and implement microservices system"),
    ("dev_graphql", "GraphQL Gateway", "rare", 700, "Build a high-performance GraphQL API gateway"),
    ("dev_redis_cache", "Redis Caching Layer", "rare", 600, "Implement Redis for ultra-fast caching"),
    ("dev_websocket", "WebSocket Real-time Engine", "rare", 900, "Build real-time communication with WebSockets"),
    ("dev_ml_model", "ML Model Training", "rare", 1500, "Train machine learning models for predictions"),
    ("dev_terraform", "Infrastructure as Code", "rare", 1000, "Manage cloud infrastructure with Terraform"),
    ("dev_elk_stack", "ELK Monitoring Stack", "rare", 850, "Set up Elasticsearch, Logstash, Kibana stack"),
    ("dev_grpc", "gRPC Service Mesh", "rare", 750, "Build high-performance gRPC service mesh"),
    ("dev_rust_core", "Rust Performance Core", "rare", 1300, "Rewrite critical paths in Rust for speed"),
    ("dev_flutter", "Flutter Cross-Platform", "rare", 1100, "Build cross-platform apps with Flutter"),
    ("dev_wasm", "WebAssembly Engine", "rare", 950, "Compile to WebAssembly for browser performance"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("dev_ai_engine", "AI Engine Core", "epic", 5500, "Build a custom artificial intelligence engine"),
    ("dev_blockchain", "Blockchain Node", "epic", 7000, "Deploy and maintain a full blockchain node"),
    ("dev_cloud_arch", "Cloud Architecture", "epic", 9000, "Enterprise cloud architecture design"),
    ("dev_quantum_sdk", "Quantum Computing SDK", "epic", 12000, "Develop quantum computing applications"),
    ("dev_neural_net", "Neural Network Lab", "epic", 8000, "Deep neural network training facility"),
    ("dev_edge_comp", "Edge Computing Grid", "epic", 6500, "Distributed edge computing network"),
    ("dev_zero_day", "Zero-Day Patch Engine", "epic", 10000, "Automated vulnerability detection and patching"),
    ("dev_metaverse_sdk", "Metaverse Development Kit", "epic", 11000, "Tools for building metaverse experiences"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("dev_agi_core", "AGI Research Lab", "legendary", 30000, "Artificial general intelligence research center"),
    ("dev_quantum_net", "Quantum Internet Node", "legendary", 45000, "Next-generation quantum internet infrastructure"),
    ("dev_self_code", "Self-Writing Codebase", "legendary", 60000, "AI system that writes and improves its own code"),
    ("dev_reality_eng", "Reality Engine", "legendary", 80000, "Full-stack reality simulation rendering engine"),
]


# ===========================================================================
#  CATEGORY 3: LEGAL & COMPLIANCE  (38 cards)
# ===========================================================================
LEGAL_CARDS: list[CardTuple] = [
    # ── Common (16) ───────────────────────────────────────────────────────
    ("law_terms_svc", "Terms of Service", "common", 60, "Draft comprehensive terms of service"),
    ("law_privacy", "Privacy Policy", "common", 55, "Create GDPR-compliant privacy policy"),
    ("law_nda", "Non-Disclosure Agreement", "common", 70, "Standard NDA template for partnerships"),
    ("law_trademark", "Trademark Registration", "common", 120, "Register and protect your brand trademark"),
    ("law_copyright", "Copyright Filing", "common", 90, "File copyright protection for content"),
    ("law_contract", "Service Contracts", "common", 100, "Draft professional service contracts"),
    ("law_cookie", "Cookie Consent Manager", "common", 50, "Implement cookie consent compliance"),
    ("law_aml_basic", "Basic AML Check", "common", 130, "Implement basic anti-money laundering checks"),
    ("law_kyc_form", "KYC Form Setup", "common", 140, "Set up Know Your Customer verification forms"),
    ("law_compliance", "Compliance Checklist", "common", 80, "Create regulatory compliance checklist"),
    ("law_dispute", "Dispute Resolution", "common", 110, "Establish dispute resolution procedures"),
    ("law_insurance", "Business Insurance", "common", 150, "Secure comprehensive business insurance"),
    ("law_tax_basic", "Tax Filing Basics", "common", 75, "Set up basic tax filing and reporting"),
    ("law_data_prot", "Data Protection Officer", "common", 160, "Appoint and train a data protection officer"),
    ("law_whistlblw", "Whistleblower System", "common", 95, "Implement anonymous whistleblower reporting"),
    ("law_audit_prep", "Audit Preparation", "common", 85, "Prepare documents for regulatory audits"),
    # ── Rare (12) ─────────────────────────────────────────────────────────
    ("law_crypto_lic", "Crypto License", "rare", 800, "Obtain cryptocurrency trading license"),
    ("law_patent", "Patent Portfolio", "rare", 1200, "Build and manage intellectual property patents"),
    ("law_gdpr_full", "Full GDPR Compliance", "rare", 1000, "Achieve complete GDPR compliance certification"),
    ("law_sec_filing", "SEC Filing Agent", "rare", 1500, "Prepare and submit SEC regulatory filings"),
    ("law_offshore", "Offshore Structure", "rare", 900, "Set up compliant offshore corporate structure"),
    ("law_fund_reg", "Fund Registration", "rare", 1300, "Register an investment fund legally"),
    ("law_aml_pro", "Advanced AML System", "rare", 700, "Enterprise anti-money laundering platform"),
    ("law_sanctions", "Sanctions Screening", "rare", 650, "Real-time global sanctions list screening"),
    ("law_arbitrate", "International Arbitration", "rare", 1100, "Access to international arbitration courts"),
    ("law_fintech", "FinTech Regulatory Pack", "rare", 1400, "Complete fintech regulatory compliance package"),
    ("law_tax_optim", "Tax Optimization", "rare", 850, "Legal tax optimization and planning"),
    ("law_multi_jur", "Multi-Jurisdiction License", "rare", 1600, "Operate legally across multiple jurisdictions"),
    # ── Epic (6) ──────────────────────────────────────────────────────────
    ("law_global_lic", "Global Operating License", "epic", 5000, "Universal license for worldwide operations"),
    ("law_lobbying", "Government Lobbying", "epic", 8000, "Professional government relations and lobbying"),
    ("law_immunity", "Legal Immunity Shield", "epic", 12000, "Comprehensive legal protection framework"),
    ("law_central_bk", "Central Bank Agreement", "epic", 10000, "Establish direct relationship with central bank"),
    ("law_reg_sandbox", "Regulatory Sandbox Entry", "epic", 7000, "Enter government fintech regulatory sandbox"),
    ("law_dao_legal", "DAO Legal Framework", "epic", 6000, "Legal structure for decentralized autonomous org"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("law_sovereignty", "Digital Sovereignty", "legendary", 25000, "Achieve digital sovereignty with own legal framework"),
    ("law_world_bank", "World Bank Partnership", "legendary", 40000, "Strategic partnership with World Bank group"),
    ("law_swiss_vault", "Swiss Vault License", "legendary", 55000, "Swiss banking vault level security license"),
    ("law_un_charter", "UN Digital Charter", "legendary", 70000, "United Nations digital commerce charter"),
]


# ===========================================================================
#  CATEGORY 4: MARKETS & TRADING  (40 cards)
# ===========================================================================
MARKETS_CARDS: list[CardTuple] = [
    # ── Common (16) ───────────────────────────────────────────────────────
    ("mks_spot_trade", "Spot Trading Desk", "common", 80, "Set up basic spot trading operations"),
    ("mks_order_book", "Order Book Engine", "common", 100, "Build a real-time order book system"),
    ("mks_price_feed", "Price Feed Service", "common", 70, "Integrate live cryptocurrency price feeds"),
    ("mks_candle_chart", "Candlestick Charts", "common", 90, "Implement interactive candlestick charting"),
    ("mks_portfolio", "Portfolio Tracker", "common", 65, "Build a multi-asset portfolio tracker"),
    ("mks_alert_sys", "Price Alert System", "common", 75, "Set up customizable price alert notifications"),
    ("mks_exchange_link", "Exchange Connector", "common", 120, "Connect to major cryptocurrency exchanges"),
    ("mks_wallet_mgr", "Wallet Manager", "common", 110, "Multi-wallet management interface"),
    ("mks_trade_hist", "Trade History Logger", "common", 55, "Record and analyze all trading activity"),
    ("mks_limit_order", "Limit Order Engine", "common", 130, "Implement limit order functionality"),
    ("mks_stop_loss", "Stop-Loss Automation", "common", 140, "Automated stop-loss order placement"),
    ("mks_market_cap", "Market Cap Dashboard", "common", 60, "Real-time market capitalization tracker"),
    ("mks_gas_track", "Gas Fee Tracker", "common", 50, "Monitor blockchain gas fees in real-time"),
    ("mks_dex_swap", "DEX Swap Interface", "common", 150, "Decentralized exchange token swap UI"),
    ("mks_nft_list", "NFT Marketplace Listing", "common", 160, "List and manage NFTs on marketplaces"),
    ("mks_staking", "Staking Pool", "common", 200, "Set up proof-of-stake staking pools"),
    # ── Rare (12) ─────────────────────────────────────────────────────────
    ("mks_futures", "Futures Trading Engine", "rare", 800, "Leveraged futures contract trading platform"),
    ("mks_options", "Options Trading Desk", "rare", 900, "Crypto options trading with Greeks analysis"),
    ("mks_arb_bot", "Arbitrage Bot", "rare", 1200, "Cross-exchange arbitrage detection and execution"),
    ("mks_liq_pool", "Liquidity Pool Manager", "rare", 1000, "Manage deep liquidity pools for trading"),
    ("mks_margin", "Margin Trading System", "rare", 1100, "Enable margin trading with risk management"),
    ("mks_otc_desk", "OTC Trading Desk", "rare", 1500, "Over-the-counter large volume trading desk"),
    ("mks_copy_trade", "Copy Trading Platform", "rare", 700, "Enable users to copy top traders automatically"),
    ("mks_grid_bot", "Grid Trading Bot", "rare", 650, "Automated grid trading strategy bot"),
    ("mks_dca_engine", "DCA Automation", "rare", 600, "Dollar cost averaging automation engine"),
    ("mks_yield_farm", "Yield Farming Aggregator", "rare", 1300, "Aggregate best yield farming opportunities"),
    ("mks_perf_bond", "Performance Bond Pool", "rare", 850, "Insurance-backed performance bond system"),
    ("mks_cross_chain", "Cross-Chain Bridge", "rare", 1400, "Bridge assets across different blockchains"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("mks_hft_engine", "HFT Trading Engine", "epic", 6000, "High-frequency trading infrastructure"),
    ("mks_market_make", "Market Maker Bot", "epic", 8000, "Professional market-making algorithm"),
    ("mks_dark_pool", "Dark Pool Exchange", "epic", 10000, "Private exchange for institutional trades"),
    ("mks_deriv_lab", "Derivatives Laboratory", "epic", 7500, "Design and launch custom derivative products"),
    ("mks_ai_trader", "AI Trading Strategist", "epic", 9000, "Machine learning powered trading strategies"),
    ("mks_flash_loan", "Flash Loan Engine", "epic", 5500, "DeFi flash loan arbitrage system"),
    ("mks_synth_asset", "Synthetic Assets Factory", "epic", 11000, "Create and trade synthetic financial assets"),
    ("mks_tokenize", "Asset Tokenization", "epic", 12000, "Tokenize real-world assets on blockchain"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("mks_exchange", "Own Crypto Exchange", "legendary", 30000, "Launch your own cryptocurrency exchange"),
    ("mks_cbdc_node", "CBDC Node Operator", "legendary", 50000, "Central bank digital currency node operator"),
    ("mks_whale_net", "Whale Intelligence Network", "legendary", 65000, "Track and predict whale wallet movements"),
    ("mks_time_travel", "Temporal Market Predictor", "legendary", 80000, "Quantum prediction engine for market movements"),
]


# ===========================================================================
#  CATEGORY 5: PR & MEDIA  (38 cards)
# ===========================================================================
PR_CARDS: list[CardTuple] = [
    # ── Common (15) ───────────────────────────────────────────────────────
    ("pr_press_kit", "Press Kit", "common", 60, "Create a professional digital press kit"),
    ("pr_blog_post", "Press Blog Post", "common", 55, "Publish articles on major crypto news sites"),
    ("pr_twitter_mgr", "Twitter Account Manager", "common", 80, "Manage official Twitter/X presence"),
    ("pr_telegram_ch", "Telegram Channel", "common", 70, "Build and manage official Telegram community"),
    ("pr_discord_srv", "Discord Server", "common", 75, "Set up and moderate Discord community"),
    ("pr_reddit_mgr", "Reddit Community", "common", 90, "Build presence on Reddit crypto subreddits"),
    ("pr_medium_blog", "Medium Publication", "common", 65, "Publish thought leadership on Medium"),
    ("pr_linkedin", "LinkedIn Corporate Page", "common", 100, "Professional LinkedIn corporate marketing"),
    ("pr_newsletter_pr", "PR Newsletter", "common", 85, "Industry-focused PR newsletter distribution"),
    ("pr_infographic", "Infographic Designer", "common", 110, "Create viral infographics for data storytelling"),
    ("pr_podcast_host", "Podcast Hosting", "common", 120, "Launch and host an industry podcast"),
    ("pr_community_mg", "Community Manager", "common", 95, "Hire dedicated community management team"),
    ("pr_faq_center", "FAQ Knowledge Base", "common", 50, "Build comprehensive FAQ and help center"),
    ("pr_translation", "Content Translation", "common", 130, "Translate content into 20+ languages"),
    ("pr_chat_support", "Live Chat Support", "common", 140, "24/7 live chat customer support system"),
    # ── Rare (11) ─────────────────────────────────────────────────────────
    ("pr_forbes_feat", "Forbes Feature Article", "rare", 800, "Get featured in Forbes cryptocurrency section"),
    ("pr_cnbc_appear", "CNBC Appearance", "rare", 1200, "Book TV appearance on CNBC financial news"),
    ("pr_bloomberg", "Bloomberg Terminal Listing", "rare", 1500, "Get listed on Bloomberg financial terminal"),
    ("pr_crisis_mgr", "Crisis Management Team", "rare", 900, "Professional PR crisis management team"),
    ("pr_conference", "Crypto Conference Speaker", "rare", 700, "Secure speaking slots at major conferences"),
    ("pr_ama_session", "Reddit AMA Session", "rare", 600, "Host popular Ask Me Anything on Reddit"),
    ("pr_documentary", "Documentary Production", "rare", 1300, "Produce a documentary about the project"),
    ("pr_viral_meme", "Viral Meme Campaign", "rare", 650, "Professional meme marketing for viral reach"),
    ("pr_charity", "Charity Partnership", "rare", 1000, "Partner with international charities for PR"),
    ("pr_hackathon", "Hackathon Sponsor", "rare", 1100, "Sponsor developer hackathons worldwide"),
    ("pr_ambassador", "Global Ambassador Network", "rare", 1400, "Build a worldwide brand ambassador network"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("pr_super_bowl_pr", "Super Bowl PR Stunt", "epic", 5000, "Execute a Super Bowl level PR campaign"),
    ("pr_un_address", "UN Conference Address", "epic", 8000, "Address the United Nations on digital finance"),
    ("pr_netflix_doc", "Netflix Documentary Deal", "epic", 10000, "Produce a Netflix-level documentary series"),
    ("pr_nyt_frontpg", "NY Times Front Page", "epic", 7000, "Get New York Times front page coverage"),
    ("pr_ted_talk", "TED Talk Main Stage", "epic", 6000, "Deliver a TED Talk on the main stage"),
    ("pr_times_sq", "Times Square Billboard", "epic", 9000, "Rent Times Square digital billboard"),
    ("pr_oscar_gala", "Oscar Night Gala Sponsor", "epic", 12000, "Sponsor award ceremony gala events"),
    ("pr_space_ad", "Space Billboard", "epic", 15000, "Advertise on orbital space billboard"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("pr_world_tour", "Global Media World Tour", "legendary", 25000, "Tour every country with media coverage"),
    ("pr_moon_logo", "Moon Surface Logo", "legendary", 45000, "Project brand logo onto the Moon surface"),
    ("pr_ai_persona", "AI Celebrity Persona", "legendary", 60000, "Create an AI-powered celebrity brand ambassador"),
    ("pr_mindshare", "Global Mindshare Monopoly", "legendary", 75000, "Achieve 100% brand recognition worldwide"),
]


# ===========================================================================
#  CATEGORY 6: TEAM & HR  (38 cards)
# ===========================================================================
TEAM_CARDS: list[CardTuple] = [
    # ── Common (15) ───────────────────────────────────────────────────────
    ("hr_intern", "Hire Intern", "common", 50, "Recruit talented interns for the team"),
    ("hr_recruiter", "Recruiter Service", "common", 80, "Engage professional recruiters for hiring"),
    ("hr_office_space", "Office Space Lease", "common", 120, "Lease modern office space for the team"),
    ("hr_remote_tools", "Remote Work Tools", "common", 65, "Set up remote collaboration tools and software"),
    ("hr_slack_ws", "Slack Workspace", "common", 55, "Configure professional Slack workspace"),
    ("hr_jira_board", "Project Management Board", "common", 70, "Set up Jira/Trello project management"),
    ("hr_onboarding", "Onboarding Program", "common", 90, "Design comprehensive employee onboarding"),
    ("hr_training", "Staff Training Program", "common", 100, "Implement ongoing skill development training"),
    ("hr_perf_review", "Performance Reviews", "common", 75, "Establish quarterly performance review system"),
    ("hr_team_build", "Team Building Events", "common", 110, "Organize monthly team building activities"),
    ("hr_benefits", "Employee Benefits Package", "common", 130, "Design attractive employee benefits package"),
    ("hr_handbook", "Employee Handbook", "common", 60, "Write comprehensive employee handbook"),
    ("hr_payroll", "Payroll System", "common", 95, "Set up automated payroll processing"),
    ("hr_diversity", "Diversity Initiative", "common", 85, "Launch workplace diversity and inclusion program"),
    ("hr_wellness", "Wellness Program", "common", 105, "Employee mental health and wellness program"),
    # ── Rare (11) ─────────────────────────────────────────────────────────
    ("hr_sr_dev", "Senior Developer Hire", "rare", 800, "Recruit senior software developers"),
    ("hr_cto_hire", "CTO Search", "rare", 1500, "Executive search for Chief Technology Officer"),
    ("hr_designer", "Lead Designer Hire", "rare", 700, "Recruit a lead UI/UX designer"),
    ("hr_data_sci", "Data Scientist Hire", "rare", 1200, "Recruit experienced data scientists"),
    ("hr_devsecops", "DevSecOps Engineer", "rare", 1000, "Hire specialized DevSecOps engineers"),
    ("hr_hq_upgrade", "HQ Office Upgrade", "rare", 900, "Upgrade to premium headquarters office"),
    ("hr_equity_plan", "Employee Equity Plan", "rare", 650, "Design employee stock option program"),
    ("hr_global_team", "Global Remote Team", "rare", 1100, "Build distributed team across time zones"),
    ("hr_culture", "Company Culture Program", "rare", 600, "Develop strong company culture framework"),
    ("hr_retreat", "Company Retreat", "rare", 1300, "Organize luxury company retreat events"),
    ("hr_academy", "Internal Academy", "rare", 850, "Build internal training academy for employees"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("hr_ai_team", "AI Research Team", "epic", 5000, "Build a dedicated AI research team"),
    ("hr_campus", "Tech Campus", "epic", 8000, "Build a Silicon Valley style tech campus"),
    ("hr_phd_lab", "PhD Research Lab", "epic", 6500, "Establish in-house PhD research laboratory"),
    ("hr_genius_bar", "Genius Recruitment Bar", "epic", 7000, "Recruit top 0.1% talent globally"),
    ("hr_satellite", "Satellite Office Network", "epic", 9000, "Open satellite offices in 10 countries"),
    ("hr_innovation", "Innovation Hub", "epic", 10000, "Create dedicated innovation and R&D hub"),
    ("hr_crypto_pay", "Crypto Salary System", "epic", 5500, "Pay salaries in cryptocurrency"),
    ("hr_leadership", "Leadership Academy", "epic", 12000, "Executive leadership development program"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("hr_dream_team", "Dream Team Assembly", "legendary", 25000, "Assemble the ultimate all-star team"),
    ("hr_mars_office", "Mars Remote Office", "legendary", 40000, "Establish the first Mars remote office"),
    ("hr_clone_ceo", "CEO Clone Program", "legendary", 55000, "AI clone of CEO for 24/7 decision making"),
    ("hr_immortal", "Immortal Team Protocol", "legendary", 70000, "Digital consciousness preservation for key staff"),
]


# ===========================================================================
#  CATEGORY 7: SECURITY & INFRASTRUCTURE  (38 cards)
# ===========================================================================
SECURITY_CARDS: list[CardTuple] = [
    # ── Common (15) ───────────────────────────────────────────────────────
    ("sec_2fa", "Two-Factor Authentication", "common", 60, "Implement 2FA for all user accounts"),
    ("sec_ssl_cert", "SSL Certificate", "common", 50, "Install and manage SSL/TLS certificates"),
    ("sec_firewall", "Web Application Firewall", "common", 80, "Deploy WAF for API protection"),
    ("sec_ddos_basic", "Basic DDoS Protection", "common", 100, "Basic distributed denial of service protection"),
    ("sec_backup", "Automated Backups", "common", 75, "Set up automated daily database backups"),
    ("sec_logging", "Security Event Logging", "common", 65, "Implement comprehensive security event logs"),
    ("sec_vpn", "Team VPN Service", "common", 90, "Secure VPN for team remote access"),
    ("sec_password", "Password Policy Engine", "common", 55, "Enforce strong password policies"),
    ("sec_encryption", "Data Encryption Layer", "common", 120, "Encrypt sensitive data at rest and in transit"),
    ("sec_scan_basic", "Vulnerability Scanner", "common", 110, "Run automated vulnerability scans"),
    ("sec_rate_limit", "API Rate Limiting", "common", 70, "Implement rate limiting on all API endpoints"),
    ("sec_captcha", "CAPTCHA Integration", "common", 85, "Add CAPTCHA for bot prevention"),
    ("sec_ip_filter", "IP Whitelist System", "common", 95, "Implement IP-based access control lists"),
    ("sec_monitoring", "Uptime Monitoring", "common", 130, "24/7 server uptime and health monitoring"),
    ("sec_cold_wallet", "Cold Wallet Storage", "common", 150, "Set up cold wallet for secure fund storage"),
    # ── Rare (11) ─────────────────────────────────────────────────────────
    ("sec_pentest", "Penetration Testing", "rare", 800, "Professional penetration testing service"),
    ("sec_soc_team", "SOC Monitoring Team", "rare", 1200, "24/7 Security Operations Center team"),
    ("sec_hsm", "Hardware Security Module", "rare", 1000, "Deploy HSM for cryptographic key management"),
    ("sec_siem", "SIEM Platform", "rare", 900, "Security information and event management"),
    ("sec_zero_trust", "Zero Trust Architecture", "rare", 1100, "Implement zero trust security model"),
    ("sec_threat_intel", "Threat Intelligence Feed", "rare", 700, "Real-time cyber threat intelligence feeds"),
    ("sec_bug_bounty", "Bug Bounty Program", "rare", 600, "Launch public bug bounty for security"),
    ("sec_multisig", "Multi-Signature Vault", "rare", 850, "Multi-signature wallet for treasury security"),
    ("sec_incident", "Incident Response Plan", "rare", 650, "Professional cyber incident response plan"),
    ("sec_compliance", "SOC 2 Compliance", "rare", 1500, "Achieve SOC 2 Type II compliance"),
    ("sec_biometric", "Biometric Authentication", "rare", 1300, "Add biometric login for critical operations"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("sec_cyber_army", "Cyber Defense Army", "epic", 5000, "Build an elite cyber defense team"),
    ("sec_quantum_enc", "Quantum Encryption", "epic", 8000, "Post-quantum cryptography implementation"),
    ("sec_bunker", "Data Center Bunker", "epic", 10000, "Underground hardened data center facility"),
    ("sec_ai_defense", "AI-Powered Defense", "epic", 6500, "Machine learning powered threat detection"),
    ("sec_honeypot", "Honeypot Network", "epic", 5500, "Deploy decoy systems to trap attackers"),
    ("sec_satellite_bk", "Satellite Backup", "epic", 9000, "Space-based data backup infrastructure"),
    ("sec_dna_auth", "DNA Authentication", "epic", 12000, "DNA-based biometric authentication system"),
    ("sec_timelock", "Quantum Timelock Vault", "epic", 7000, "Time-locked quantum-secured vault system"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("sec_fortress", "Digital Fortress", "legendary", 25000, "Impenetrable multi-layer security fortress"),
    ("sec_alien_tech", "Alien Encryption Tech", "legendary", 45000, "Theoretical unbreakable encryption system"),
    ("sec_time_vault", "Temporal Security Vault", "legendary", 60000, "Time-displaced secure storage system"),
    ("sec_omniscient", "Omniscient Defense Grid", "legendary", 80000, "AI that predicts all attacks before they happen"),
]


# ===========================================================================
#  CATEGORY 8: SPECIALS & MEME  (40 cards)
# ===========================================================================
SPECIALS_CARDS: list[CardTuple] = [
    # ── Common (16) ───────────────────────────────────────────────────────
    ("spc_doge_react", "Doge Reactor", "common", 80, "Harness the power of much wow for token generation"),
    ("spc_pepe_farm", "Pepe Farm", "common", 90, "Cultivate rare Pepe memes for profit"),
    ("spc_moon_boot", "Moon Boots", "common", 70, "Equip moon boots for faster profit climbing"),
    ("spc_lambo_fund", "Lambo Fund", "common", 120, "Start saving for the inevitable Lamborghini"),
    ("spc_hodl_sign", "HODL Diamond Hands", "common", 65, "Display diamond hands commitment badge"),
    ("spc_btc_baby", "Baby Bitcoin", "common", 100, "Nurture a baby Bitcoin to full maturity"),
    ("spc_shib_army", "Shiba Army Badge", "common", 75, "Join the Shiba Inu army for bonus rewards"),
    ("spc_nft_monkey", "NFT Monkey Avatar", "common", 110, "Mint a unique monkey NFT for your profile"),
    ("spc_fomo_alarm", "FOMO Alarm Clock", "common", 55, "Never miss a pump with the FOMO alarm"),
    ("spc_whale_call", "Whale Detector", "common", 130, "Track whale wallet movements in real-time"),
    ("spc_rekt_shield", "REKT Shield", "common", 85, "Protection against getting REKT in dumps"),
    ("spc_bull_horn", "Bull Run Horn", "common", 95, "Sound the horn to signal bull market start"),
    ("spc_bear_trap", "Bear Trap Detector", "common", 105, "Detect fake dips before they trap bears"),
    ("spc_gem_finder", "Hidden Gem Finder", "common", 140, "Discover low-cap gem tokens early"),
    ("spc_airdrop_net", "Airdrop Hunting Net", "common", 150, "Automatically find and claim airdrops"),
    ("spc_meme_lord", "Meme Lord Title", "common", 60, "Earn the coveted Meme Lord title"),
    # ── Rare (12) ─────────────────────────────────────────────────────────
    ("spc_elon_tweet", "Elon Tweet Simulator", "rare", 800, "Simulate the market impact of celebrity tweets"),
    ("spc_rug_detect", "Rug Pull Detector", "rare", 700, "AI-powered scam and rug pull detection"),
    ("spc_defi_wiz", "DeFi Wizard Staff", "rare", 900, "Master DeFi protocols with wizard-level skill"),
    ("spc_satoshi_key", "Satoshi Key Fragment", "rare", 1200, "Discover a fragment of Satoshi's private key"),
    ("spc_matrix", "Matrix Code Viewer", "rare", 650, "See the crypto market as raw blockchain data"),
    ("spc_time_mach", "Time Machine Prototype", "rare", 1500, "Preview future price charts... maybe"),
    ("spc_rocket_fuel", "Rocket Fuel Reserve", "rare", 1000, "Extra fuel for when your tokens go to the moon"),
    ("spc_crystal_ball", "Crypto Crystal Ball", "rare", 850, "Mystical price prediction artifact"),
    ("spc_gold_pick", "Golden Pickaxe", "rare", 600, "Mine tokens at double speed with golden tools"),
    ("spc_dao_crown", "DAO Governance Crown", "rare", 1100, "Wield supreme governance voting power"),
    ("spc_metaverse_lnd", "Metaverse Land Plot", "rare", 1300, "Premium virtual real estate in the metaverse"),
    ("spc_cyber_cat", "Cyber Cat Companion", "rare", 750, "Adorable AI cat that helps earn tokens"),
    # ── Epic (8) ──────────────────────────────────────────────────────────
    ("spc_infinity", "Infinity Token Stone", "epic", 5000, "One of six legendary token infinity stones"),
    ("spc_dragon_egg", "Blockchain Dragon Egg", "epic", 7000, "Hatch a mythical dragon that guards your vault"),
    ("spc_excalibur", "Excalibur Validator", "epic", 8500, "Legendary sword that validates blocks instantly"),
    ("spc_phoenix", "Phoenix Rebirth Token", "epic", 6000, "Token that resurrects your portfolio from ashes"),
    ("spc_unicorn", "Unicorn Startup Card", "epic", 10000, "Turn any project into a billion-dollar unicorn"),
    ("spc_galaxy_map", "Galaxy Trading Map", "epic", 9000, "Navigate the crypto universe with star charts"),
    ("spc_alien_coin", "Alien Civilization Coin", "epic", 12000, "Currency used by an advanced alien civilization"),
    ("spc_black_hole", "Black Hole Compressor", "epic", 11000, "Compress infinite energy into finite tokens"),
    # ── Legendary (4) ─────────────────────────────────────────────────────
    ("spc_ark_react", "VTX Ark Reactor", "legendary", 30000, "Unlimited token generation power source"),
    ("spc_god_mode", "God Mode Activator", "legendary", 50000, "Activate god mode for maximum profit generation"),
    ("spc_universe", "Create Your Own Universe", "legendary", 65000, "Spawn an entire token universe under your control"),
    ("spc_singularity", "Profit Singularity", "legendary", 80000, "Achieve infinite profit-per-hour singularity"),
]


# ===========================================================================
#  COMBINED CATALOG
# ===========================================================================

ALL_CATEGORIES: dict[str, list[CardTuple]] = {
    "marketing":  MARKETING_CARDS,
    "development": DEVELOPMENT_CARDS,
    "legal":      LEGAL_CARDS,
    "markets":    MARKETS_CARDS,
    "pr":         PR_CARDS,
    "team":       TEAM_CARDS,
    "security":   SECURITY_CARDS,
    "specials":   SPECIALS_CARDS,
}


CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    "marketing":  "Marketing",
    "development": "Development",
    "legal":      "Legal & Compliance",
    "markets":    "Markets & Trading",
    "pr":         "PR & Media",
    "team":       "Team & HR",
    "security":   "Security & Infra",
    "specials":   "Specials & Meme",
}


def total_card_count() -> int:
    """Return the total number of cards in the catalog."""
    return sum(len(cards) for cards in ALL_CATEGORIES.values())
