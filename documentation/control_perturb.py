template = """
TASK: Extract all control and perturbed condition pairs from the Methods section of a molecular biology research paper.

---
DEFINITIONS
---

CONTROL CONDITION:
The baseline experimental setup. Includes cell line/organism/tissue (e.g., "HEK293", "mouse liver", "C. elegans") and standard/untreated state.

PERTURBED CONDITION:
The experimental manipulation applied to the system:
- Genetic: knockdown (KD), knockout (KO), overexpression (OE), mutation
- Chemical: drug/compound treatment
- Physical: heat shock, radiation, starvation
- Biological: infection, differentiation, stimulation
- If no perturbation exists, output "None"

---
IMPORTANT NOTES
---

• A paper may contain MULTIPLE experiments with different control-perturbation pairs
• A paper may contain NO perturbations (observational/profiling studies)
• Extract ALL pairs mentioned in the Methods section
• Each control-perturbation combination is a separate row in the output table

---
EXTRACTION STEPS
---

1. LOCATE relevant Methods subsections:
   "Cell culture", "Gene editing", "CRISPR", "RNA interference", "Transfection", "Treatments", "RNA-seq", "Experimental design"

2. IDENTIFY ALL EXPERIMENTS:
   Look for phrases indicating multiple experiments:
   - "In parallel experiments..."
   - "Additionally, we..."
   - "For comparison, we also..."
   - Multiple cell lines with different treatments
   - Time series or dose-response studies

3. FOR EACH EXPERIMENT, EXTRACT:
   
   CONTROL:
   - Cell/organism name, "wild-type", "untreated", "non-targeting control", "vehicle"
   - Format: [Cell line/organism]
   
   PERTURBATION:
   - Knockdown (siRNA/shRNA/CRISPRi) → "[GENE] KD"
   - Knockout (CRISPR/deletion/-/-) → "[GENE] KO"
   - Overexpression → "[GENE] OE"
   - Chemical treatment → "treated with [compound]"
   - Other manipulations → describe concisely
   - No manipulation → "None"

4. HANDLE SPECIAL CASES:
   
   Multiple perturbations on SAME control:
   → Create separate rows for each perturbation
   
   SAME perturbation on multiple controls:
   → Create separate rows for each control
   
   Multiple perturbations tested together:
   → List as single perturbation with comma separation
   
   No perturbation (profiling study):
   → Single row with "None" as perturbation

---
STANDARDIZATION
---

- Gene symbols: uppercase for human, capitalized for mouse
- Abbreviations: KD, KO, OE
- Be concise but specific
- No extra punctuation or descriptions

---
VALIDATION
---

✓ Each row is ONE control-perturbation pair
✓ Control = cell/organism, NOT procedure
✓ Perturbation = biological manipulation, NOT assay
✓ All experiments mentioned in Methods are captured
✓ Vehicle/DMSO is control, not perturbation

---
OUTPUT FORMAT (REQUIRED)
---

Respond with ONLY a markdown table in this exact format:

| Control | Perturbation |
|---------|--------------|
| [control 1] | [perturbation 1] |
| [control 2] | [perturbation 2] |
| ... | ... |

If NO experiments are described or text is unclear, output:

| Control | Perturbation |
|---------|--------------|
| Not specified | Not specified |

---
EXAMPLES
---

Example 1 - Single experiment:
Input: "HeLa cells were transfected with siRNA targeting PKM2 or non-targeting control."
Output:
| Control | Perturbation |
|---------|--------------|
| HeLa | PKM2 KD |

Example 2 - Multiple perturbations on same control:
Input: "A549 cells were transfected with siRNA targeting FOXA1, FOS, or non-targeting control."
Output:
| Control | Perturbation |
|---------|--------------|
| A549 | FOXA1 KD |
| A549 | FOS KD |

Example 3 - Multiple controls with same perturbation:
Input: "HEK293 and HeLa cells were transduced with ZNF645 lentivirus or empty vector."
Output:
| Control | Perturbation |
|---------|--------------|
| HEK293 | ZNF645 OE |
| HeLa | ZNF645 OE |

Example 4 - Multiple perturbations tested together:
Input: "E14 mESCs with double knockout of PATZ1 and ZNF263 were generated using CRISPR."
Output:
| Control | Perturbation |
|---------|--------------|
| E14 mESCs | PATZ1 KO, ZNF263 KO |

Example 5 - Multiple independent experiments:
Input: "MEFs were either treated with etoposide (50μM) or left untreated. Separately, OPA1-/- MEFs were compared to wild-type."
Output:
| Control | Perturbation |
|---------|--------------|
| MEF | treated with etoposide |
| MEF | OPA1-/- |

Example 6 - No perturbation:
Input: "RNA-seq was performed on HEK293 cells cultured under standard conditions to profile baseline gene expression."
Output:
| Control | Perturbation |
|---------|--------------|
| HEK293 | None |

Example 7 - Complex multi-experiment study:
Input: "K562 cells were treated with IRF2 siRNA. In parallel, A549 cells were infected with FOS-expressing lentivirus or empty vector."
Output:
| Control | Perturbation |
|---------|--------------|
| K562 | IRF2 KD |
| A549 | FOS OE |

---
YOUR TASK
---

Read the Methods section below and extract ALL control-perturbation pairs.

{{methods}}
""".strip()