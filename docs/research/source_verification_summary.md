# Source-Verification Summary: Ebert and Conrad Research

**Date:** 2026-06-12
**Scope:** Web-based source verification of research claims used by the moral-ABM model
**Detailed findings:** `Ebert_speeches_source_verification.md`

---

## Part I: Ebert

### Verified (primary source directly accessed)

| Claim | Source | Confidence |
|---|---|---|
| Neujahrsaufruf 1924 - full German text | *Arbeiter-Jugend*, 16. Jg., 1924 (BBF scan) | HIGH |
| May 11, 1919 Versailles denunciation | Ogden Daily Standard, Salt Lake Tribune (May 1919) | HIGH |
| Feb 1919 National Assembly address (Selbstbestimmungsrecht, renunciation of Gewaltprinzip) | Multiple newspaper archives + FES | HIGH |

### Verified (scholarly source confirmed online)

| Claim | Source | Confidence |
|---|---|---|
| Vernunftrepublikaner coinage = Meinecke 1919 | Kaemper (2014); multiple independent sources | HIGH |
| Krueger (1985) "friedliche Revision" thesis framing Ebert | *Vierteljahrshefte fuer Zeitgeschichte*; multiple reviews | HIGH |
| Cohrs (2022, Cambridge) credits Ebert with "Atlanticist" foreign policy | *The New Atlantic Order*, ch. 13 | HIGH |
| Weimar Constitution Art. 4 (binding international law) -- Ebert supported | MPIL, De Gruyter sources | HIGH |
| Muehlhausen (2006) is the definitive Ebert biography | Multiple academic reviews (H-Net, sehepunkte, ZfP) | HIGH |
| Muehlhausen (2017) is the definitive Ebert speech edition | UPenn, Emory catalogs; Dietz Verlag | HIGH |
| Stresemann diaries (Sutton Vol. II, 1937) cover Ebert's death and relationship | NYT 1938 review; Princeton catalog | HIGH |

### Suspect (could not verify online)

| Claim | Problem | Recommendation |
|---|---|---|
| "Sovereignty in the modern world cannot mean isolation" (Reichstag June 1920) | No German original found; no verbatim match in any primary source | Remove as direct quotation; use period-accurate paraphrase with Ebert's vocabulary |
| DFG speech November 1923 | Rests on Scheer (1983, pp. 382-387) -- monograph not accessible online; publication date discrepancy (1981 vs 1983) | Flag as single-source dependent; verify Scheer physically |
| Konstanz speech August 1924 | Discussed by Muehlhausen (2006, pp. 830-835) but no verbatim transcript found online | Flag as paraphrastic; verify via Muehlhausen or FES archive |
| "rare combination of moral conviction and political realism" (attributed to Kolb 1997) | No match in any searchable source | Removed from Ebert.txt; replaced with unattributed paraphrase |
| Specific content of Ebert-Stresemann conversation (early 1925) | Sutton Vol. II not accessed in full text; content is Ebert.txt author's paraphrase | Check against Sutton or Bernhard edition |

### Terminology corrections applied

| Removed | Replaced with |
|---|---|
| "peaceful means" (as Ebert vocabulary) | "negotiation, economic leverage, institutional engagement" + Krueger (1985) attribution |
| "embedded sovereignty" (as Ebert's concept) | Ebert's actual commitments: Art. 4 WRV, equal participation, binding international law; "embedded sovereignty" retained only as retrospective scholarly label |
| "collective security" (as Ebert concept) | "equal membership in the League" / "binding international law" -- era-appropriate terms |
| "democratic peace" (as Ebert concept) | Ebert's own formulation: "freie und friedliche Demokratie" as precondition for "geachtete Stellung unter den Voelkern" |

### Ebert's period-authentic vocabulary (from verified primary sources)

- Selbstbestimmungsrecht (self-determination)
- Gleichberechtigung (equal rights)
- das Recht (law/right)
- Voelkerbund (League of Nations)
- freie und friedliche Demokratie (free and peaceful democracy)
- geachtete Stellung unter den Voelkern (honored place among the nations)
- Politik der Voelkerverstaendigung (policy of international understanding)

---

## Part II: Conrad von Hotzendorf

### Verified (scholarly source confirmed online)

| Claim | Source | Confidence |
|---|---|---|
| "25 times" preventive war proposals (1913-1914) | Strachan (2001), reproduced in Fromkin (2004); independently corroborated by 1914-1918-Online | HIGH |
| Social Darwinist worldview | 1914-1918-Online; Grotelueschen & Varble (2022); Sondhaus (2000) reviews | HIGH |
| Baernreither quote (manufacturing excuses for war) | Wank (1986), *Austrian History Yearbook* | HIGH |
| Rothenberg assessment (most responsible for war; incompetent commander) | Rothenberg (2002), H-Net review of Sondhaus -- direct quotation verified | HIGH |
| "Fate of nations...decided on battlefield" quotation | Grotelueschen & Varble (2022, p. 136) | HIGH |
| June 28, 1914 diary entry (forlorn fight / cannot go down ingloriously) | Habsburger.net; *National Interest* | HIGH |
| "Wegelagererpolitik" (Aehrenthal's denunciation) | Clark (2012), Sondhaus (2000), Williamson (1991) | HIGH |
| Franz Joseph "go with honour" quotation | Bibl (1924) via Habsburger.net | MEDIUM-HIGH (secondary source) |

### Not verified online but plausible

| Claim | Source chain | Recommendation |
|---|---|---|
| Franz Joseph "Meine Politik ist eine Politik des Friedens" (Nov 15, 1911) | Likely via Sondhaus (2000) or Conrad's *Aus meiner Dienstzeit* | Cite intermediary source |
| Sondhaus "Architect of the Apocalypse" subtitle | Book subtitle confirmed via catalogs; used in prompt_templates.py line 676 | Can use with confidence |

### Key finding

The Conrad research file (`data/research_conrad_hotzendorf_WWI.txt`) is a **responsible scholarly synthesis**. All testable claims verified. Conrad's own memoir (*Aus meiner Dienstzeit*, 5 vols, 1921-25) is the only primary source and is explicitly self-serving -- secondary-source triangulation is essential for any Conrad quotation.

---

## Files Modified in This Session

| File | Changes |
|---|---|
| `docs/Ebert.txt` | 8 edits: removed unverifiable quotations, replaced anachronistic terminology, added scholarly cautionary notes, fixed Kolb attribution |
| `docs/research/Ebert_speeches_source_verification.md` | Created (~84KB): Parts I-II with 15 verified claims, source tables, 3 appendices |
| `docs/research/source_verification_summary.md` | This file |

---

## Next Steps (Require Physical Access)

1. Verify Scheer (1981 or 1983), pp. 382-387, for the November 1923 DFG speech
2. Verify Kolb (1997), pp. 245-250, for the June 1920 Reichstag speech content
3. Verify Stresemann diary entry (Sutton Vol. II or Bernhard Vol. 2) for exact content of early 1925 conversation
4. Verify Muehlhausen (2017 or 2006, pp. 830-835) for Konstanz speech text
