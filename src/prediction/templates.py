TEMPLATE_PREDICTION_1 = """
# TASK: Experimental Design Generation (Type Q1)

## Overview
You will act as a Principal Investigator planning a scientific study. You will be provided with a specific research question or objective (`main_content`). Your task is to generate the logical reasoning required to design an experiment to address this objective. You must construct the "Inquiry Logic" triplet by generating the missing `context` and `outcome`.

## Logical Components

1. **Input: Research Goal (`main_content`)**
   This is the specific knowledge gap, hypothesis, or objective provided to you.

2. **Generate: Justification (`context`)**
   You must generate the scientific background or reasoning that makes the proposed experiment feasible or relevant. This should describe established biological principles, properties of specific model systems, or prior knowledge that serves as the foundation for the chosen method. Do not invent specific citations (e.g., "Ref: 12"), but rather state the general scientific consensus or established biological rule.

3. **Generate: Methodology (`outcome`)**
   You must generate the specific operational step, assay, or technique that creates the data necessary to answer the Research Goal. This should be a concrete action (e.g., "perform RNA-seq," "use CRISPR-Cas9 to knockout X," "stain with antibodies against Y") rather than a vague statement.

## Reasoning Flow
Your generation must follow this logical path:
*Because we want to know [main_content], and considering [context], we will perform [outcome].*

## Output Format
Return your response in the following JSON format:

```json
{
    "main_content": "The provided input goal",
    "context": "The scientific justification or background principle used to select the method.",
    "outcome": "The specific experimental method or assay performed."
}
```

**Input (Goal):** 
{{main_content}}
""".strip()

TEMPLATE_PREDICTION_2 = """
# TASK: Scientific Interpretation Generation (Type Q2)

## Overview
You will act as a Senior Scientific Reviewer analyzing raw data. You will be provided with a specific empirical observation or statistical result (`main_content`). Your task is to apply scientific theory to this observation to derive a meaningful conclusion. You must construct the "Discovery Logic" triplet by generating the missing `context` and `outcome`.

## Logical Components

1. **Input: Empirical Observation (`main_content`)**
   This is the specific data point, morphological description, or statistical finding provided to you.

2. **Generate: Established Principle (`context`)**
   You must generate the "lens" through which this data is interpreted. This should be an established biological rule, physical law, or known association (e.g., "It is well established that protein X is a marker for Y," or "Changes in nuclear shape are indicative of Z"). This provides the theoretical bridge between the raw number/image and its biological meaning.

3. **Generate: New Insight (`outcome`)**
   You must generate the novel conclusion or hypothesis that arises from combining the Observation with the Principle. This represents the new understanding or implication for the biological system (e.g., "Therefore, this suggests the pathway is upregulated," or "This indicates a transition to a mesenchymal state").

## Reasoning Flow
Your generation must follow this logical path:
*We observed [main_content]. Since it is known that [context], we conclude that [outcome].*

## Output Format
Return your response in the following JSON format:

```json
{
    "main_content": "The provided input observation",
    "context": "The general biological rule or established theory applied to the data.",
    "outcome": "The specific biological interpretation or conclusion derived."
}
```

**Input (Observation):** 
{{main_content}}
""".strip()

EXAMPLES_PREDICTION_1 = """
## Examples

### Example 1
**Input (Goal):** "To determine whether the canonical PKA–CREB axis is involved in CREM induction after NK cell activation"

**Output:**
```json
{
  "context": "Calcium is a known activator of PKA, which subsequently phosphorylates CREB to initiate transcription.",
  "outcome": "We measured phosphorylated CREB (pCREB) levels in NK cells using flow cytometry and western blot after CAR or IL-15 stimulation."
}
```

### Example 2
**Input (Goal):** "To test if mechanical confinement causes stable changes in gene expression"

**Output:**
```json
{
  "context": "The nucleus is the stiffest organelle in the cell, and prior studies suggest that physical deformation can alter chromatin accessibility.",
  "outcome": "We confined A375 cells in vitro using a polydimethylsiloxane piston system and performed bulk RNA-sequencing analysis."
}
```
""".strip()

EXAMPLES_PREDICTION_2 = """
## Examples

### Example 1
**Input (Observation):** "Motif enrichment analysis revealed that binding motifs for JUN-related factors were highly enriched in CREM KO cells compared with WT."

**Output:**
```json
{
  "context": "JUN-related factors form the AP-1 complex, which is a critical regulator of chromatin remodeling associated with long-lived memory T cell signatures.",
  "outcome": "This suggests that CREM functions as a negative regulator, and its removal allows for an epigenetic landscape that favors memory persistence."
}
```

### Example 2
**Input (Observation):** "In confined cells, tubacin treatment significantly increased the rate of nuclear HMGB2 accumulation."

**Output:**
```json
{
  "context": "Tubacin is a selective inhibitor of HDAC6, which leads to increased acetylation of alpha-tubulin and stabilization of the microtubule network.",
  "outcome": "These findings indicate that microtubule stability, rather than just the presence of the protein, is the key driver for HMGB2 nuclear localization under mechanical stress."
}
```
""".strip()