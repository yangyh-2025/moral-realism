# Peer Review Synthesis: WWI Historical Analysis for Moral-ABM

**Synthesis date:** 2026-06-13
**Reviewers completed:** R2 (ABM adequacy), R3 (internal consistency), R4 (coverage gaps)
**R1 status:** Partial — Germany/Britain sections verified via test; Italy/AH/Lenin in progress

---

## Finding Summary by Severity

### CRITICAL (7 findings — must fix)

| # | Source | Finding |
|---|--------|---------|
| C1 | R2 | **Weight matrix not implemented in simulation.** Document proposes country-specific motivation weights (prestige/security/alliance/expansion/morality); code uses leader_type behavioral weights instead. No `weight_matrix` parameter exists. |
| C2 | R2 | **`Alliance_Invocation_Rate=0` contradicts implemented chain-ganging rules.** Simulation prompts contain explicit alliance obligation penalties (+0.3 strategic value, -0.4 credibility loss). |
| C3 | R2 | **7 psychological bias parameters exist only in document.** `Win_Prob_Overestimate`, `Loss_Aversion`, etc. — zero grep matches in `app/` directory. |
| C4 | R3 | **Russia leader_type contradiction across documents.** Scene history says 昏庸型; model validation says 强权型. Simulation output depends on which is authoritative. |
| C5 | R4 | **Wilson near-total omission.** Moral-internationalist leader archetype with dedicated 200+ line research monograph; only 7 scattered references in primary document. |
| C6 | R4 | **Armenian Genocide unmentioned.** Largest moral catastrophe contemporaneous with analyzed leaders. Document on "moral dimensions" of WWI cannot omit this. |
| C7 | R4 | **Uncertainty/partial information not modeled.** July Crisis decisions made under radical uncertainty; ABM assumes full information. No parameter addresses intelligence quality or strategic uncertainty. |

### HIGH (10 findings — should fix)

| # | Source | Finding |
|---|--------|---------|
| H1 | R2 | **Decimal weights unsupported by ordinal-only source.** Hamilton & Herwig (2003) provide ranking, not ratio-scale 0.35 vs. 0.40 precision. |
| H2 | R2 | **Sovereignty severity grades are author-judgment.** No cited methodology for 5-point scale; grades erase the ontological incommensurability that synthesis doc identifies as causal. |
| H3 | R2 | **4 of 7 "strong modeling implications" not implemented.** National interest decomposition, sovereignty log decay, sunk cost, normative competition — not in code. |
| H4 | R2 | **Synthesis design critiques unaddressed.** `synthesis_ABM_design_improvements.md` lists 10 tensions; primary doc addresses 0. |
| H5 | R2 | **Temperature sensitivity not analyzed.** LLM at temperature=0.35 may not differentiate weights of 0.35 vs. 0.30. |
| H6 | R2 | **Prompt framing vs. numerical weights not analyzed.** LLM told "+0.2 for respect_sovereignty" vs. told "Germany weights prestige at 0.35" — fundamentally different parameter structures. |
| H7 | R4 | **Fischer Controversy unmentioned.** Defining WWI historiographical debate; document makes war-guilt claims without acknowledging the field's most contested question. |
| H8 | R4 | **Eurocentrism unacknowledged.** WWI presented as purely European; global turn in historiography (Gerwarth, Manela, Xu) unrecognized. |
| H9 | R4 | **Reliance on pre-2015 canonical works.** Post-2015 scholarship ghettoized in Part 2G; Cambridge History of WWI (2014), Leonhard (2018) absent. |
| H10 | R3 | **"Prestige = Security" finding undermines weight separation.** Evidence says they're indistinguishable → conclusion says they need separate parameters. Logically reversed. |

### MAJOR GAPS (R4-identified — most important)

- Peace movements (Second International, Zimmerwald, interwar mass movements) not integrated despite dedicated research monograph
- Chemical weapons as norm-collapse case study missed
- Domestic audience costs not modeled (well-established IR mechanism)
- Coalition politics unitary-actor assumption unacknowledged
- Crisis preference shifts (within-leader volatility) not operationalized
- Pope Benedict XV depth absent despite 1917 Peace Note relevance
- Arthur Henderson completely absent despite embodying national/internationalist tension
- Uneven source depth: strong on Germany/Britain, thin on France/Italy/AH/Lenin

### MEDIUM (R3-identified — internal consistency)

- Nicholas II "no coherent national interest concept" vs. stable ABM weight assignment
- Wilhelm "高度飘忽" vs. stable fixed weights — structural contradiction
- France comparison table "极为一致" vs. body text showing goal divergence
- Blockade death toll evidence-claim mismatch (Drew comparison lacks WWII baseline)
- Sovereignty terminology drift (binary legal → continuous severity)
- No methodological bridge between qualitative characterizations and quantitative weights

---

## Verdict: REVISE

The document represents serious historical synthesis but has a fundamental structural problem: **Part 3 presents parameters as if they are operational ABM specifications, when the simulation implements a fundamentally different parameter structure.** The historical analysis (Parts 1-2) is well-grounded but uneven across leader sections. Critical coverage gaps (Wilson, Armenian genocide, Fischer controversy, uncertainty modeling) prevent acceptance as-is.

### Minimum revision path (to ACCEPT-WITH-RESERVATIONS):

1. **Reframe Part 3** to clarify whether parameters are (a) analytical desiderata for future model versions, or (b) descriptions of current implementation. If (b), align with what code actually does.
2. **Add scope statement** acknowledging Eurocentric framing, 19-country ABM limitation, and deliberate exclusions (Japan, Ottoman Empire, colonial theaters, gender dimension).
3. **Fix Russia leader_type contradiction** — harmonize 昏庸型 vs. 强权型 across documents.
4. **Add methodological bridge** explaining how qualitative characterizations map to quantitative weights (even if approximate/ordinal).
5. **Expand Wilson section** to at least 50 lines drawing from existing research monograph.
6. **Add Armenian genocide acknowledgment** as contemporaneous moral event.
7. **Add Fischer Controversy subsection** to Part 2.
8. **Resolve the 3 FATAL code-document mismatches** (C1-C3) — either implement parameters in code or reframe document claims.
