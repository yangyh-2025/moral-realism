# Cross-Reference: Historical Research vs. Scene 1 Ground Truth Data

**STATUS: V6 IMPLEMENTED (2026-06-12)** — All 6 gaps identified in this document have been addressed in the V6 ground truth data. The implementation details are documented in `data/history/generate_history_v6.py` and the updated `data/history/scene1_prewar_1913.json`. The analysis below is preserved for reference.

## Overview

This document cross-references the historical research on British WWI leadership with the ground truth following data in `scene1_prewar_1913.json` (50 rounds, 1913Q1-1925Q2, 19 countries). The ground truth encodes which country follows which leader on the dominant issue of each quarter.

## UK's Position in the Model

- **UK never follows any other country** across all 50 rounds (R1-R50). UK is a permanent leader.
- **UK initially follows the dominant issue but does not subordinate to another state.**

This correctly reflects the historical reality: the UK was an independent great power making its own strategic decisions throughout this period, never a follower of France, Russia, or any other power.

## Belgium's Alignment: Historically Validated

Belgium follows the UK in every single round from R1 (1913Q1) through R50 (1925Q2).

**Historical validation -- ACCURATE:**
- The research confirms that the 1839 Treaty of London made Britain the guarantor of Belgian neutrality
- Belgium relied on Britain's guarantee for its security against Germany
- After WWI, Belgium continued to align with British security guarantees (Lloyd George's 1920 reaffirmation to Premier Delacroix)
- The Locarno Treaties (R45-R48) feature Britain as key guarantor of Belgo-German borders

## Serbia/Yugoslavia's Shift: Accurate and Significant

| Period | Serbia follows | Historical Context |
|--------|---------------|-------------------|
| R1-R10 (1913-1915) | Russia (index 2) | Historically accurate: Serbia was Russia's Balkan client, Russia backed the Slavic Balkan League |
| R12-R14 (1915) | Russia (index 2) | Serbia overrun by Central Powers but still aligned with Russia |
| R15 onward (1916-1925) | UK (index 3) | **Critical shift** -- research confirms this needs examination |

**Analysis of the R15 shift:** The ground truth has Serbia/Yugoslavia switching from following Russia to following the UK at R15 (1916Q3). Historically, this coincides with: (a) the Russian Brusilov Offensive being Russia's last major success, (b) Serbia being overrun and its government in exile relying on Entente support, (c) the eventual Bolshevik Revolution (R19) making Russia irrelevant as a patron. The ground truth captures a realignment that occurred gradually in 1916-1917 as Russia weakened and Britain/France became the primary protectors of Serbian interests. **This shift is historically supported.**

## Ottoman Empire: Accurate But Could Be Richer

The Ottoman Empire follows Germany from R1 through R22, then becomes "None" at R23 (1918Q3) when it surrenders. This correctly captures:
- The Ottoman-German military alliance (the Goeben-Breslau incident, Liman von Sanders mission)
- Ottoman entry into WWI on the Central Powers side
- Ottoman collapse and surrender before the general Armistice

**Missing nuance:** The ground truth does not capture the secret Anglo-Ottoman dealings (the Sykes-Picot contradiction of Hussein-McMahon promises, the 1918-1919 partition). The post-war Ottoman/Turkish transition (R25-R32: Greco-Turkish War, Turkish Nationalists under Ataturk) shows the Ottoman Empire as "None" rather than showing Turkey's new alignment. This is somewhat accurate for the Ottoman state (which was abolished) but misses the emergence of an independent Turkish foreign policy.

## Key Historical Events Captured by the Ground Truth

| Round | Dominant Issue | Historical Research Support |
|-------|---------------|---------------------------|
| R5 | Anglo-German naval race peaks | Supported: 1911 Agadir Crisis, Mansion House speech, naval building programs |
| R7 | July Crisis / Archduke assassination | Supported: documented in detail by Asquith's six principles and Cabinet deliberations |
| R8 | WWI outbreak / Germany invades Belgium | Supported: Asquith's "scrap of paper" response, Belgian neutrality as casus belli |
| R9 | Ottoman enters war & Gallipoli | Supported: Easterner vs Westerner debate, Churchill's role |
| R10 | Italy joins Entente (Treaty of London) | Supported: secret treaty promising Italy territorial gains |
| R17 | Russian Revolution & US entry | Supported: transformative moment; US entry changed war dynamics |
| R19 | Russian October Revolution & Caporetto | Supported: Bolsheviks expose secret treaties |
| R24 | Armistice / German & A-H empires dissolve | Supported: but does NOT capture the continued blockade |
| R25 | Paris Peace Conference | Supported: Lloyd George as mediator between Clemenceau and Wilson |
| R26 | Treaty of Versailles | Supported: war guilt, reparations, territorial losses |
| R29 | League of Nations founded | Supported: both leaders advocated for League; US rejection |
| R35 | Treaty of Rapallo (Germany-Soviet) | Supported: Germany breaking Versailles isolation |
| R36 | Washington Naval Treaty | Supported: naval disarmament ratios |
| R45-48 | Locarno Treaties | Supported: UK/Italy guarantee borders, Germany rejoins |

## Gaps and Suggested Enhancements

Based on the historical research, several important dimensions are NOT reflected in the current ground truth:

### 1. The Naval Blockade (R8-R26)
The ground truth has no issue capturing the British blockade of Germany or its humanitarian consequences (~424,000-763,000 civilian deaths). This was one of the most consequential and morally complex British policies of the war. **Recommendation:** Consider adding a blockade-related dominant issue in 1915-1919 rounds, potentially as a secondary issue.

### 2. Secret Treaties / Double Diplomacy
The contradictory promises (Sykes-Picot vs Hussein-McMahon vs Balfour Declaration) are not explicitly captured. R25 (Paris Peace Conference) mentions Wilson's Fourteen Points but not the tension between open covenants and the secret treaty legacy. **Recommendation:** An issue capturing the "betrayal of Arab allies" or "contradictory wartime promises" could enrich the moral dimensions of UK behavior.

### 3. The Asquith-to-Lloyd George Transition (December 1916)
This critical leadership change that split the Liberal Party permanently occurs between R15 (1916Q3) and R16 (1916Q4) but is NOT reflected in the ground truth. The UK's following behavior (always "None") does not change, but historically the character of British leadership changed dramatically. **Recommendation:** If the model tracks individual leaders or leadership style, this transition should be marked around R16.

### 4. The Post-Armistice Blockade Continuation (R24-R26)
The ground truth shows Armistice at R24 (1918Q4) and Versailles at R26 (1919Q2), but the continued starvation blockade between these dates (~100,000 additional civilian deaths) is not captured. **Recommendation:** An issue like "Humanitarian crisis / continued blockade" could bridge R24-R26.

### 5. Imperial Expansion at Versailles
The British Empire gained ~1 million square miles at the very moment self-determination was proclaimed. The mandate system contradictions (Class A/B/C hierarchies, racial assumptions) are not captured. **Recommendation:** The League of Nations founding (R29) could include an issue about mandate legitimacy and colonial self-determination.

### 6. Belgium's Ambiguous Position
Belgium follows the UK throughout, but historically Belgium also had interests that conflicted with British blockade policy (needing food imports through the blockade). The Commission for Relief in Belgium (1914-1919) is a missing dimension. **Recommendation:** Belgium might at certain rounds show tension with UK policy while remaining fundamentally aligned.

### 7. The Moral Tension Dimension
A recurring finding of the research is the gap between liberal rhetoric (defending small nations, treaty sanctity, self-determination) and realist practice (starvation blockade, secret treaties, imperial expansion). The ground truth captures structural alignment but not the moral dilemmas inherent in British policy. **Recommendation:** If the model has any mechanism for tracking moral consistency, the UK's behavior across 1914-1922 should show significant tension between declared principles and actual policies.

## Overall Assessment

The ground truth data correctly captures:
- UK's position as an independent great power (never a follower)
- Belgium's alignment with UK security guarantees
- Serbia's shift from Russian to Western protection
- Ottoman alignment with Germany and subsequent collapse

The ground truth does NOT capture (key gaps):
- The naval blockade and its humanitarian/moral dimensions
- The secret treaty contradictions (Sykes-Picot / Hussein-McMahon / Balfour)
- The Asquith-to-Lloyd George leadership transition
- The post-armistice continued blockade
- The tension between liberal-moral rhetoric and imperial-realist practice
- The mandate system's subordination of self-determination to imperial interests

## Specific Recommendations for Model Enhancement

1. **Add a "UK Leadership" transition flag** at R16 to mark the Asquith-to-Lloyd George change
2. **Add blockade-related issues** in the 1915-1919 period
3. **Add a "double diplomacy" issue** around R17 (Russian Revolution exposes secret treaties)
4. **Consider moral consistency metrics** that track the gap between a power's declared principles and actual policies
5. **For Belgium**, consider moments of tension (blockade affects neutral Belgium) even while preserving overall alignment
6. **For the Ottoman/post-Ottoman space**, add issues capturing the contradictory promises to Arabs, Zionists, and French
