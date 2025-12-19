# Experimental Framework For Pathway Discovery

This document outlines a standard scientific framework used to move from a simple observation of correlation to a well-supported, specific causal mechanism. We often start by noticing that two events are linked, but the real challenge is to understand *how* and *why* they are linked.

We will use the following abstract model:
*   **X**: The initial cause or condition (e.g., a genetic mutation).
*   **Y**: The final observed outcome or phenotype (e.g., a disease state).
*   **A**: A potential intermediate biological process or molecule that connects X and Y.

### The Starting Point: Observation

We begin with a simple, reproducible observation that suggests a relationship between `X` and `Y`. This establishes a correlation, but it does not prove causation or reveal the mechanism.

*   **Logic:** When `X` is absent, `Y` is also absent. When `X` is present, `Y` is also present.
*   **Notation:**
    *   `X^off` -> `Y^off`
    *   `X^on` -> `Y^on`

**Example:**
*   **Observation:** In hematopoietic stem and progenitor cells (HSPCs):
    1.  Cells without a `DNMT3A R878H` mutation (`X^off`) do not show abnormal expansion (`Y^off`).
    2.  Cells with a `DNMT3A R878H` mutation (`X^on`) show abnormal expansion (`Y^on`).

### Experiment 1: Candidate Screening

**Goal:** To identify a plausible biological mechanism (`A`) that could mediate the effect of `X` on `Y`.

*   **Hypothesis:** The biological process `A` is correlated with, and potentially mediates, the effect of `X` on `Y`. The proposed pathway is `X -> A -> Y`.
*   **Methodology:** Observe the state of the candidate mechanism `A` when `X` is present versus absent.
*   **Interpretation:**
    *   **Hypothesis Supported:** If `X^on` is consistently associated with `A^on`, and `X^off` with `A^off`, then `A` is a strong candidate mediator. The results are consistent with the `X -> A -> Y` model.
    *   **Hypothesis Rejected:** If the state of `A` does not change with the state of `X`, then `A` is unlikely to be on the direct causal pathway. We must search for a different candidate.

**Example:**
*   **Hypothesis:** Increased oxidative phosphorylation (OXPHOS) mediates the effect of the `DNMT3A R878H` mutation on HSPC expansion. Here, `A` is OXPHOS.
*   **Test:**
    1.  In cells without the mutation (`X^off`), we observe normal levels of OXPHOS (`A^off`) and no HSPC expansion (`Y^off`).
    2.  In cells with the mutation (`X^on`), we observe a significant increase in OXPHOS (`A^on`), which is correlated with HSPC expansion (`Y^on`).
*   **Conclusion:** The hypothesis is supported. OXPHOS is now a strong candidate for the mechanism.

### Experiment 2: Perturbation Experiment (to Confirm Necessity)

**Goal:** To test if the candidate mechanism `A` is *required* for `X` to cause `Y`. This experiment directly tests the causal link.

*   **Hypothesis:** `A` is a necessary component in the causal pathway from `X` to `Y`.
*   **Methodology:** Induce the `X^on` state, but simultaneously inhibit or remove `A` (e.g., using a chemical inhibitor or gene deletion).
*   **Interpretation:**
    *   **Hypothesis Supported:** If `X^on` + `A^off` -> `Y^off`, it demonstrates that `A` is required for the signal to pass from `X` to `Y`. The causal chain is broken without `A`, strengthening our confidence in the `X -> A -> Y` model.
    *   **Hypothesis Rejected:** If `X^on` + `A^off` -> `Y^on`, it demonstrates that `A` is *not* necessary. `X` must be causing `Y` through an alternate, parallel pathway (`B`) that does not involve `A`. Our initial model is incorrect.

**Example:**
*   **Hypothesis:** OXPHOS is necessary for the `DNMT3A R878H` mutation to drive HSPC expansion.
*   **Test:** We take cells with the mutation (`X^on`) and treat them with a drug (like metformin) that inhibits OXPHOS, effectively turning `A` off.
*   **Result:** `DNMT3A R878H` mutation (`X^on`) + OXPHOS inhibition (`A^off`) -> no/less HSPC expansion (`Y^off`).
*   **Conclusion:** The hypothesis is supported. This confirms that OXPHOS activity is a necessary step for the mutation to cause expansion.

### Experiment 3: Rescue/Complementation Experiment (to Confirm Specificity)

**Goal:** To confirm that the result from Experiment 2 was specifically due to the inhibition of `A` and not an unforeseen "off-target" effect of our intervention.

*   **Hypothesis:** The inhibition of `Y` observed in Experiment 2 was caused *specifically* by blocking `A`.
*   **Methodology:** Repeat the perturbation experiment (`X^on` + `A` blocked), but this time re-introduce a modified version of `A` that is resistant to the block.
*   **Interpretation:**
    *   **Hypothesis Supported (Successful Rescue):** If `X^on` + `A^blocked` + `A^rescued` -> `Y^on`, it confirms that our inhibitor's effect on `Y` was specifically mediated through `A`. This result provides very strong evidence for the `X -> A -> Y` causal model by ruling out off-target effects.
    *   **Hypothesis Rejected (Failed Rescue):** If `X^on` + `A^blocked` + `A^rescued` -> `Y^off`, the hypothesis of specificity is rejected. This implies that the agent used to block `A` also independently inhibits another factor (`B`) that is *also* necessary for `Y`. Our model is incomplete.

**Example:**
*   **Hypothesis:** Metformin blocks HSPC expansion specifically by inhibiting OXPHOS.
*   **Test:** We take cells with the `DNMT3A R878H` mutation (`X^on`) and treat them with metformin (`A` is blocked). Then, we introduce a modified, metformin-resistant version of an OXPHOS subunit (`A^rescued`).
*   **Result:** `DNMT3A R878H` (`X^on`) + metformin (`A` blocked) + metformin-resistant OXPHOS (`A^rescued`) -> HSPC expansion is restored (`Y^on`).
*   **Conclusion:** The hypothesis is supported. This confirms that metformin's effect was specific to OXPHOS, solidifying the complete causal link: `DNMT3A R878H -> increased OXPHOS -> HSPC expansion`.

### Experiment 4: Orthogonal Validation (to Confirm Generalizability)

**Goal:** To confirm that the `X -> A -> Y` pathway is a robust biological phenomenon and not an artifact of a specific experimental model, assay, or condition. This step ensures the finding is generalizable.

*   **Hypothesis:** The `X -> A -> Y` causal pathway holds true across different biological contexts and measurement techniques.
*   **Methodology:** Re-test the key links of the pathway using fundamentally different approaches. Examples include:
    *   **Different Biological Models:** Move from cell lines to more complex systems like patient-derived organoids, primary human cells, or an *in vivo* animal model (e.g., a knock-in mouse).
    *   **Different Measurement Techniques:** If the initial finding was based on RNA levels (e.g., RNA-seq), validate it at the protein level (e.g., Western Blot, IHC, flow cytometry) or by measuring functional activity.
    *   **Independent Datasets:** For clinical or genomic findings, test the correlation in an independent patient cohort or a publicly available dataset.
*   **Interpretation:**
    *   **Hypothesis Supported (Successful Validation):** If the key relationships (`X->A`, `A->Y`) are confirmed in a different system, it provides powerful evidence that the pathway is a fundamental and robust biological mechanism, greatly increasing confidence in its relevance.
    *   **Hypothesis Rejected (Failed Validation):** If the pathway is not recapitulated, it suggests the mechanism is context-dependent (e.g., specific to the cell line used, or only observable *in vitro*). This result is also valuable as it defines the boundaries and limitations of the discovery.

**Example:**
*   **Hypothesis:** The `DNMT3A R878H -> OXPHOS -> HSPC expansion` pathway is relevant *in vivo* and in patients.
*   **Test:**
    1.  **Animal Model:** Create a knock-in mouse model with the `DNMT3A R878H` mutation. Measure OXPHOS activity and HSPC counts in the bone marrow of these mice compared to wild-type mice.
    2.  **Patient Samples:** Obtain bone marrow samples from patients with known `DNMT3A` mutations. Use flow cytometry to measure OXPHOS activity in their HSPCs and correlate this with clinical data on clonal expansion.
*   **Result:** The `DNMT3A R878H` mice (`X^on`) show elevated OXPHOS in HSPCs (`A^on`) and increased HSPC counts (`Y^on`) compared to wild-type mice. Patient samples confirm a strong correlation between the mutation, high OXPHOS, and expansion.
*   **Conclusion:** The hypothesis is supported. The pathway is validated in an *in vivo* model and in primary human cells, confirming its physiological and clinical relevance.

## Summary of the Logic

| Step | Goal | Hypothesis Tested | Interpretation if Supported | Interpretation if Rejected |
| :--- | :--- | :--- | :--- | :--- |
| **Observation** | Establish Correlation | `X` and `Y` are related. | The events are linked; further investigation is warranted. | The events are unrelated. |
| **1. Candidate Screen** | Identify a Mediator | `A` is correlated with the `X -> Y` relationship. | `A` is a plausible candidate mechanism. | `A` is not the correct mechanism; find a new candidate. |
| **2. Perturbation** | Confirm Necessity | `A` is necessary for `X` to cause `Y`. | The `X -> A -> Y` causal link is supported in this system. | `A` is not necessary; `X` acts through a parallel pathway. |
| **3. Rescue** | Confirm Specificity | The perturbation effect in Exp. 2 was specifically due to inhibiting `A`. | The `X -> A -> Y` model is robust and specific in this system. | The inhibitor has off-target effects; the model is more complex. |
| **4. Orthogonal Validation** | Confirm Generalizability | The `X -> A -> Y` pathway is not an artifact of the model or assay. | The pathway is a robust, fundamental biological mechanism. | The pathway is context-dependent; its scope is limited. |