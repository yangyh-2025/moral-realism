# Peer Review Plan: WWI Historical Analysis for Moral-ABM (1913-1925)

**Plan date:** 2026-06-13
**Plan status:** Ready for execution
**Review architecture:** Specialized-parallel (4 reviewers + 1 synthesizer)

---

## 1. Document Corpus Map

### Primary review target

| Document | Path | Scope |
|----------|------|-------|
| **WWI_Historical_Analysis_1913_1925.md** | `docs/WWI_Historical_Analysis_1913_1925.md` | Main synthesis: 8 leader groups, scholarly debates (Versailles, Belgium neutrality, secret treaties, decision psychology, self-determination), ABM parameter quantification (~452 lines, ~25,000 words) |

### Supplemental research corpus (to be reviewed alongside primary document)

**Leader-specific research reports:**

| Document | Path | Leader(s) | Depth |
|----------|------|-----------|-------|
| British Leadership | `docs/research/british_leadership_WWI_research.md` | Asquith, Lloyd George | Full monograph (~200+ lines) |
| Nicholas II | `docs/research/Nicholas_II_Leadership_Report.md` | Nicholas II | Full monograph (~200+ lines) |
| Nicholas II (CN) | `docs/research/Nicholas_II_Leadership_Report_CN.md` | Nicholas II | Chinese translation (reference only; EN version is canonical) |
| Franz Joseph | `docs/franz_joseph_july_crisis_research.md` | Franz Joseph I | Full monograph (~200+ lines) |
| Lenin | `docs/research/Lenin_Research_Report.md` | Lenin | Full monograph (~200+ lines) |
| Lenin (CN) | `docs/research/Lenin_Research_Report_CN.md` | Lenin | Chinese translation (reference only; EN version is canonical) |
| Rathenau/Stresemann | `docs/research/rathenau_stresemann_research.md` | Rathenau, Stresemann | Full monograph (~200+ lines) |
| Weimar Foreign Policy | `docs/weimar_foreign_policy_research.md` | Ebert, Stresemann | Full monograph (~200+ lines) |
| Ebert Speeches | `docs/research/Ebert_speeches_source_verification.md` | Ebert | Source verification |
| Wilson | `docs/research/wilson_moral_internationalism_research.md` | Wilson | Full monograph |
| Clemenceau/Briand | `docs/research/clemenceau_briand_research.md` | Clemenceau, Briand | Full monograph |
| UK text dump | `docs/UK_Asquith_LloydGeorge_leadership_research.txt` | Asquith, Lloyd George | Raw research notes |
| Ebert text dump | `docs/Ebert.txt` | Ebert | Raw research notes |

**Thematic research reports:**

| Document | Path | Topic |
|----------|------|-------|
| Peace Movements | `docs/research/peace_movements_research.md` | Second International, anti-war movements |
| Arthur Henderson | `docs/research/arthur_henderson_research.md` | British Labour internationalism |
| Stalin Foreign Policy | `docs/research/stalin_foreign_policy_research.md` | Soviet foreign policy |
| Churchill | `docs/research/churchill_foreign_policy_research.md` | Churchill |
| Mussolini | `docs/research/mussolini_foreign_policy_research.md` | Mussolini |

**Simulation design / ABM documents:**

| Document | Path | Content |
|----------|------|---------|
| Simulation Design | `docs/simulation_design/仿真设计说明.md` | Core ABM design specification |
| AH Scholarly Analysis | `docs/simulation_design/AH_1914_decision_making_scholarly_analysis.md` | Austria-Hungary deep dive |
| Interim 1914 Report | `docs/simulation_design/interim_report_1914_analysis.md` | Serbia + codebase + IR theory analysis |
| Sovereignty Norms | `docs/simulation_design/sovereignty_norms_evolution_1914_contemporary.md` | Sovereignty norms 1914-present |
| Synthesis/Improvements | `docs/simulation_design/synthesis_ABM_design_improvements.md` | Cross-reference of all analysis vs. ABM design |
| Cross-Reference | `docs/research/cross_reference_scene1_vs_research.md` | Scene 1 ground truth vs. historical research |

**History/scene documents:**

| Document | Path | Content |
|----------|------|---------|
| Scene History | `docs/scene_history/三场景历史背景说明.md` | Three-scenario historical context |
| Model Validation | `docs/model_validation/模型校验章节.md` | F1 validation methodology and results |

**Other relevant docs:**

| Document | Path |
|----------|------|
| Program Design | `docs/program_design/程序设计说明.md` |
| Technical Docs | `docs/technical_doc/技术文档.md` |
| Prompt Design | `docs/prompt_design/智能体提示词设计说明.md` |
| ID22/25/26 Reports | `docs/id22_report/`, `docs/id25_report/`, `docs/id26_report/` |

**Total corpus:** 30+ documents, estimated ~150,000-200,000 words of research material.

---

## 2. Review Architecture: Specialized-Parallel

### Rationale

The review dimensions are orthogonal -- historical fact-checking, ABM parameter adequacy, internal consistency, and coverage gaps are independent analytical tasks. Each requires different expertise and different subsets of the corpus. Running them in parallel maximizes depth-per-dimension while minimizing elapsed time.

A single agent cannot hold the full corpus in working memory (~200K words). Specialization with bounded document assignments solves this.

A 5th synthesis agent integrates findings, resolves cross-dimensional conflicts (e.g., a fact correction may affect a parameter recommendation), and produces the unified review report.

### Architecture diagram

```
Phase 1 (Parallel): 4 specialized reviewers
    R1: Historical Accuracy  ──┐
    R2: ABM Modeling Adequacy ──┼── Each reads assigned document subset
    R3: Internal Consistency  ──┤   with dimension-specific criteria
    R4: Coverage Gaps         ──┘

Phase 2 (Sequential):
    R5: Lead Synthesizer ── reads all 4 reviews → unified report
```

### Agent model selection

| Agent | Model | Rationale |
|-------|-------|-----------|
| R1 Historical Accuracy | Opus | Requires nuanced judgment of historiographical debates, source evaluation |
| R2 ABM Adequacy | Opus | Requires cross-document reasoning between historical claims and ABM parameters |
| R3 Internal Consistency | Sonnet | Pattern-matching contradictions across sections; Sonnet efficient for this |
| R4 Coverage Gaps | Sonnet | Systematic enumeration of missing elements; Sonnet sufficient |
| R5 Lead Synthesizer | Opus | Requires synthesis, prioritization, and resolution of cross-dimensional conflicts |

---

## 3. Review Dimension Specifications

### R1: Historical Accuracy Checker

**Document assignment:** Primary document `WWI_Historical_Analysis_1913_1925.md` + ALL leader-specific research reports (British Leadership, Nicholas II [EN canonical], Franz Joseph, Lenin [EN canonical], Rathenau/Stresemann, Weimar Foreign Policy, Wilson, Clemenceau/Briand) + Ebert speeches source verification + source verification summary. Chinese translations of Nicholas II and Lenin reports are reference-only; reviewers should use the EN versions as authoritative.

**Review criteria:**
1. **Factual errors:** Identify any claim in the primary document that contradicts well-established historiography. Flag specific line references.
2. **Anachronisms:** Identify concepts, terms, or frameworks applied to 1913-1925 actors that post-date their era (e.g., using post-WWII international law concepts to judge 1914 decisions without noting the anachronism).
3. **Missing context:** Identify claims that are technically true but misleading without additional context (e.g., citing a statistic without noting scholarly debate about its validity).
4. **Source quality:** Evaluate whether cited sources are (a) peer-reviewed academic works, (b) primary sources used appropriately, (c) potentially outdated or superseded by newer scholarship.
5. **Quotation accuracy:** For any claim presented as a direct quotation, flag whether the surrounding context in the source supports the quoted interpretation.
6. **Cross-check with supplemental research:** For each leader section, compare the primary document's claims against the corresponding deep-dive research report. Flag discrepancies where the deep-dive report contains materially different facts, interpretations, or sources not reflected in the primary document.
7. **Historiographical awareness:** Flag places where the primary document presents one scholarly interpretation as settled fact when there is active debate (e.g., the "sleepwalkers" vs. "conscious choice" debate on war origins).
8. **Wilson coverage note:** Wilson has a dedicated deep-dive research report (`wilson_moral_internationalism_research.md`) but appears only peripherally in the primary document (Parts 2E and 3). R1 should note whether the primary document accurately represents Wilson's role where it does mention him, and flag whether the Wilson deep-dive contains significant evidence or interpretations that the primary document omits.

**Output format:** Structured findings list with severity ratings:
- **CRITICAL:** Factually wrong claim that would undermine the paper's credibility if published
- **HIGH:** Misleading or incomplete claim that requires substantial revision
- **MEDIUM:** Minor factual imprecision or outdated source
- **LOW:** Clarification suggested but no factual error

### R2: ABM Modeling Adequacy Checker

**Document assignment:** Primary document (Parts 2-3, especially the ABM parameter sections) + ALL simulation design documents (仿真设计说明, AH_1914 analysis, interim_report, sovereignty_norms, synthesis_ABM_design_improvements) + model validation chapter + scene history

**Review criteria:**
1. **Parameter justification:** For each weight/parameter in the primary document's ABM sections (motivation weights matrix, sovereignty severity grades, alliance quantification, Lenin ideology-pragmatism table, leader change effects), evaluate:
   - Is the numerical value explicitly justified by cited historical evidence?
   - Are the ordinal rankings (e.g., "Prestige > Security for Austria") supported by the scholarship cited?
   - Are there alternative plausible values that the document does not acknowledge?
2. **Weight defensibility:** The primary document assigns specific numerical weights (e.g., Germany: Prestige=0.35, Security=0.40). Evaluate:
   - Does the underlying scholarship (Hamilton & Herwig 2003, etc.) actually support these precise numbers, or only the ordinal ranking?
   - If the scholarship only supports ordinal rankings, does the document acknowledge this limitation?
   - Are there sensitivity analyses or robustness checks mentioned? If not, flag this as a gap.
3. **Model-document alignment:** Compare the ABM claims in the primary document against the actual simulation design documents:
   - Does the primary document accurately describe what the simulation actually implements?
   - Are there ABM mechanisms described in the primary document that do not exist in the simulation design (or vice versa)?
   - Does the synthesis_ABM_design_improvements document's critique of the current model match gaps visible in the primary document?
4. **Causal mechanism adequacy:** For each "ABM implication" claim in Part 3 of the primary document:
   - Does the historical evidence actually support a *causal* claim, or only a *correlational* one?
   - Are the proposed mechanisms testable in an ABM framework?
   - Are there confounding variables the document does not address?
5. **Operationalization quality:** Can the concepts described (e.g., "prestige," "moral weight," "ideology-pragmatism tension") be operationalized as ABM variables without circularity?
6. **Validation cross-check:** Cross-reference the primary document's ABM parameter claims against the model validation results in `模型校验章节.md` and the three scenario reports (ID22/25/26). Do the F1 scores and confusion patterns in validation support or challenge the parameter recommendations in the primary document? For example, if ID22 (Scene 1, 1913-1925) shows systematic false positives in certain country-periods, does the primary document's parameterization explain or overlook this pattern?
7. **LLM-era method assumptions:** The ABM uses LLM-driven decision-making rather than traditional utility functions. Flag any ABM parameter recommendations in the primary document that assume traditional agent behavior (e.g., fixed utility maximization) without accounting for LLM-specific behaviors (temperature sensitivity, prompt framing effects, knowledge cutoff biases, post-hoc reasoning tendencies). Cross-reference against `prompt_design/智能体提示词设计说明.md` where relevant.

**Output format:** Structured findings with:
- **FATAL:** Parameter claim that cannot be supported by cited evidence; would need complete removal or re-anchoring
- **HIGH:** Parameter value that requires significant revision or acknowledgment of uncertainty
- **MEDIUM:** Parameter that needs better justification or sensitivity analysis
- **LOW:** Minor annotation/caveat needed

### R3: Internal Consistency & Logical Coherence Checker

**Document assignment:** Primary document (all three parts) + cross_reference_scene1_vs_research + scene history + model validation

**Review criteria:**
1. **Cross-section contradictions:** Compare claims in Part 1 (leader analysis) against Part 2 (scholarly debates) and Part 3 (ABM parameters). Flag instances where:
   - A leader's characterization in Part 1 contradicts how they are used as evidence in Part 2
   - The comparison summary table (end of Part 1) contains claims that conflict with the detailed analysis earlier in Part 1
   - ABM parameter recommendations in Part 3 are inconsistent with historical analysis in Parts 1-2
2. **Logical coherence of arguments:** For each section's central argument:
   - Does the conclusion follow from the evidence presented?
   - Are there logical leaps where the evidence presented is insufficient to support the claim?
   - Are there argumentative structures that beg the question (assume what they need to prove)?
3. **Evidence-claim alignment:** For major interpretive claims (e.g., "Wilhelm II was driven by personal prestige," "the blockade caused more civilian deaths than Allied strategic bombing in WWII"):
   - Does the evidence cited (quotations, statistics, scholarly references) actually support the specific claim made, or does it support a weaker/different claim?
   - Are there instances where a quotation from one context is used to support a claim about a different context?
4. **Temporal consistency:** The document covers 1913-1925. Check:
   - Are there instances where post-1925 developments are anachronistically attributed to pre-1925 actors?
   - Are leader characterizations consistent across the time periods they governed (e.g., Lenin 1917 vs. Lenin 1924)?
5. **Terminological consistency:** Check whether key terms (e.g., "sovereignty," "national interest," "moral") are used consistently across all three parts. Flag semantic drift.
6. **Numerical consistency:** If the same statistic or number appears in multiple places, verify it is identical. Cross-check casualty figures, dates, treaty names.
7. **Comparison table vs. body text:** The summary comparison table at the end of Part 1 is the most synthesis-heavy element. Cross-check every cell against the detailed leader analysis that precedes it.

**Output format:** Contradiction pairs with explicit references:
- **CONTRADICTION:** [Claim A, location] vs. [Claim B, location]
- **LOGICAL_GAP:** [Claim C] does not follow from [Evidence D]
- **TERMINOLOGY:** [Term X] used differently in [Section Y] vs. [Section Z]
- **NUMERICAL:** [Statistic A] at [Location 1] vs. [Statistic B] at [Location 2]

### R4: Coverage Gaps & Scholarly Depth Checker

**Document assignment:** Primary document + ALL research reports + scene history + model validation + prompt design (`智能体提示词设计说明.md`)

**Review criteria:**
1. **Missing leaders/actors:** Are there significant decision-makers from 1913-1925 who are absent or under-analyzed?
   - Wilson is extensively researched (`wilson_moral_internationalism_research.md`) but barely appears in the primary document (only in Parts 2E and 3)
   - Japan (great power, Versailles participant, Shandong controversy) is absent
   - Ottoman/Turkish leadership (Enver Pasha, Ataturk) is absent
   - The Pope/Benedict XV (1917 peace note) appears briefly but without depth
   - **Author note:** Japan and Ottoman/Turkish leadership are deliberately excluded (the ABM model's Scene 1 only covers 19 European countries). R4 should note their absence as a scope constraint rather than an error, but should flag whether the primary document acknowledges this Eurocentric scope limitation.
3. **Missing scholarly debates:** Are there major historiographical controversies not addressed?
   - The Fischer Controversy (German war guilt debate, 1960s-present) is not named or discussed
   - The "war enthusiasm" myth (recent scholarship challenging the "August 1914 enthusiasm" narrative)
   - The colonial dimension (WWI as a global/imperial war, not just European)
   - Gender analysis of WWI leadership and diplomacy
3. **Missing moral dimensions:** 
   - Chemical weapons (first use 1915, moral/legal implications)
   - Treatment of POWs and civilian populations in occupied territories
   - The Armenian genocide (1915) as a moral event contemporaneous with the leaders analyzed
   - Colonial troops and racial hierarchies in the war
4. **Missing ABM considerations:**
   - Uncertainty/partial information modeling (leaders making decisions with incomplete intelligence)
   - Domestic audience costs (a leader's domestic political survival constraining foreign policy)
   - Temporal dynamics (how preferences shift during a crisis, not just between leaders)
   - Coalition politics within governments
5. **Geographic coverage:** The document is Eurocentric. Are non-European theaters and actors acknowledged? (Middle Eastern theater, African theater, Asian theater, Latin American neutrality)
6. **Scholarly depth assessment:** For each major section, evaluate whether the cited sources represent:
   - The most authoritative works in that subfield
   - A balanced range of scholarly perspectives (or a selective reading favoring one interpretation)
   - Recent scholarship (post-2015) vs. reliance on older canonical works

**Output format:** Gap inventory with priority:
- **CRITICAL GAP:** Missing element that fundamentally undermines the document's claims
- **MAJOR GAP:** Important missing element that weakens the analysis
- **MINOR GAP:** Desirable addition but does not threaten core arguments
- **SUGGESTION:** Enhancement opportunity

---

## 4. Lead Synthesizer (R5) Methodology

After R1-R4 complete their reviews in parallel, the synthesizer will:

1. **Merge and de-duplicate:** Combine findings across all four reviews. Flag findings that appear in multiple reviews (high-confidence issues).

2. **Resolve cross-dimensional conflicts:** If R1 (Historical Accuracy) says a claim is well-supported but R2 (ABM Adequacy) says the parameter derived from that claim is unjustified, the synthesizer must adjudicate.

3. **Prioritize into tiers:**
   - **TIER 1 (Must Fix Before Publication):** CRITICAL/FATAL findings that would damage scholarly credibility
   - **TIER 2 (Should Fix):** HIGH/MAJOR findings that significantly weaken the document
   - **TIER 3 (Consider Fixing):** MEDIUM findings that would improve quality
   - **TIER 4 (Optional Enhancements):** LOW/MINOR/SUGGESTION items
4. **Generate a unified revision roadmap** organized by document section (not by reviewer).
5. **Provide a one-paragraph executive summary** suitable for a grant report or paper introduction.

**Output:** `docs/peer_review_report.md` -- the unified review deliverable.

---

## 5. Phase 2 (Optional): Targeted Scholar Consultation

If the synthesizer identifies specific scholarly questions that require external verification (e.g., "Is the claim that the British blockade caused 424,000 civilian deaths the current scholarly consensus?"), deploy document-specialist agents to do targeted web searches of recent (2023-2026) academic publications to verify or update specific claims.

This phase is conditional on Phase 1 findings and should only be invoked for Tier 1/2 issues where the reviewers disagree.

---

## 6. Task Flow

```
Step 1: Deploy R1 (Historical Accuracy) ────┐
Step 2: Deploy R2 (ABM Adequacy)    ────┼── ALL IN PARALLEL
Step 3: Deploy R3 (Consistency)     ────┤
Step 4: Deploy R4 (Coverage Gaps)   ────┘

[Wait for all 4 to complete]

Step 5: Deploy R5 (Synthesizer) ── reads all 4 review outputs, produces unified report

[Conditional]
Step 6: If Tier 1/2 issues remain contested, deploy document-specialist agents for targeted verification
```

**Estimated effort:**
- Steps 1-4 (parallel reviews): ~15-30 minutes per agent (depends on agent model and corpus size)
- Step 5 (synthesis): ~15-20 minutes
- Total wall-clock time: ~45-60 minutes
- Total approximate token cost: ~800K-1.2M input tokens across all agents

---

## 7. Review Criteria Summary Matrix

| Criterion | R1 Historical | R2 ABM | R3 Consistency | R4 Gaps |
|-----------|:---:|:---:|:---:|:---:|
| Factual accuracy | Primary | -- | Cross-check | -- |
| Source quality | Primary | Primary | -- | Primary |
| Historiographical awareness | Primary | -- | -- | Primary |
| Parameter justification | -- | Primary | Cross-check | -- |
| Model-document alignment | -- | Primary | Primary | -- |
| Causal mechanism validity | -- | Primary | Primary | -- |
| Cross-section contradictions | -- | -- | Primary | -- |
| Logical coherence | -- | -- | Primary | -- |
| Terminological consistency | -- | -- | Primary | -- |
| Missing actors/events | -- | -- | -- | Primary |
| Missing scholarly debates | -- | -- | -- | Primary |
| Geographic/colonial coverage | -- | -- | -- | Primary |

---

## 8. Deliverables

| Deliverable | Path | Description |
|-------------|------|-------------|
| Review R1 output | `docs/peer_review_r1_historical.md` | Historical accuracy findings |
| Review R2 output | `docs/peer_review_r2_abm.md` | ABM adequacy findings |
| Review R3 output | `docs/peer_review_r3_consistency.md` | Consistency findings |
| Review R4 output | `docs/peer_review_r4_gaps.md` | Coverage gap findings |
| **Synthesized report** | `docs/peer_review_report.md` | Unified review with tiered revision roadmap |

---

## 9. Review Guardrails

**Must Do:**
- Every finding must cite specific line/section references from the primary document
- Every CRITICAL/HIGH finding from R1 must be cross-referenced against the supplemental research corpus
- R1 should incorporate existing source verification findings (`Ebert_speeches_source_verification.md`, `source_verification_summary.md`) rather than independently re-verifying the same sources
- Every ABM parameter challenge must identify what additional evidence would be needed to justify the current value
- The synthesizer must NOT average or soften reviewer disagreements -- preserve the tension

**Must NOT Do:**
- Do NOT propose rewrites -- reviewers identify problems, not solutions
- Do NOT evaluate the quality of the underlying simulation code (out of scope)
- Do NOT fact-check the supplemental research documents (they are treated as authoritative within this review)
- Do NOT evaluate the literary quality or writing style of the primary document
- Do NOT make recommendations about publication venues or submission strategy

---

*This plan is ready for execution. To proceed, invoke the reviewers in parallel using oh-my-claudecode agents.*
