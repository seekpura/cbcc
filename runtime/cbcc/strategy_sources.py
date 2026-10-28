from __future__ import annotations
from pathlib import Path
from typing import Any
import json, hashlib, re


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def _sha(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def _read(path:Path)->str:
    try: return path.read_text(encoding='utf-8')
    except Exception: return ''


def _authority_excerpt(text:str, max_chars:int=5000)->str:
    """Keep high-value Markdown authority content instead of only a file hash."""
    if not text: return ''
    lines=[]
    for line in text.splitlines():
        s=line.strip()
        if not s: continue
        if s.startswith('#') or s.startswith('- ') or s.startswith('* ') or re.match(r'^\d+[.)]\s',s) or 'WHY' in s.upper() or 'MUST' in s.upper() or '原则' in s or '必须' in s or '不要' in s:
            lines.append(s)
        if sum(len(x)+1 for x in lines)>=max_chars: break
    if not lines: return text[:max_chars]
    return '\n'.join(lines)[:max_chars]


def _active_domains(request:dict[str,Any])->set[str]:
    domains={'truth','product_value','positioning','culture','visual','content','asset','strategy'}
    if (request.get('target') or {}).get('category') or (request.get('product') or {}).get('category') or (request.get('product') or {}).get('product_type'): domains.add('category_specificity')
    if request.get('market_rows') or request.get('market_file') or request.get('market_keyword_rows') or request.get('market_review_rows') or request.get('competitor_listing_rows') or request.get('market_competitor_listing_rows'): domains.add('market')
    if 'market' in domains and 'category_specificity' in domains: domains.add('evidence_reconciliation')
    if 'market' in domains: domains.update({'evidence_quality_weighting','market_evidence_fit'})
    if request.get('market_source_records') or request.get('market_research_scope') or request.get('market_research_as_of'): domains.add('research_quality')
    if request.get('market_research_ingestion') or 'market' in domains: domains.add('research_ingestion')
    if request.get('research_source_adapters'): domains.update({'source_adapters','adapter_family_cursor','research_ingestion','research_quality','market'})
    if request.get('competitor_listing_rows') or request.get('market_competitor_listing_rows'): domains.add('competitor_intelligence')
    if request.get('offer_economics'): domains.update({'economics','offer','sku'})
    if any((request.get('offer_economics') or {}).get(k) for k in ['promo_response_rows','bundle_affinity_rows','repeat_cycle_rows','replacement_cycle_rows']) or any(request.get(k) for k in ['promo_response_rows','bundle_affinity_rows','repeat_cycle_rows']): domains.add('offer_response_evidence')
    if len(((request.get('offer_economics') or {}).get('scenarios') or [])) > 1 or len(request.get('skus') or []) > 1: domains.add('portfolio')
    econ=request.get('offer_economics') or {}
    if any(econ.get(k) for k in ['behavior_rows','portfolio_behavior_rows','pair_behavior_rows','portfolio_pair_rows','cohort_rows','portfolio_cohort_rows','incrementality_rows','portfolio_incrementality_rows','switch_rows','portfolio_switch_rows','holdout_rows','portfolio_holdout_rows']) or any(request.get(k) for k in ['portfolio_behavior_rows','portfolio_pair_rows','portfolio_cohort_rows','portfolio_incrementality_rows','portfolio_switch_rows','portfolio_holdout_rows']): domains.update({'portfolio_behavior','measurement','portfolio_incrementality'})
    if request.get('listing_input'): domains.update({'listing','search'})
    target=request.get('target') or {}; listing_fields=((request.get('listing_input') or {}).get('fields') or {})
    if len(target.get('visible_copy_locales') or [])>1 or listing_fields.get('_localized_copy'): domains.add('localization')
    if listing_fields.get('_localized_copy') or listing_fields.get('_localized_copy_reviews') or listing_fields.get('_localized_copy_history'): domains.add('final_copy')
    if listing_fields.get('_localized_copy_history'): domains.add('copy_iteration')
    if listing_fields.get('_terminology_memory') or (request.get('listing_input') or {}).get('terminology_memory'): domains.update({'terminology_memory','localization','final_copy'})
    if (request.get('listing_input') or {}).get('host_authoring_responses') or request.get('host_copy_authoring_responses'): domains.update({'host_copy_authoring','copy_iteration','final_copy'})
    if str(target.get('platform_family') or '').casefold() in {'tiktok_shop','shopee','amazon','shopify','dtc'}: domains.add('platform_native')
    if request.get('ad_rows') or request.get('ad_analysis'): domains.update({'ads','measurement','revision_integration'})
    if request.get('feedback_rows'): domains.update({'feedback','measurement','revision','revision_integration'})
    if request.get('experiment'):
        domains.update({'experiment','experiment_design','measurement'})
        ex=request.get('experiment') or {}
        if any(ex.get(k) for k in ['cluster_design','geo_design','cuped','sequential']): domains.add('advanced_causal')
    if request.get('photography_contract') or request.get('visual_strategy') or request.get('cmf'): domains.update({'photography','cmf','material_lighting','prelight_color'})
    if str(target.get('platform_family') or '').casefold() in {'tiktok_shop','shopee','amazon','shopify','dtc'} or request.get('platform_content_targets'): domains.add('surface_production')
    if request.get('production_run') and request.get('compile_assets'): domains.update({'production_binding','production_learning'})
    # Derived market domains must be resolved after every input path (including Source Adapters)
    # has had a chance to activate `market`. Otherwise adapter-only projects consume market data
    # but miss the Evidence Quality / Category Reconciliation authorities.
    if 'market' in domains:
        domains.update({'evidence_quality_weighting','market_evidence_fit'})
        if 'category_specificity' in domains: domains.add('evidence_reconciliation')
    return domains


def compile_strategy_reasoning_context(request: dict[str, Any]) -> dict[str, Any]:
    """Compile professional reasoning authorities actually relevant to the project.

    Deterministic calculators remain the fact/math authority. This context now includes selected
    authority excerpts plus section bindings, so downstream strategy authoring consumes more than
    registry metadata/hashes.
    """
    root=_root(); domains=_active_domains(request)
    preg=_load_json(root/'prompts/registry.json',{'prompts':[]}); kreg=_load_json(root/'knowledge/registry.json',{'documents':[]}); onto=_load_json(root/'ontology/commerce_ontology.json',{})

    wanted_prompts={'PROMPT-MASTER-STRATEGY','PROMPT-SKU-OFFER','PROMPT-POSITIONING','PROMPT-VISUAL-PHOTO','PROMPT-PLATFORM-MATRIX','PROMPT-ASSET-CURATION','PROMPT-CULTURE','PROMPT-CREATIVE-SURFACE-CANONICAL'}
    if 'market' in domains: wanted_prompts.add('PROMPT-MARKET-STRATEGY')
    if 'listing' in domains: wanted_prompts.add('PROMPT-LISTING')
    if 'measurement' in domains: wanted_prompts.add('PROMPT-MEASUREMENT')
    if request.get('claims'): wanted_prompts.add('PROMPT-TRUTH-VALUE')
    if 'economics' in domains: wanted_prompts.add('PROMPT-ECONOMICS')
    if 'feedback' in domains: wanted_prompts.add('PROMPT-FEEDBACK')
    if 'ads' in domains: wanted_prompts.add('PROMPT-ADS')
    if 'competitor_intelligence' in domains: wanted_prompts.add('PROMPT-COMPETITOR-INTEL')
    if 'portfolio' in domains: wanted_prompts.add('PROMPT-PORTFOLIO-STRATEGY')
    if 'localization' in domains: wanted_prompts.add('PROMPT-TRANScreation-AUTHORING')
    if 'research_quality' in domains or 'market' in domains: wanted_prompts.add('PROMPT-RESEARCH-QUALITY')
    if 'portfolio_behavior' in domains: wanted_prompts.add('PROMPT-PORTFOLIO-BEHAVIOR')
    if 'final_copy' in domains: wanted_prompts.add('PROMPT-FINAL-COPY')
    if 'platform_native' in domains: wanted_prompts.add('PROMPT-PLATFORM-NATIVE-SYSTEMS')
    if 'research_ingestion' in domains: wanted_prompts.add('PROMPT-EVIDENCE-INGESTION')
    if 'portfolio_incrementality' in domains: wanted_prompts.add('PROMPT-MARGINAL-CONTRIBUTION')
    if 'copy_iteration' in domains: wanted_prompts.add('PROMPT-COPY-ITERATION')
    if 'photography' in domains: wanted_prompts.add('PROMPT-ASSET-PHOTO-WHY')
    if 'source_adapters' in domains: wanted_prompts.add('PROMPT-SOURCE-ADAPTERS')
    if 'experiment_design' in domains: wanted_prompts.add('PROMPT-CAUSAL-EXPERIMENT')
    if 'host_copy_authoring' in domains: wanted_prompts.add('PROMPT-HOST-COPY')
    if 'surface_production' in domains: wanted_prompts.add('PROMPT-SURFACE-PRODUCTION')
    if 'material_lighting' in domains: wanted_prompts.add('PROMPT-CMF-LIGHTING')
    if 'adapter_family_cursor' in domains: wanted_prompts.add('PROMPT-ADAPTER-CURSOR')
    if 'advanced_causal' in domains: wanted_prompts.add('PROMPT-ADVANCED-CAUSAL')
    if 'terminology_memory' in domains: wanted_prompts.add('PROMPT-TERMINOLOGY-MEMORY')
    if 'production_binding' in domains: wanted_prompts.add('PROMPT-PRODUCTION-BINDING')
    if 'production_learning' in domains: wanted_prompts.add('PROMPT-PRODUCTION-LEARNING-LOOP')
    if 'prelight_color' in domains: wanted_prompts.add('PROMPT-PRELIGHT-COLOR')
    if 'category_specificity' in domains:
        wanted_prompts.update({'PROMPT-MULTICATEGORY-SPECIFICITY','PROMPT-CATEGORY-COMMERCE-DEPTH'})
    if 'evidence_reconciliation' in domains: wanted_prompts.add('PROMPT-CATEGORY-EVIDENCE-RECONCILIATION')
    if 'offer_response_evidence' in domains: wanted_prompts.add('PROMPT-OFFER-RESPONSE-EVIDENCE')
    if 'evidence_quality_weighting' in domains: wanted_prompts.add('PROMPT-EVIDENCE-QUALITY-WEIGHTING')
    if 'revision_integration' in domains or 'market_evidence_fit' in domains: wanted_prompts.add('PROMPT-REVISION-INTEGRATION')

    prompts=[]
    for row in preg.get('prompts',[]):
        if row.get('id') not in wanted_prompts: continue
        path=(root/'prompts'/row['path']).resolve()
        text=_read(path)
        prompts.append({**row,'sha256':_sha(path) if path.exists() else None,'available':path.exists(),'authority_excerpt':_authority_excerpt(text),'selection_reason':'Activated by current project domains or required core strategy authoring.'})

    wanted_knowledge={'KNOW-README','KNOW-CONTENT_ASSETS','KNOW-CREATIVE_PHOTOGRAPHY','KNOW-CULTURE','KNOW-POSITIONING','KNOW-PRODUCT_VALUE','KNOW-CREATIVE-SURFACE-CANONICAL'}
    if 'market' in domains: wanted_knowledge.add('KNOW-MARKET_STRATEGY')
    if 'measurement' in domains: wanted_knowledge.add('KNOW-MEASUREMENT')
    if 'competitor_intelligence' in domains: wanted_knowledge.add('KNOW-COMPETITOR-INTEL')
    if 'portfolio' in domains: wanted_knowledge.add('KNOW-SKU-PORTFOLIO')
    if 'localization' in domains: wanted_knowledge.add('KNOW-TRANScreation')
    if 'research_quality' in domains or 'market' in domains: wanted_knowledge.add('KNOW-RESEARCH-QUALITY')
    if 'portfolio_behavior' in domains: wanted_knowledge.add('KNOW-PORTFOLIO-BEHAVIOR')
    if 'final_copy' in domains: wanted_knowledge.add('KNOW-FINAL-COPY')
    if 'platform_native' in domains: wanted_knowledge.add('KNOW-PLATFORM-NATIVE-SYSTEMS')
    if 'research_ingestion' in domains: wanted_knowledge.add('KNOW-EVIDENCE-INGESTION')
    if 'portfolio_incrementality' in domains: wanted_knowledge.add('KNOW-MARGINAL-CONTRIBUTION')
    if 'copy_iteration' in domains: wanted_knowledge.add('KNOW-COPY-ITERATION')
    if 'photography' in domains: wanted_knowledge.add('KNOW-ASSET-PHOTO-WHY')
    if 'source_adapters' in domains: wanted_knowledge.add('KNOW-SOURCE-ADAPTERS')
    if 'experiment_design' in domains: wanted_knowledge.add('KNOW-CAUSAL-EXPERIMENT')
    if 'host_copy_authoring' in domains: wanted_knowledge.add('KNOW-HOST-COPY')
    if 'surface_production' in domains: wanted_knowledge.add('KNOW-SURFACE-PRODUCTION')
    if 'material_lighting' in domains: wanted_knowledge.add('KNOW-CMF-LIGHTING')
    if 'adapter_family_cursor' in domains: wanted_knowledge.add('KNOW-ADAPTER-CURSOR')
    if 'advanced_causal' in domains: wanted_knowledge.add('KNOW-ADVANCED-CAUSAL')
    if 'terminology_memory' in domains: wanted_knowledge.add('KNOW-TERMINOLOGY-MEMORY')
    if 'production_binding' in domains: wanted_knowledge.add('KNOW-PRODUCTION-BINDING')
    if 'production_learning' in domains: wanted_knowledge.add('KNOW-PRODUCTION-LEARNING-LOOP')
    if 'prelight_color' in domains: wanted_knowledge.add('KNOW-PRELIGHT-COLOR')
    if 'category_specificity' in domains:
        wanted_knowledge.update({'KNOW-MULTICATEGORY-SPECIFICITY','KNOW-CATEGORY-COMMERCE-DEPTH'})
    if 'evidence_reconciliation' in domains: wanted_knowledge.add('KNOW-CATEGORY-EVIDENCE-RECONCILIATION')
    if 'offer_response_evidence' in domains: wanted_knowledge.add('KNOW-OFFER-RESPONSE-EVIDENCE')
    if 'evidence_quality_weighting' in domains: wanted_knowledge.add('KNOW-EVIDENCE-QUALITY-WEIGHTING')
    if 'revision_integration' in domains or 'market_evidence_fit' in domains: wanted_knowledge.add('KNOW-REVISION-INTEGRATION')
    strategy_depth_paths={'professional_strategy_authoring.md','asset_portfolio_curation.md','market_to_strategy.md','listing_decision_system.md','visual_why_framework.md'}
    knowledge=[]
    for row in kreg.get('documents',[]):
        rid=row.get('id'); include=(rid in wanted_knowledge) or row.get('path') in strategy_depth_paths
        if not include: continue
        path=root/'knowledge'/row['path']; text=_read(path)
        knowledge.append({**row,'sha256':_sha(path) if path.exists() else None,'available':path.exists(),'authority_excerpt':_authority_excerpt(text),'selection_reason':'Core handbook or domain activated by current project inputs.'})

    relevant_entities=['ProductTruth','Fact','Claim','Evidence','SKU','SKUFamily','Offer','Variant','Bundle','Market','Competitor','PriceBand','Configuration','Audience','CultureContext','TargetContext','Positioning','ValueProposition','Message','MessageHierarchy','KeywordIntent','SearchDemand','CompetitorCluster','MarketOpportunity','ListingArchitecture','Objection','DecisionJob','SurfaceNeed','BusinessHypothesis','ContentObject','AssetPortfolio','Asset','PhotographyContract','CMFContract','Metric','PerformanceDiagnosis','FeedbackIssue','Experiment','RevisionAction','UnitEconomics','SharedGrowthBudget','OfferRoom','TranscreationContract','IncrementalityEvidence','CompetitorListingObservation','CustomerVoiceTheme','CannibalizationHypothesis','TradeUpStep','LifecycleOfferRole','LocaleAuthoringTask','ResearchDataset','ResearchSourceQuality','BehaviorObservation','CohortObservation','PortfolioIncrementalityEvidence','FinalCopy','CopyReview','NativeAuthoringSystem','EvidenceFingerprint','SourceVersion','SourceLineage','SwitchObservation','HoldoutExperiment','MarginalContribution','CopyVersion','CopyRevisionTask','SurfaceAuthoringContract','AssetPhotographyReasoning','SourceAdapter','RefreshState','ResearchChangeSet','SemanticDuplicateCandidate','ExperimentDesign','PowerPlan','BalanceDiagnostic','InterferenceRisk','HostAuthoringResponse','SurfaceProductionContract','MaterialLightingProfile','ShotLightingReasoning','AdapterCheckpoint','CursorWindow','ClusterDesign','GeoExperiment','CUPEDPlan','SequentialMonitoringPlan','TerminologyMemory','TerminologyAudit','ProductionContractBinding','PrelightPlan','LightingDiagram','ExposureRatioPlan','PolarizationPlan','ColorConsistencyPlan','CategoryDecisionProfile','DecisionIntent','CategoryPhotographyPlan','CategoryCommerceProfile','ObjectionPriority','ProofHierarchy','OfferArchitecture','ContentCadence','EvidencePriority','CategoryEvidenceReconciliation','ProofEvidenceCondition','PromoResponseObservation','BundleAffinityObservation','RepeatReplacementCycle','PlatformCategoryIntersection','EvidenceQualityWeight','MarketEvidenceFitContract','StrategyRevisionRoute','CapabilityIntegrationMap','ProductVisualIntelligence','FoundationAsset','CreativeOpportunity','CreativeOpportunityUniverse','DirectionSynthesis','CreativeDirection','CreativeCouncil','CreativeAnchor','SurfaceArchitecture','InformationAssetization','ProductPresence','SurfaceCopyBudget','VisualExpressionVariant','DesignCard','CanonicalPromptContract','RendererRecipe','PaidCampaignArchitecture','CreatorVideoPlan','StrategyDecision']
    entities=[e for e in onto.get('entities',[]) if e in relevant_entities]
    relations=[r for r in onto.get('relations',[]) if r.get('from') in entities and r.get('to') in entities]
    constraints=[c for c in onto.get('constraints',[]) if c.get('scope') in {'strategy','claim','positioning','listing','asset','asset-package','photography','culture','measurement','experiment','local-revision'}]
    processes=[p for p in onto.get('processes',[]) if p.get('id') in {'P-STRATEGY','P-ASSET','P-LEARN'}]

    prompt_ids=[x.get('id') for x in prompts]; knowledge_ids=[x.get('id') or x.get('path') for x in knowledge]
    bindings={
        '01_information_completeness_assumptions_decisions':['PROMPT-MASTER-STRATEGY','KNOW-PROFESSIONAL-STRATEGY-AUTHORING'],
        '02_product_truth_value_ladder':['PROMPT-TRUTH-VALUE','KNOW-PRODUCT_VALUE'],
        '03_platform_region_audience_culture_insight':['PROMPT-EVIDENCE-QUALITY-WEIGHTING','PROMPT-REVISION-INTEGRATION','PROMPT-ADAPTER-CURSOR','PROMPT-SOURCE-ADAPTERS','PROMPT-EVIDENCE-INGESTION','PROMPT-MARKET-STRATEGY','PROMPT-COMPETITOR-INTEL','PROMPT-RESEARCH-QUALITY','PROMPT-CULTURE','KNOW-SOURCE-ADAPTERS','KNOW-EVIDENCE-INGESTION','KNOW-MARKET_STRATEGY','KNOW-COMPETITOR-INTEL','KNOW-RESEARCH-QUALITY','KNOW-EVIDENCE-QUALITY-WEIGHTING','KNOW-REVISION-INTEGRATION','KNOW-CULTURE','KNOW-MARKET-TO-STRATEGY'],
        '04_marketing_core_strategy':['PROMPT-EVIDENCE-QUALITY-WEIGHTING','PROMPT-CATEGORY-EVIDENCE-RECONCILIATION','PROMPT-OFFER-RESPONSE-EVIDENCE','PROMPT-CATEGORY-COMMERCE-DEPTH','PROMPT-MULTICATEGORY-SPECIFICITY','PROMPT-TERMINOLOGY-MEMORY','PROMPT-HOST-COPY','PROMPT-SKU-OFFER','PROMPT-MARGINAL-CONTRIBUTION','PROMPT-COPY-ITERATION','PROMPT-PORTFOLIO-STRATEGY','PROMPT-PORTFOLIO-BEHAVIOR','PROMPT-POSITIONING','PROMPT-LISTING','PROMPT-TRANScreation-AUTHORING','PROMPT-FINAL-COPY','KNOW-HOST-COPY','KNOW-MARGINAL-CONTRIBUTION','KNOW-COPY-ITERATION','KNOW-SKU-PORTFOLIO','KNOW-PORTFOLIO-BEHAVIOR','KNOW-POSITIONING','KNOW-TRANScreation','KNOW-FINAL-COPY','KNOW-EVIDENCE-QUALITY-WEIGHTING','KNOW-CATEGORY-EVIDENCE-RECONCILIATION','KNOW-OFFER-RESPONSE-EVIDENCE','KNOW-CATEGORY-COMMERCE-DEPTH','KNOW-MULTICATEGORY-SPECIFICITY','KNOW-LISTING-DECISION-SYSTEM'],
        '05_visual_photography_strategy':['PROMPT-CREATIVE-SURFACE-CANONICAL','KNOW-CREATIVE-SURFACE-CANONICAL','PROMPT-MULTICATEGORY-SPECIFICITY','PROMPT-PRELIGHT-COLOR','PROMPT-CMF-LIGHTING','PROMPT-VISUAL-PHOTO','PROMPT-ASSET-PHOTO-WHY','KNOW-CMF-LIGHTING','KNOW-ASSET-PHOTO-WHY','KNOW-CREATIVE_PHOTOGRAPHY','KNOW-MULTICATEGORY-SPECIFICITY','KNOW-VISUAL-WHY-FRAMEWORK','KNOW-ASSET-PORTFOLIO-CURATION'],
        '06_platform_content_matrix':['PROMPT-CREATIVE-SURFACE-CANONICAL','KNOW-CREATIVE-SURFACE-CANONICAL','PROMPT-CATEGORY-EVIDENCE-RECONCILIATION','PROMPT-CATEGORY-COMMERCE-DEPTH','PROMPT-MULTICATEGORY-SPECIFICITY','PROMPT-PRODUCTION-BINDING','PROMPT-SURFACE-PRODUCTION','PROMPT-PLATFORM-MATRIX','PROMPT-PLATFORM-NATIVE-SYSTEMS','PROMPT-TRANScreation-AUTHORING','KNOW-SURFACE-PRODUCTION','KNOW-CONTENT_ASSETS','KNOW-PLATFORM-NATIVE-SYSTEMS','KNOW-TRANScreation','KNOW-CATEGORY-EVIDENCE-RECONCILIATION','KNOW-CATEGORY-COMMERCE-DEPTH','KNOW-MULTICATEGORY-SPECIFICITY'],
        '07_race_execution_table':['PROMPT-MASTER-STRATEGY','PROMPT-PLATFORM-MATRIX'],
        '08_culture_adaptation_checklist':['PROMPT-CULTURE','KNOW-CULTURE'],
        '09_risk_measurement_priority_next_steps':['PROMPT-PRODUCTION-LEARNING-LOOP','KNOW-PRODUCTION-LEARNING-LOOP','PROMPT-REVISION-INTEGRATION','PROMPT-ADVANCED-CAUSAL','PROMPT-CAUSAL-EXPERIMENT','PROMPT-MEASUREMENT','PROMPT-PORTFOLIO-BEHAVIOR','PROMPT-ADS','PROMPT-FEEDBACK','KNOW-REVISION-INTEGRATION','KNOW-CAUSAL-EXPERIMENT','KNOW-MEASUREMENT','KNOW-PORTFOLIO-BEHAVIOR'],
    }
    bindings={k:[x for x in v if x in prompt_ids or x in knowledge_ids] for k,v in bindings.items()}

    return {
        'status':'STRATEGY_REASONING_CONTEXT_COMPILED','version':'0.6.7-semantic-workspaces','active_domains':sorted(domains),
        'purpose':'Project-specific selection and content-level consumption of professional reasoning authorities. Deterministic truth/calculations remain separate authorities.',
        'selected_prompts':prompts,'selected_knowledge':knowledge,
        'authority_bindings':bindings,
        'ontology':{'version':onto.get('version'),'entities':entities,'relations':relations,'constraints':constraints,'processes':processes},
        'annotation_contract':{
            'output_key':'strategy_annotations','principle':'Add interpretation/WHY/execution only; do not replace Product Truth or deterministic calculations.',
            'decision_contract':'WHAT → WHY → EVIDENCE → CONSUMER → PLATFORM → CULTURE → BUSINESS → EXECUTION → MEASUREMENT',
            'runtime_consumption':'Strategy Authority records which selected prompt/knowledge authorities bind to each section; host/model annotations deepen those exact sections.'
        },
    }
