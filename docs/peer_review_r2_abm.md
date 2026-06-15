# Reviewer R2: ABM Modeling Adequacy Check

**Target Document:** `WWI_Historical_Analysis_1913_1925.md` (Parts 2-3, especially ABM parameter sections)  
**Cross-Referenced Against:** Simulation design docs, prompt templates, leader profiles, validation chapter, and actual codebase (`app/core/prompt_templates.py`, `app/core/leader_profiles.py`, `app/services/llm_service.py`, etc.)  
**Date:** 2026-06-13

---

## 1. Weight Matrix Audit (Part 3, Section 1: 动机排序与权重)

### 1.1 The Proposed Weight Matrix

The primary document proposes a country-specific motivation weight matrix (Table: 建议权重矩阵) assigning decimal weights across five dimensions (prestige, security, alliance commitment, expansion, morality/international law) for seven countries.

### 1.2 FATAL: Weight Matrix Not Implemented in Simulation

**Severity: FATAL**

Cross-reference with the codebase (`app/core/prompt_templates.py`, `app/core/decision_engine.py`, `app/services/llm_service.py`) reveals that **this weight matrix does not exist in the simulation**. There is no `weight_matrix`, `motivation_weight`, `prestige_weight`, `security_weight`, or `moral_weight` parameter anywhere in the code. The simulation's LLM prompt does not inject these five-dimensional numerical weights into the decision context. The prompt templates (`LEADER_TYPE_RULES`, lines 620-670 of `prompt_templates.py`) define behavioral value weights (e.g., "+0.2 for sovereignty-respecting actions under Wangdao") but these are leader-type-specific behavioral modifiers, not the country-specific motivation decomposition claimed in the primary document.

**What the simulation actually implements:**
- Four leader types with behavioral preference weights (Wangdao, Baquan, Qiangquan, Hunyong)
- Leader-specific psychological profiles (`app/core/leader_profiles.py`) injected as narrative prompts
- No country-level decomposition of motivations into prestige/security/alliance/expansion/morality dimensions

**Required justification:** The primary document must either (a) state that this matrix is an analytical derivation for discussion purposes only and is not implemented as code, or (b) implement it. As written, the document implies these weights are operational ABM parameters when they are not.

### 1.3 HIGH: Numerical Precision Unsupported by Cited Evidence

**Severity: HIGH**

The matrix assigns decimal values to three significant figures (e.g., Germany: prestige=0.35, security=0.40, alliance=0.15, expansion=0.05, morality=0.05). The sole cited source for the ordinal ranking is Hamilton & Herwig (2003). However, Hamilton & Herwig provide **ordinal rankings**, not ratio-scale weights. The transition from "prestige and security ranked highest for Germany" to "prestige=0.35, security=0.40" involves an unacknowledged leap across measurement scales.

Issues:
- Why 0.35 vs. 0.30 vs. 0.40? No sensitivity justification.
- Are these weights additive and compensatory (linear combination) or multiplicative? Not specified.
- The Hamilton & Herwig source states that prestige and security were "almost indistinguishable" in decision-makers' minds. Yet the matrix separates them into additive components (0.35 + 0.40 = 0.75 for Germany), implying they are independent dimensions that can be traded off -- contradicting the historical evidence that conflating them was precisely the causal mechanism.

**Required justification:** Either (a) add an explicit statement that the decimal weights are illustrative, with the ordinal ranking being the only component supported by evidence; (b) provide a sensitivity analysis showing how results change under alternative weight vectors; or (c) collapse prestige and security into a single "status/security" dimension with a range rather than point estimates.

### 1.4 MEDIUM: Britain's morality_weight=0.20 is Questionable

**Severity: MEDIUM**

The matrix assigns Britain the highest morality/international-law weight (0.20). The primary document's own historical analysis (Part 1, Section 2) documents Britain's naval blockade causing 300,000-424,000 civilian deaths (including 100,000 in the armistice period), the "continuous voyage" doctrine violating neutral rights, and Churchill's explicit description of the blockade as designed to starve "the whole population -- men, women, and children." The document acknowledges this as Britain's "core moral controversy." Yet this evidence does not inform the weight.

Furthermore, the synthesis design document (improvement #1) notes that Britain's morality weight applied selectively -- "defending Belgium's sovereignty while violating neutral rights when necessary." This selectivity is better captured by the Baquan (hegemonic) type's "instrumental use of norms" than by a high weight on an independent "morality" dimension.

### 1.5 MEDIUM: U.S. morality_weight=0.70 Not Anchored in 1913-1925 Period

**Severity: MEDIUM**

The matrix assigns the U.S. a morality weight of 0.70 with the annotation "(1917+)." This is the most extreme weight in the entire matrix. However, the primary document's own Part 1 analysis was not focused on the U.S. (Wilson appears only in Part 2's self-determination discussion and Part 3's Lenin-Wilson comparison). The leader_profiles.py `PROFILE_WILSON` documents Wilson's "文明等级过滤" (civilization hierarchy filter) -- his morality framework applied only to white Christian nations, not to colonies. The weight 0.70 implies a near-monocausal account of U.S. motivation that the historical evidence (including the document's own sources) does not support.

---

## 2. Sovereignty Quantification Audit (Part 3, Section 2: 主权侵犯量化)

### 2.1 HIGH: Sovereignty Severity Grades are Author-Judgment, Not Cited Evidence

**Severity: HIGH**

The primary document proposes a 5-point sovereignty violation severity scale (5=total occupation/partition, 4=large-scale territorial violation, 3=limited territorial violation, 2=non-territorial economic/military violation, 1=minor). No source is cited for these gradations. The assignment of specific countries to specific grades (Belgium=5, Luxembourg=4, China=3, Netherlands=2) appears to be the author's own judgment.

This is problematic because the `synthesis_ABM_design_improvements.md` document (Section 3.1, point #9) explicitly argues that **"what constitutes a sovereignty violation" was itself the first-order object of conflict in 1914** -- a core insight the primary document appears to have missed. Austria-Hungary considered its ultimatum to Serbia a legitimate exercise of imperial sovereignty; Serbia considered accepting Clause 6 an extinction of its sovereignty. If the severity grades are assigned from a single (apparently Westphalian/contemporary) perspective, they erase the very incommensurability that the synthesis document identifies as causally central.

### 2.2 MEDIUM: Logarithmic Decay Claim Needs Statistical Justification

**Severity: MEDIUM**

The document claims sovereignty norm constraint follows "近似对数衰减" (approximate logarithmic decay): 3 new severe violations in 1914, cumulative 7 by 1915, cumulative 9 by 1916. "1920-1925 near total collapse."

Issues:
- N=3 data points (3 time points) is insufficient to fit a logarithmic function. A linear function with a floor effect would fit equally well.
- "Near total collapse" for 1920-1925 is not documented with specific violation counts. How many violations per quarter?
- The document does not specify whether these counts are of severe violations only (grade 5) or all violations (grades 2-5). If the former, N is too small for any functional form claim.

### 2.3 MEDIUM: Model-Document Misalignment on Sovereignty Implementation

**Severity: MEDIUM**

The primary document's sovereignty severity scale (grades 1-5) has no corresponding implementation in the simulation. The simulation uses a binary `respect_sov` flag on each of 20 actions (`app/core/action_manager.py`). There is no mechanism for:
- Graded sovereignty violation severity
- Different countries perceiving the same action's sovereignty implications differently (the synthesis document's improvement #1)
- Tracking cumulative sovereignty violation counts across time

The document should state that the severity scale is an analytical construct external to the model, or the model should be extended accordingly.

---

## 3. Alliance/Following Quantification (Part 3, Section 3: 同盟/条约行为量化)

### 3.1 FATAL: `Alliance_Invocation_Rate = 0` Claim is Inconsistent with Simulation

**Severity: FATAL**

The primary document states: "ABM含义: `Alliance_Invocation_Rate = 0` (对于核心战前条约)" -- i.e., none of the pre-war core defense alliances were strictly legally triggered by Sarajevo.

This is descriptively accurate as history. However, the simulation's prompt templates (rules 9, 12, 13 in `prompt_templates.py`) contain **explicit alliance obligation mechanisms** with numerical penalties:
- Rule 9: "If your ally suffers military attack, you are obligated to take confrontational actions against the attacker in the next round, or face alliance credibility loss and domestic political pressure"
- Rule 13 (chain-ganging): Allies of attacked states get "+0.3 strategic value" for hostile actions against the attacker, and "-0.4 alliance credibility loss" for non-response
- Rule 12: Camp switching has "-0.4 credibility loss"

These rules create precisely the mechanical alliance invocation that the primary document claims should be `Alliance_Invocation_Rate = 0`. The simulation has alliance invocation built in as a **numerically incentivized mechanism**, not as a historically contingent political bargaining process. The gap between the document's claim and the simulation's implementation is a direct contradiction.

### 3.2 MEDIUM: "Territorial Compensation as Currency" Insight Not Operationalized

**Severity: MEDIUM**

The primary document insight that "wartime following is primarily motivated by territorial compensation, with alliance/ideology secondary" is historically well-supported. However, the simulation has no mechanism for territorial compensation offers between states. The 20-action space has no "offer territory" or "promise territorial compensation" action. The only resource that changes hands is abstract CINC points through the action power_change values. This means the simulation cannot reproduce the Italian 1915 case (London Treaty territorial promises) that the primary document itself cites as the paradigmatic example.

### 3.3 MEDIUM: Valid Historical Finding, No Model Connection

**Severity: MEDIUM**

The finding that "wartime alliance expansion occurred through new secret treaties with territorial compensation as currency" is well-documented by Singer & Small (1965) and the secret treaties table. However, this finding has no pathway into the ABM because (a) the simulation has no secret treaty mechanism, (b) no territorial transfer mechanism, and (c) no mechanism for states to make binding promises about future territorial distributions. The ABM implications section should acknowledge these gaps rather than implying the finding directly informs the model.

---

## 4. Lenin Ideology-Pragmatism Table (Part 3, Section 4)

### 4.1 MEDIUM: Table is Well-Supported by Historical Evidence but Unconnected to Model

**Severity: MEDIUM**

The Lenin ideology-pragmatism tension table is among the best-supported sections of Part 3, with each transition point anchored to specific historical events (February 1918 offensive, March Action failure, Polish war defeat). The six-dimension breakdown (imperialist war, secret treaties, self-determination, world revolution vs. trade, authoritarian allies, peaceful coexistence) is analytically rich.

However, two issues:

1. **Model non-connection:** The ABM implications propose `Ideology_Pragmatism_Threshold: when regime_survival_prob < 0.3, pragmatism sharply overrides ideology` and a "shadow channel" for Comintern diplomatic subversion. Neither of these mechanisms exists in the simulation. There is no `regime_survival_prob` parameter, no `Ideology_Pragmatism_Threshold`, and no "shadow channel" mechanism. The Comintern/NKID dual-track system described in the historical analysis has no simulation analogue.

2. **Single-case generalizability:** The Lenin case is presented as an "extreme stress test" of ideology-pragmatism tension, implying that if the model can capture Lenin, it can capture milder cases. But this is a methodological claim about generalizability that requires argumentation. A single extreme case (Lenin) does not validate a parameter structure for normal cases (e.g., British liberal internationalism, German Weltpolitik).

### 4.2 LOW: Lenin Not Present in Simulation

**Severity: LOW (annotation)**

The Soviet Union appears in the simulation (as RUS in scenes 1-3) but the simulation's timeframe does not include the 1917-1924 period within scene 1's active leader assignment (RUS is assigned Nikolai II's Qiangquan type in scene 1, not Lenin). The Lenin analysis is therefore entirely external to the simulation's validation scope. This should be noted.

---

## 5. Leader Change Effects (Part 3, Section 5)

### 5.1 MEDIUM: Leader Change Mechanism Partially Implemented but Not as Claimed

**Severity: MEDIUM**

The primary document proposes that `Leader_Change_Event` can "fundamentally change state preference weights within one time step" and provides two comparison tables (Asquith -> Lloyd George, Franz Joseph -> Karl I).

The simulation **does** implement a leader profile switch mechanism for one specific case: UKG in Scene 1 switches from the Asquith profile (`PROFILE_UKG_1913`) to the Lloyd George profile (`PROFILE_UKG_1913_LLOYD_GEORGE`) at round 16 (`SCENE1_UKG_PROFILE_SWITCH_ROUND = 16` in `leader_profiles.py`). This is a significant implementation that partially validates the document's claim.

However:
1. This is the **only** implemented leader change. The Franz Joseph -> Karl transition is not implemented. Wilhelm II's declining control (shadow Kaiser period) is not modeled. The Nicholas II -> Provisional Government -> Lenin sequence is not modeled.
2. The implemented change only affects the narrative `leader_profile` prompt text, not the formal `leader_type` (UKG remains Wangdao throughout). The document implies that leader changes alter preference weights, but in the simulation, the behavioral value weights come from the leader_type, which stays constant.
3. The document does not acknowledge that leader change events are implemented for only 1 of the 8 leadership transitions it discusses.

### 5.2 LOW: Scene History Document Contradicts Primary Document on Russia

**Severity: LOW (annotation)**

The scene history background document (三场景历史背景说明.md) labels RUS in scene 1 as 昏庸型 (Hunyong), citing Nicholas II's indecisiveness. The model validation chapter (模型校验章节.md) initially also labeled RUS as 昏庸型 but later updated to 强权型 (Qiangquan) with a note about Nicholas's indecisiveness being a limitation of the Qiangquan classification. The primary document's historical analysis (Part 1, Section 3) describes Nicholas II as "weak and excessively kind" with "pathological conflict aversion" -- traits that align more with Hunyong than Qiangquan. The primary document is silent on this classification tension.

---

## 6. Model-Document Alignment (Cross-Document Consistency)

### 6.1 FATAL: Psychological Bias Parameters Exist Only in Primary Document

**Severity: FATAL**

Part 2, Section C of the primary document proposes seven psychological bias parameters with specific numerical values:

| Bias | Proposed Value |
|------|---------------|
| Win_Prob_Overestimate | +0.3 |
| Loss_Aversion | 2.0-2.5x |
| Offensive_Bias | +0.4 |
| Sunk_Cost | 0.15 * casualties/person |
| Military_Instit_Bias | +0.2 |
| Short_Term_Disc | 0.7 |
| Info_Bias | +0.2 |

**None of these parameters exist in the simulation code.** A grep for `Win_Prob`, `Loss_Aversion`, `Offensive_Bias`, `Sunk_Cost`, `Overestimate`, `前景理论`, `沉没成本` across the entire `app/` directory returns zero matches. The simulation has no mechanism for:
- Inflating subjective victory probability estimates
- Multiplicative loss aversion weighting
- Offensive doctrine bias in military planning
- Sunk cost effects scaling with casualties
- Organizational military bias
- Hyperbolic time discounting
- Information filtering bias

The simulation does have some related mechanisms (conflict escalation inertia in Rule 11, win probability assessment in the cost-benefit analysis requirements), but these operate through LLM narrative reasoning in prompts, not through numerical bias parameters. The gap between the document's parametric claims and the simulation's actual implementation is complete.

### 6.2 HIGH: Primary Document's "ABM Implications" Often Misaligned with Implementation

**Severity: HIGH**

The primary document's 7-point "强建模含义总结" (Strong Modeling Implications Summary) claims several mechanisms that the simulation does not implement:

| Claim | Implementation Status |
|-------|----------------------|
| 1. National interest is not unidimensional -- decomposed into prestige/security/territory | **Not implemented** -- single `national_interest` per country from CINC level only |
| 2. Sovereignty norm constraint follows logarithmic decay | **Not implemented** -- binary respect_sov, no tracking of violation frequency over time |
| 3. Alliance/following is not automatic -- territorial compensation is the currency | **Partially** -- alliance incentives exist in prompts, but no territorial compensation mechanism |
| 4. Casualties trigger escalation, not exit -- sunk cost must be modeled | **Not implemented** -- no casualty tracking or sunk cost parameter |
| 5. Leader changes can fundamentally alter state preferences within one step | **Partially** -- 1 of 8 transitions implemented, only affects narrative profile not formal type |
| 6. Lenin as extreme stress test of ideology/pragmatism tension | **Not implemented** -- no ideology parameter, no pragmatism threshold |
| 7. Wilson vs. Lenin antagonism shows normative competition is a causal force | **Not implemented** -- no normative competition mechanism |

Out of 7 claimed strong modeling implications, **4 are not implemented at all, 2 are partially implemented, and 0 are fully implemented as described.**

### 6.3 HIGH: Synthesis Document's Critiques Map Directly onto Primary Document Gaps

**Severity: HIGH**

The `synthesis_ABM_design_improvements.md` document identifies 10 specific tensions between the simulation design and historical evidence. The primary document (Part 3) addresses none of these tensions:

| Synthesis Critique | Primary Document Coverage |
|-------------------|--------------------------|
| #2: Sovereignty is not binary -- it is ontologically diverse | Proposes a 5-point severity scale that remains unidimensional |
| #3: CINC framework has implicit materialist ontology bias | Not acknowledged |
| #4: Following is modeled as interest-maximization only | Not acknowledged |
| #6: LLM rationality vs. historical bounded rationality | Not acknowledged |
| #7: Strategic relationship stability constraints preclude 1914-style cascades | Not acknowledged |
| #9: Sovereignty respect rate as a single framework erases ontological disagreement | Not acknowledged |

The synthesis document was written as a critical analysis based on the same historical materials. The primary document's ABM parameter recommendations do not engage with these critiques, creating a significant alignment gap between the historical-analysis-to-design pipeline and the actual design improvements proposed.

---

## 7. Validation Cross-Check

### 7.1 MEDIUM: F1 Scores Neither Support Nor Challenge ABM Parameter Claims

**Severity: MEDIUM**

The model validation results (overall weighted F1=0.761) demonstrate that the simulation has non-random historical replication ability. However:

1. **The validation tests following behavior, not motivation weights.** The F1 scores measure whether simulated countries follow the same leaders as historical countries did. They do not test whether they follow for the right reasons (prestige vs. security vs. morality). The weight matrix is thus entirely unvalidated.

2. **The largest error mode (FP/false following in multipolar systems, 65-67%) may indicate the motivation decomposition problem.** In multipolar systems, FP errors dominate -- the model "over-follows" (follows when it should be neutral). This could indicate that the model cannot distinguish between following driven by alliance obligation vs. following driven by issue-specific interest -- precisely the "alliance != following" distinction the primary document highlights. But the model validation chapter attributes this to "more menu options" in multipolar systems, not to motivation ambiguity.

3. **Italy's F1 trajectory (0.59 -> 0.597 -> 0.958) validates the alliance-following distinction but not the weight matrix.** Italy's dismal F1 in multipolar eras and perfect F1 in bipolar eras demonstrates that alliance and following are different constructs. This supports the primary document's conceptual point but provides zero evidence for the specific weights (e.g., Italy: prestige=0.30, expansion=0.40).

4. **F1=0 countries (Spain, Finland, Ireland) challenge the model's neutrality/alignment assumptions.** The validation chapter identifies that the model cannot handle "non-alignment != issue neutrality." The primary document does not discuss how the weight matrix would handle neutral/non-aligned states.

### 7.2 MEDIUM: Leader Type Validation Uses CINC Thresholds, Not Historical Behavior

**Severity: MEDIUM**

The model validation chapter (Section 4) assigns leader types to countries based on CINC power_share thresholds (>0.10 = great power = gets leader_type). This means the assignment of leader types is **structurally determined by material capabilities, not by historical evidence**. The primary document's historical analysis documents complex leader behavior (e.g., Austria-Hungary acting like Hunyong despite being a middle power), but the simulation assigns leader_type only to CINC-defined great powers. This creates a fundamental circularity: the weight matrix claims to capture motivation differences, but the model only allows motivation differences for countries that are already materially powerful.

The validation chapter acknowledges this in Section 4.5: "中等强国与小国的 leader_type 为零（None），其行为由 national_interest 驱动而不受 leader_type 行为权重的调节" -- middle and small powers get no leader type. This means the entire motivation weight matrix for Italy (prestige=0.30, expansion=0.40) would be applied to a country that, in the simulation, has no leader_type because its CINC is below the threshold.

---

## 8. LLM-Era Method Assumptions

### 8.1 HIGH: Temperature Sensitivity Not Addressed

**Severity: HIGH**

The simulation uses temperature=0.35 for decision tasks (`llm_service.py`, line 47). The primary document proposes numerical weight parameters (e.g., prestige=0.35 for Germany) but does not discuss whether LLM outputs at temperature=0.35 are stable enough to meaningfully differentiate between a weight of 0.35 and 0.30. Temperature 0.35 is relatively low but not zero -- some output variance remains. Without ablation studies demonstrating sensitivity to weight changes of 0.05-0.10, the precision of the proposed weights cannot be evaluated.

### 8.2 HIGH: Prompt Framing Effects Not Analyzed

**Severity: HIGH**

The simulation implements leader-type-specific behavioral value weights in the prompt (e.g., Wangdao: +0.2 for respect_sov=True actions). The primary document proposes country-specific motivation weights (e.g., Germany: prestige=0.35). These are **structurally different types of parameters**:

- **Prompt weights** (implemented): LLM is told "actions respecting sovereignty get +0.2" and asked to incorporate this into cost-benefit analysis narratively.
- **Document weights** (proposed): Hypothetical numerical decomposition of motivation dimensions.

The document does not discuss how LLM narrative reasoning might interact with numerical weights embedded in prompts. For example, would an LLM explicitly told "Germany weights prestige at 0.35" actually produce different behavior than one told "Germany highly values prestige"? The prompt design document (Section 8, principle 8) emphasizes that weights "must be explicitly applied in cost-benefit analysis" -- but this is a behavioral instruction, not a validated calibration.

### 8.3 MEDIUM: Knowledge Cutoff and Post-Hoc Reasoning Biases

**Severity: MEDIUM**

The synthesis document (Section 3.1, point #10) identifies a critical LLM-era concern: "LLM post-hoc correction" -- the LLM, trained on data that includes the known outcome of WWI, may systematically fail to reproduce the "defective rationality" of historical actors (e.g., Austria's willingness to launch a war it knew it might lose). The primary document does not address whether the proposed ABM parameters would interact with this LLM bias.

For example, if an LLM "knows" that Germany lost WWI, it may be less willing to produce the high-risk behaviors that Germany actually engaged in during July 1914 -- regardless of what prestige or security weights are specified. This creates a fundamental confound: the weights might be "accurate" in historical terms but produce "inaccurate" simulation outputs because the LLM's training data corrects for the poor outcomes.

### 8.4 MEDIUM: Prompt Cache Optimization Not Discussed

**Severity: MEDIUM**

The simulation uses Anthropic prompt caching for the shared system prompt prefix (`decision_engine.py`, line 381-343). The prompt design document (Section 8, principle 8) notes that leader-type-specific weights must change between agents. The primary document's country-level weight matrix would require either (a) per-country system prompts (breaking the cache design and multiplying API costs by N) or (b) embedding weights in user prompts (where they compete for attention with situational data). Neither option is analyzed.

### 8.5 LOW: Few-Shot Anchoring in Goal Evaluation Not Extended to Decision Weights

**Severity: LOW (annotation)**

The goal evaluation prompt uses three few-shot anchors (85/55/25) to stabilize scoring. The primary document's weight matrix has no analogous anchoring. If the LLM is asked to weight "prestige" at 0.35 vs. "security" at 0.40, it has no reference examples of what a 0.35-weighted prestige consideration looks like in cost-benefit analysis terms. The prompt design document's eight design principles do not address this gap.

---

## 9. Summary Matrix

| Section | Finding | Severity | Count |
|---------|---------|----------|-------|
| 1. Weight Matrix | Weight matrix not implemented in simulation | FATAL | 1 |
| 3. Alliance | Alliance_Invocation_Rate=0 contradicts implemented chain-ganging | FATAL | 1 |
| 6. Model-Doc Alignment | 7 psychological bias parameters exist only in document | FATAL | 1 |
| 1. Weight Matrix | Decimal weights unsupported by ordinal-only source | HIGH | 1 |
| 2. Sovereignty | Severity grades are author judgment, no cited methodology | HIGH | 1 |
| 6. Model-Doc Alignment | 4/7 "strong modeling implications" not implemented | HIGH | 1 |
| 6. Model-Doc Alignment | Synthesis critiques unaddressed by primary document | HIGH | 1 |
| 8. LLM Methods | Temperature sensitivity not analyzed for weight precision | HIGH | 1 |
| 8. LLM Methods | Prompt framing effects vs. numerical weights not analyzed | HIGH | 1 |
| 1. Weight Matrix | UK morality_weight=0.20 contradicted by blockade evidence | MEDIUM | 1 |
| 1. Weight Matrix | US morality_weight=0.70 exceeds evidence for period | MEDIUM | 1 |
| 2. Sovereignty | Logarithmic decay claim from N=3 data points | MEDIUM | 1 |
| 2. Sovereignty | Model-doc misalignment on sovereignty (binary vs. graded) | MEDIUM | 1 |
| 3. Alliance | Territorial compensation insight not operationalized | MEDIUM | 1 |
| 3. Alliance | Historical finding has no pathway into ABM | MEDIUM | 1 |
| 4. Lenin | Well-supported historically but model-unconnected | MEDIUM | 1 |
| 5. Leader Change | 1 of 8 transitions implemented | MEDIUM | 1 |
| 7. Validation | F1 scores validate following, not motivation weights | MEDIUM | 1 |
| 7. Validation | Leader type assignment by CINC threshold, not behavior | MEDIUM | 1 |
| 8. LLM Methods | Knowledge cutoff/post-hoc reasoning biases | MEDIUM | 1 |
| 8. LLM Methods | Prompt cache not discussed for per-country weights | MEDIUM | 1 |
| 4. Lenin | Lenin not an active simulation agent | LOW | 1 |
| 5. Leader Change | Scene history contradicts primary doc on Russia type | LOW | 1 |
| 8. LLM Methods | Few-shot anchoring not extended to decision weights | LOW | 1 |

**Totals: 3 FATAL, 6 HIGH, 14 MEDIUM, 3 LOW**

---

## 10. Overall Assessment

The primary document represents a serious historical synthesis with rigorous source engagement. Parts 1 and 2 are well-grounded in the scholarly literature. However, Part 3 (ABM参数量化基础) contains a systematic misalignment between the parameters it proposes and the simulation it purports to inform.

The most severe problem is not that the proposed parameters are historically implausible -- many are plausible as ordinal characterizations. The problem is that **the document presents analytical parameters as if they are operational ABM parameters, when the simulation implements a fundamentally different parameter structure** (leader-type behavioral weights + narrative profiles rather than country-level motivation decompositions).

Three convergent lines of evidence establish this:
1. **Code absence**: Grep for weight_matrix, motivation_weight, prestige_weight, security_weight, Win_Prob_Overestimate, Loss_Aversion, Offensive_Bias, Sunk_Cost, Ideology_Pragmatism_Threshold, Alliance_Invocation_Rate across the entire app/ directory returns zero operational matches.
2. **Simulation design docs**: The 仿真设计说明.md and 智能体提示词设计说明.md describe leader-type-driven behavioral weights, not country-specific motivation decomposition.
3. **Synthesis document**: The synthesis_ABM_design_improvements.md independently identifies 10 gaps between historical evidence and simulation design -- most of which the primary document's Part 3 does not address.

**Recommended action**: The primary document should either (a) be reframed to clarify that Part 3's parameter proposals are analytical desiderata for a future version of the model, not descriptions of the current implementation, or (b) have its parameter proposals aligned with what the simulation actually implements (leader-type behavioral weights, leader profiles, CINC-based structural constraints). In either case, the three FATAL findings must be resolved before the document can serve as the ABM parameter justification it claims to be.

---

*Review methodology: All code claims verified against `app/core/prompt_templates.py`, `app/core/leader_profiles.py`, `app/services/llm_service.py`, `app/core/decision_engine.py`, `app/core/action_manager.py`, and `app/core/decision_validation.py`. Historical claims cross-referenced against synthesis_ABM_design_improvements.md, AH_1914_decision_making_scholarly_analysis.md, sovereignty_norms_evolution_1914_contemporary.md, and 模型校验章节.md.*
