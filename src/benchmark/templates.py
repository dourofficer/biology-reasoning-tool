TEMPLATE_SUBPROBLEM_2 = """
*PAPER:*
{{paper}}

*TASK:*
Analyze the provided scientific paper. Your task is to act as a scientific editor and identify instances of a specific three-part logical argument structure that authors use to build their case. This structure connects their novel findings to established knowledge to propose a new hypothesis or conclusion.

Scan the Results section of the paper carefully to make sure you find all the instances. For each instance you find, extract the three components of this argument, which are defined as follows:

**1. Premise (The "What We Found"):**
*   **Definition:** An empirical result, observation, or data point generated *specifically within the current study*.
*   **Identifiers:** Look for direct statements of results ("We found that...", "Our analysis revealed..."), often linked to figures or tables from the current paper ("(Fig. 1a)", "(Extended Data Fig. 7a)").
*   **Constraint:** This component **must not** be a statement of established knowledge supported by a citation to *another paper*. If a sentence's primary purpose is to state a fact from the literature, it belongs in the Connecting Principle.
*   **Location:** Crucially, the premise might be ***implicit***. The authors may have established a finding in a previous paragraph and are now using it as the unspoken foundation for a new line of reasoning.

**2. Connecting Principle (The "Why It Matters"):**
*   **Definition:** A statement of pre-existing knowledge that acts as a logical bridge. It provides the established biological context or mechanism needed to understand the significance of the Premise.
*   **Identifiers:** This can be a specific mechanism from the literature ("Protein X is known to regulate Pathway Y `(Ref: 12)`"), a general, uncited biological fact ("The methionine cycle generates SAM"), or a summary of the current understanding of a disease ("The mechanism by which... is believed to be... `(Ref: 13, 17)`").
*   **Constraint:** This is the "lens" through which the new finding is interpreted. It is often, but not always, supported by citations to external literature.

**3. Interpretation (The "What It Means"):**
*   **Definition:** The novel conclusion, testable hypothesis, or new mechanistic explanation that emerges from combining the Premise with the Connecting Principle.
*   **Identifiers:** Look for forward-looking or inferential language: "Therefore, we hypothesized...", "These findings suggest that...", "This indicates that...", "A prediction based on this hypothesis is...". It often leads into a description of a follow-up experiment ("To test this...").
*   **Constraint:** This represents the author's intellectual contribution in the argument—the new idea they are proposing based on their data. While might be confusing, but this component IS NOT the experiment itself, it just states an interpretation, which means a conclusion or a hypothesis.

**Extraction Rules:**
*   **Verbatim Extraction:** Extract the text exactly as it appears in the document.
*   **Logical Flow:** The components do not need to be contiguous sentences, but they must form a coherent logical unit in the text.
*   **Implicit knowledge:** For any components that are implicit in the logic flow but can be found within the document, always make them explicit by extracting them verbatim from the document. Mark the implicit components with prefix "(implicit) ..." before reporting the content.
*   **Citations:** You must standardize all citations found within the extracted text to the format `(Ref: [numbers])`. This standardization does not conflict with the verbatim extraction rule and is prioritized.
    *   *Original:* "...methylation activity¹³,¹⁷." -> *Converted:* "...methylation activity `(Ref: 13, 17)`."
    *   *Original:* "...(H3K27me3) 25," -> *Converted:* "...(H3K27me3) `(Ref: 25)`,"

**Output Format:**
Report each instance in the following JSON format. Provide the context of where you find an instance before reporting it.

```json
{
  "premise_finding": "[Verbatim text of the result from the current study. If the premise is implicit, state 'Implicit finding:' followed by a concise summary of the finding from earlier in the text.]",
  "connecting_principle": "[Verbatim text of the established biological fact/mechanism]",
  "interpretation_hypothesis": "[Verbatim text of the resulting hypothesis or conclusion]"
}
```
""".strip()

TEMPLATE_SUBPROBLEM_2b = """
# PAPER EXCERPT:
{{paper}}

# TASK:
Analyze the provided scientific paper excerpt. Your task is to act as a scientific editor and identify instances of a specific three-part logical argument structure that authors use to build their case. This structure connects their novel findings to established knowledge to propose a new hypothesis or conclusion.

Scan the Results section of the paper carefully.

**Search Strategy:**
To successfully identify these arguments, follow this specific order of operations:
1.  **IDENTIFY THE INTERPRETATION FIRST.** Look for the conclusion, hypothesis, or inference. This component is the "anchor" of the argument and will always be explicit in the text.
2.  **Work Backwards.** Once you have isolated the interpretation, look immediately preceding it (or within the logical flow of the paragraph) to find the **Premise** (the specific data) and the **Connecting Principle** (the biological rule) that led to that conclusion.

**Component Definitions:**

**1. Premise (The "What We Found"):**
*   **Definition:** An empirical result, observation, or data point generated *specifically within the current study*.
*   **Identifiers:** Look for direct statements of results ("We found that...", "Our analysis revealed..."), often linked to figures or tables ("(Fig. 1a)").
*   **Constraint:** This component **must not** be a statement of established knowledge supported by a citation to *another paper*.
*   **Implicitness:** If the finding is established in a previous paragraph and acts as an unspoken foundation, or is simply understood from context without being restated, mark this component as `(implicit)`.

**2. Connecting Principle (The "Why It Matters"):**
*   **Definition:** A statement of pre-existing knowledge that acts as a logical bridge. It provides the established biological context or mechanism needed to understand the significance of the Premise.
*   **Identifiers:** Mechanisms from literature ("Protein X regulates Pathway Y `(Ref: 12)`") or general biological facts ("The methionine cycle generates SAM").
*   **Constraint:** This is the "lens" through which the new finding is interpreted.
*   **Implicitness:** If the biological mechanism or background knowledge is assumed to be known by the reader and not explicitly written, mark this component as `(implicit)`.

**3. Interpretation (The "What It Means") - FIND THIS FIRST:**
*   **Definition:** The novel conclusion, testable hypothesis, or new mechanistic explanation that emerges from combining the Premise with the Connecting Principle.
*   **Identifiers:** Look for forward-looking or inferential language: "Therefore, we hypothesized...", "These findings suggest that...", "This indicates that...", "A prediction based on this hypothesis is...", "Collectively, these data show...".
*   **Constraint:** This IS NOT the experiment itself; it is the *meaning* derived from the experiment. This component must be explicit.

**Extraction Rules:**
*   **Verbatim Extraction:** For explicit text, extract it exactly as it appears in the document.
*   **Logical Flow:** The components do not need to be contiguous sentences, but they must form a coherent logical unit.
*   **Implicit Content:** If a component (Premise or Connecting Principle) is implicit, do **not** try to find the text elsewhere or summarize it. Simply write `(implicit)`.
*   **Citations:** You must standardize all citations found within the extracted text to the format `(Ref: [numbers])`.
    *   *Original:* "...methylation activity¹³,¹⁷." -> *Converted:* "...methylation activity `(Ref: 13, 17)`."
    *   *Original:* "...(H3K27me3) 25," -> *Converted:* "...(H3K27me3) `(Ref: 25)`,"

**Output Format:**
Provide the analysis **strictly** as a valid JSON array containing objects. Do not include any conversational text, introductory remarks, or explanations outside the JSON code block. Use the exact keys provided below. IMPORTANT: If you cannot find any instances, return an empty array.

```json
[
  {
    "premise_finding": "[Verbatim text OR `(implicit)`]",
    "connecting_principle": "[Verbatim text OR `(implicit)`]",
    "interpretation": "[Verbatim text of the hypothesis/conclusion]"
  },
  {
    "premise_finding": "...",
    "connecting_principle": "...",
    "interpretation": "..."
  }
]
```

**Examples:**
```json
[
  {
    "premise_finding": "Analysis of our bulk RRBS and RNA-seq datasets also showed promoter hypermethylation and decreased expression of genes associated with 1C metabolism in Dnmt3aR878H/+ cells relative to Dnmt3a+/+ cells (Extended Data Fig. 7a). Notably, metformin treatment reversed these aberrant changes in DNA methylation and gene expression in mutant cells (Extended Data Fig. 7a).",
    "connecting_principle": "In human clonal haematopoiesis, the DNMT3A R882 mutation has previously been reported to result in preferential DNA hypomethylation of targets of the polycomb repressive complex 2 (PRC2) (Ref: 17), which catalyses the methylation of histone H3 K27 (H3K27). In addition, the Dnmt3aR878H mutation was previously found to be associated with a reduction in H3K27 trimethylation (H3K27me3) (Ref: 25), indicating its potential influence on another layer of epigenetic regulation.",
    "interpretation": "Given that PRC2-mediated methylation activity is also regulated by the [SAM]/[SAH] ratio, we hypothesized that metformin could reverse the aberrant H3K27 hypomethylation profile in Dnmt3aR878H/+ HSPCs."
  },
  {
    "premise_finding": "Of note, 4 out of the 8 up-regulated metabolites (L-cysteate, dimethylglycine, reduced glutathione (GSH) and taurine) are involved in one-carbon (1C) metabolism through the methionine cycle (Fig. 3a,b).",
    "connecting_principle": "Since the methionine cycle generates SAM,",
    "interpretation": "these findings suggest that metformin could potentially affect SAM levels and the ratio of SAM to SAH, which is also known as the methylation index, an indicator of cellular methylation potential."
  },
  {
    "premise_finding": "(implicit)",
    "connecting_principle": "The mechanism by which DNMT3A mutations confer a competitive advantage to mutant HSCs is believed to be mediated through focal DNA hypomethylation secondary to reduced de novo DNA methylation activity (Ref: 13, 17). In the context of DNMT3A R882 mutants in which a copy of the wild-type gene remains, the residual DNA methylation activity is estimated to be around 20% of normal, but is not absent (Ref: 13).",
    "interpretation": "We hypothesized that the metformin-induced increase in methylation index could augment this activity, resulting in a reversal of the aberrant DNA CpG hypomethylation pattern in mutant cells and consequent decrease in their competitive advantage. A prediction based on this hypothesis is that elimination of residual DNMT3A activity by inactivating the remaining wild-type Dnmt3a allele in mutant cells should render them resistant to the effect of metformin."
  }
]
```
""".strip()

TEMPLATE_SUBPROBLEM_2c = """
# PAPER EXCERPT:
{{paper}}

# TASK:
Analyze the provided scientific paper excerpt. Your task is to act as a scientific editor and identify instances of a specific three-part logical argument structure that authors use to build their case. This structure connects their novel findings to established knowledge to propose a new hypothesis or conclusion.

Scan the Results section of the paper carefully.

**Component Definitions:**

**1. Premise (The "What We Found"):**
*   **Definition:** An empirical result, observation, or data point generated *specifically within the current study*.
*   **Identifiers:** Look for direct statements of results ("We found that...", "Our analysis revealed..."), often linked to figures or tables ("(Fig. 1a)").
*   **Constraint:** This component **must not** be a statement of established knowledge supported by a citation to *another paper*.
*   **Implicitness:** If the finding is established in a previous paragraph and acts as an unspoken foundation, or is simply understood from context without being restated, mark this component as `(missing)`.

**2. Connecting Principle (The "Why It Matters"):**
*   **Definition:** A statement of pre-existing knowledge that acts as a logical bridge. It provides the established biological context or mechanism needed to understand the significance of the Premise.
*   **Identifiers:** Mechanisms from literature ("Protein X regulates Pathway Y `(Ref: 12)`") or general biological facts ("The methionine cycle generates SAM").
*   **Constraint:** This is the "lens" through which the new finding is interpreted.
*   **Implicitness:** If the biological mechanism or background knowledge is assumed to be known by the reader and not explicitly written, mark this component as `(missing)`.

**3. Interpretation (The "What It Means") - FIND THIS FIRST:**
*   **Definition:** The novel conclusion, testable hypothesis, or new mechanistic explanation that emerges from combining the Premise with the Connecting Principle.
*   **Identifiers:** Look for forward-looking or inferential language: "Therefore, we hypothesized...", "These findings suggest that...", "This indicates that...", "A prediction based on this hypothesis is...", "Collectively, these data show...".
*   **Constraint:** This IS NOT the experiment itself; it is the *meaning* derived from the experiment. This component must be explicit.

**Search Strategy:**
To successfully identify these arguments, you must analyze the text subsection by subsection. For each subsection, follow this specific order of operations:
1.  **IDENTIFY THE INTERPRETATION FIRST.** Look for the conclusion, hypothesis, or inference. This component is the "anchor" of the argument and will always be explicit in the text.
2.  **Work Backwards.** Once you have isolated the interpretation, look immediately preceding it (or within the logical flow of the paragraph) to find the **Premise** (the specific data) and the **Connecting Principle** (the biological rule) that led to that conclusion.
3.  **Assess Presence.** If a component (Premise or Connecting Principle) is not explicitly stated in the text—whether it is understood from context, implied, or simply missing—mark that specific component as `(implicit)`.

**Extraction Rules:**
*   **Verbatim Extraction:** For explicit text, extract it exactly as it appears in the document.
*   **Logical Flow:** The components do not need to be contiguous sentences, but they must form a coherent logical unit.
*   **Implicit/Missing Content:** If a component is not found explicitly, do **not** try to find the text elsewhere or summarize it. Simply write `(missing)`.

**Output Format:**
Provide the analysis **strictly** as a valid JSON array containing objects. Do not include any conversational text, introductory remarks, or explanations outside the JSON code block.

Use the nested format below, grouping findings by their specific subsection header. IMPORTANT: If you cannot find any instances in a subsection, return an empty `triplets` array for that section.

```json
[
  {
    "subsection": "[Subsection Header Name]",
    "triplets": [
        {
            "premise_finding": "[Verbatim text OR `(missing)`]",
            "connecting_principle": "[Verbatim text OR `(missing)`]",
            "interpretation": "[Verbatim text of the hypothesis/conclusion]"
        },
        {
            "premise_finding": "...",
            "connecting_principle": "...",
            "interpretation": "..."
        }
    ]
  },
  {
    "subsection": "[Next Subsection Header Name]",
    "triplets": []
  }
]
```

Examples for a list of triplets:
```
[
  {
    "premise_finding": "Analysis of our bulk RRBS and RNA-seq datasets also showed promoter hypermethylation and decreased expression of genes associated with 1C metabolism in Dnmt3aR878H/+ cells relative to Dnmt3a+/+ cells (Extended Data Fig. 7a). Notably, metformin treatment reversed these aberrant changes in DNA methylation and gene expression in mutant cells (Extended Data Fig. 7a).",
    "connecting_principle": "In human clonal haematopoiesis, the DNMT3A R882 mutation has previously been reported to result in preferential DNA hypomethylation of targets of the polycomb repressive complex 2 (PRC2) (Ref: 17), which catalyses the methylation of histone H3 K27 (H3K27). In addition, the Dnmt3aR878H mutation was previously found to be associated with a reduction in H3K27 trimethylation (H3K27me3) (Ref: 25), indicating its potential influence on another layer of epigenetic regulation.",
    "interpretation": "Given that PRC2-mediated methylation activity is also regulated by the [SAM]/[SAH] ratio, we hypothesized that metformin could reverse the aberrant H3K27 hypomethylation profile in Dnmt3aR878H/+ HSPCs."
  },
  {
    "premise_finding": "Of note, 4 out of the 8 up-regulated metabolites (L-cysteate, dimethylglycine, reduced glutathione (GSH) and taurine) are involved in one-carbon (1C) metabolism through the methionine cycle (Fig. 3a,b).",
    "connecting_principle": "Since the methionine cycle generates SAM,",
    "interpretation": "these findings suggest that metformin could potentially affect SAM levels and the ratio of SAM to SAH, which is also known as the methylation index, an indicator of cellular methylation potential."
  },
  {
    "premise_finding": "(missing)",
    "connecting_principle": "The mechanism by which DNMT3A mutations confer a competitive advantage to mutant HSCs is believed to be mediated through focal DNA hypomethylation secondary to reduced de novo DNA methylation activity (Ref: 13, 17). In the context of DNMT3A R882 mutants in which a copy of the wild-type gene remains, the residual DNA methylation activity is estimated to be around 20% of normal, but is not absent (Ref: 13).",
    "interpretation": "We hypothesized that the metformin-induced increase in methylation index could augment this activity, resulting in a reversal of the aberrant DNA CpG hypomethylation pattern in mutant cells and consequent decrease in their competitive advantage. A prediction based on this hypothesis is that elimination of residual DNMT3A activity by inactivating the remaining wild-type Dnmt3a allele in mutant cells should render them resistant to the effect of metformin."
  }
]
```
"""