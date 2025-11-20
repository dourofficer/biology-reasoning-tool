```python
template = """
You are an expert academic assistant specializing in scientific text analysis. Your task is to extract the "Background," "Research Question," and "Experiment Approach" from the introductory paragraphs of a scientific paper.

Your extraction must adhere to the following principles:

1.  **Semantic Focus:** Analyze the logical flow of the argument. Do not rely on simple structural cues like paragraph order or sentence position. The goal is to identify the function of the text.
2.  **Component Definitions:**
    *   **Background:** Extract the sentences that establish the context, summarize the current state of knowledge, and define the central problem or challenge in the field. This section sets the stage for why the research is necessary.
    *   **Research Question:** Isolate the specific gap in knowledge or the critical unmet need that the paper aims to address. This should articulate the central "unknown" that motivates the study. **Crucially, distinguish the research gap from the summary of the paper's findings or methods.**
    *   **Experiment:** Identify the sentences that describe the study's core methodology, model system, or overall strategy used to answer the research question. This section should capture the *'how'* of the research as presented in the introduction. **Avoid sentences that describe the results or conclusions** (e.g., "we found that..."); focus only on the description of the action taken or the system used.
3.  **Extraction Nature:** The extracted text should be taken out of the given text verbatim. The extracted text for each section can be composed of scattered, non-contiguous sentences from the provided introduction.

Analyze the user-provided text below. Then, use the provided example as a guide to produce the final output for the new input text.

---

### **Example for Guidance:**

**INPUT:**
<input>
Monocyte-derived macrophages (mo-macs) drive immunosuppression in the tumor microenvironment (TME) and tumor-enhanced myelopoiesis in the bone marrow (BM) fuels these populations. Here, we performed paired transcriptome and chromatin analysis over the continuum of BM myeloid progenitors, circulating monocytes, and tumor-infiltrating mo-macs in mice and in patients with lung cancer to identify myeloid progenitor programs that fuel pro-tumorigenic mo-macs. Analyzing chromatin accessibility and histone mark changes, we show that lung tumors prime accessibility for Nfe2l2 (NRF2) in BM myeloid progenitors as a cytoprotective response to oxidative stress. NRF2 activity is sustained and increased during monocyte differentiation into mo-macs in the lung TME to regulate oxidative stress, in turn promoting metabolic adaptation, resistance to cell death, and contributing to immunosuppressive phenotype. NRF2 genetic deletion and pharmacological inhibition significantly reduced mo-macs’ survival and immunosuppression in the TME, enabling NK and T cell therapeutic antitumor immunity and synergizing with checkpoint blockade strategies. Altogether, our study identifies a targetable epigenetic node of myeloid progenitor dysregulation that sustains immunoregulatory mo-macs in the TME.

A major focus in cancer immunotherapy has been reprogramming monocyte-derived macrophages (mo-macs) in the tumor microenvironment (TME) of solid tumors to reverse immunosuppression and unleash T cell/NK cell responses [1]. While this TME-centric approach has considerable merit, it fails to tackle the ‘wellspring’ of bone marrow (BM) myeloid progenitors seeding monocytes and mo-macs in the TME via tumor-driven myelopoiesis [2-5]. Demand-adapted myelopoietic mobilization during infection/trauma is linked to transcriptomic changes in BM myeloid progenitors enabling their expansion and survival [6-8], but we have not yet deciphered the exact nature of epigenetic and metabolic changes that occur in myeloid progenitors and mo-mac progeny during tumor-induced myelopoiesis. As our view of systemic tumor–host crosstalk expands, it becomes important to understand if and how complex tumoral cues can ‘pre-condition’ myeloid progenitors in BM by altering their chromatin states, priming gene programs of immunoregulation and undermining anti-tumor responses. Understanding such regulation during chronic tumor inflammation is key to therapeutically targeting the mo-mac replenishment cycle and developing more durable myeloid-targeting therapies. Here, we sought to identify genetic and epigenetic changes that prime myeloid progenitors in tumor-bearing hosts, probe their contribution to tumorigenic immunoregulatory mo-mac plasticity in the TME, and harness this knowledge to redirect TME mo-mac fate towards an anti-tumor phenotype.
</input>

**OUTPUT:**
<output>
Background: 
A major focus in cancer immunotherapy has been reprogramming monocyte-derived macrophages (mo-macs) in the tumor microenvironment (TME) of solid tumors to reverse immunosuppression and unleash T cell/NK cell responses [1]. While this TME-centric approach has considerable merit, it fails to tackle the ‘wellspring’ of bone marrow (BM) myeloid progenitors seeding monocytes and mo-macs in the TME via tumor-driven myelopoiesis [2-5]. Demand-adapted myelopoietic mobilization during infection/trauma is linked to transcriptomic changes in BM myeloid progenitors enabling their expansion and survival [6-8], but we have not yet deciphered the exact nature of epigenetic and metabolic changes that occur in myeloid progenitors and mo-mac progeny during tumor-induced myelopoiesis. 

Research question: 
As our view of systemic tumor–host crosstalk expands, it becomes important to understand if and how complex tumoral cues can ‘pre-condition’ myeloid progenitors in BM by altering their chromatin states, priming gene programs of immunoregulation and undermining anti-tumor responses.

Experiment:
Here, we performed paired transcriptome and chromatin analysis over the continuum of BM myeloid progenitors, circulating monocytes, and tumor-infiltrating mo-macs in mice and in patients with lung cancer to identify myeloid progenitor programs that fuel pro-tumorigenic mo-macs.
</output>
---

### **New Task:**

**INPUT:**
<input>
{{text}}
</input>
"""
```

>>> INPUT
Signals from the microenvironment are known to be critical for development, stem cell self-renewal and oncogenic progression. Although some niche-driven signals that promote cancer progression have been identified [1-5], concerted efforts to map disease-relevant microenvironmental ligands of cancer stem cell receptors have been lacking. Here, we use temporal single-cell RNA-sequencing (scRNA-seq) to identify molecular cues from the bone marrow stromal niche that engage leukaemia stem-enriched cells (LSCs) during oncogenic progression. We integrate these data with our human LSC RNA-seq and in vivo CRISPR screen of LSC dependencies [6] to identify LSC–niche interactions that are essential for leukaemogenesis. These analyses identify the taurine–taurine transporter (TAUT) axis as a critical dependency of aggressive myeloid leukaemias. We find that cysteine dioxygenase type 1 (CDO1)-driven taurine biosynthesis is restricted to osteolineage cells, and increases during myeloid disease progression. Blocking CDO1 expression in osteolineage cells impairs LSC growth and improves survival outcomes. Using TAUT genetic loss-of-function mouse models and patient-derived acute myeloid leukaemia (AML) cells, we show that TAUT inhibition significantly impairs in vivo myeloid leukaemia progression. Consistent with elevated TAUT expression in venetoclax-resistant AML, TAUT inhibition synergizes with venetoclax to block the growth of primary human AML cells. Mechanistically, our multiomic approaches indicate that the loss of taurine uptake inhibits RAG–GTP dependent mTOR activation and downstream glycolysis. Collectively, our work establishes the temporal landscape of stromal signals during leukaemia progression and identifies taurine as a key regulator of myeloid malignancies.


Signals from the tumour microenvironment (TME) can regulate initiation, progression and immune evasion of tumours [1-5, 7-10]. While scRNA-seq analysis has identified cellular TME components, especially in solid tumours [11, 12], concerted efforts to link ligands from the changing TME landscape with cognate receptors on cancer cells have been lacking. As cell surface proteins are particularly amenable to therapeutic targeting, functional characterization of their interactions with the TME are of considerable clinical interest. 

Aggressive therapy-resistant myeloid leukaemias, such as blast-crisis-phase chronic myeloid leukaemia (bcCML) and AML, initiate and expand in a complex bone marrow microenvironment. Although previous studies have described the cellular composition of normal bone marrow niche [13-15], their dynamic alterations during leukaemia progression remain undefined. We use scRNA-seq to establish temporal changes in bone marrow microenvironment populations, and in niche-driven signals during disease progression. To define TME ligands that are essential for leukaemogenesis, we focused on cognate cell surface receptors enriched in LSCs as compared to healthy controls, and those essential for in vivo leukaemia progression [6]. This approach identified signals that are known to be critical for cancer growth, such as KIT–KITL and CD47–thrombospondin 1 [16], as well as multiple new signalling axes.

Of these signals, TAUT, encoded by SLC6A6, was strongly associated with poor prognosis in human leukaemias and emerged as a key regulator of AML. As taurine can be neuroprotective, mitigate the side-effects of chemotherapy [17] or support anti-cancer immunity [18], a cancer-promoting role of taurine has not been considered. We examined if blocking taurine production in the TME impairs LSC function. We used genetic tools to establish whether TAUT expression in cancer cells controls the growth of aggressive myeloid leukaemias. Using metabolomic, proteomic and transcriptomic approaches, we identify downstream mechanisms by which taurine regulates leukaemia growth.

>>> OUTPUT (gemini-2.5-pro)
Background: 
Signals from the microenvironment are known to be critical for development, stem cell self-renewal and oncogenic progression. Signals from the tumour microenvironment (TME) can regulate initiation, progression and immune evasion of tumours [1-5, 7-10]. Aggressive therapy-resistant myeloid leukaemias, such as blast-crisis-phase chronic myeloid leukaemia (bcCML) and AML, initiate and expand in a complex bone marrow microenvironment. As cell surface proteins are particularly amenable to therapeutic targeting, functional characterization of their interactions with the TME are of considerable clinical interest.

Research question: 
While scRNA-seq analysis has identified cellular TME components, especially in solid tumours [11, 12], concerted efforts to link ligands from the changing TME landscape with cognate receptors on cancer cells have been lacking. Although previous studies have described the cellular composition of normal bone marrow niche [13-15], their dynamic alterations during leukaemia progression remain undefined.

Experiment:
Here, we use temporal single-cell RNA-sequencing (scRNA-seq) to identify molecular cues from the bone marrow stromal niche that engage leukaemia stem-enriched cells (LSCs) during oncogenic progression. To define TME ligands that are essential for leukaemogenesis, we focused on cognate cell surface receptors enriched in LSCs as compared to healthy controls, and those essential for in vivo leukaemia progression [6]. We used genetic tools to establish whether TAUT expression in cancer cells controls the growth of aggressive myeloid leukaemias.
