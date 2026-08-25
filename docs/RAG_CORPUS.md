# Bundled RAG corpus manifest

This manifest records what can be established from the files committed to this
repository. The corpus is a 49-chunk demo/evaluation fixture, not a clinical
knowledge base. It must not be used to make diagnosis or treatment decisions.

The twelve Markdown files under `docs/rag/` appear to be condensed,
locally-formatted summaries or transformations of the sources named inside
them. The repository does not document who produced each transformation,
whether every statement was checked against the cited source, or whether text
was copied verbatim in places. The original publications are not bundled.

Unless a row says otherwise, redistribution status is **not independently
verified**. A public URL, DOI, “open access” label, or the repository's MIT
license does not by itself establish permission to redistribute underlying
third-party material.

## Cited-source summaries

| Local file | Source recorded in file | Organization / author | Year/version | Form in repository | Rights status |
| --- | --- | --- | --- | --- | --- |
| `docs/rag/guidelines/2016_NICE_NG95_Chest-Pain.md` | [NICE CG95: Recent-onset chest pain](https://www.nice.org.uk/guidance/cg95) | National Institute for Health and Care Excellence | 2016 update of 2010 guidance | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/guidelines/2018_ACEP_Chest-Pain-Policy.md` | [ACEP clinical policy PDF](https://www.acep.org/siteassets/sites/acep/blocks/equal/webinar_chestpainw2_aceppolicy.pdf) | American College of Emergency Physicians; *Annals of Emergency Medicine* | 2018 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/guidelines/2021_ACC-AHA_Chest-Pain_exec.md` | [2021 chest-pain guideline executive summary](https://doi.org/10.1016/j.jacc.2021.07.052) | ACC/AHA; *JACC/Circulation* | 2021 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/guidelines/2025_ESC_0-1h-hsTroponin.md` | [Chen et al., AnZhen 0/1-hour adaptation](https://doi.org/10.1038/s44325-025-00080-8) | Chen et al.; *npj Cardiovascular Health* | 2025 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/reviews/2000_TIMI-UA-NSTEMI.md` | [Antman et al., TIMI risk score](https://doi.org/10.1001/jama.284.7.835) plus an unnamed Cleveland Clinic summary | Antman et al.; *JAMA* | 2000 | condensed Markdown summary/transformation | not independently verified; second source URL absent |
| `docs/rag/reviews/2013_HEART-Score.md` | [Backus et al., HEART validation](https://doi.org/10.1016/j.ijcard.2013.01.255) | Backus et al.; *International Journal of Cardiology* | 2013 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/reviews/2014_EDACS-Score.md` | [Than et al., EDACS validation](https://doi.org/10.1016/j.annemergmed.2014.02.010) | Than et al.; *Annals of Emergency Medicine* | 2014 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/reviews/2020_PERC-Wells.md` | [NCBI Bookshelf evidence review](https://www.ncbi.nlm.nih.gov/books/NBK556663/) | NCBI Bookshelf; author not recorded locally | 2020 | condensed Markdown summary/transformation | not independently verified |
| `docs/rag/tools/2010_Noncardiac-Chest-Pain_Overview.md` | [Open-access narrative review](https://pmc.ncbi.nlm.nih.gov/articles/PMC3093002/) | author not recorded locally | 2010 inferred from filename | condensed Markdown summary/transformation | source is labeled open access locally; redistribution terms not independently verified |
| `docs/rag/tools/2022_ACC_Ambulatory-LowRisk-Pathways.md` | [ACC expert consensus decision pathway](https://pmc.ncbi.nlm.nih.gov/articles/PMC10691881/) | American College of Cardiology; author not recorded locally | 2022 | condensed Markdown summary/transformation | source is labeled open access locally; redistribution terms not independently verified |
| `docs/rag/tools/2022_hsTroponin_0-1h_MetaReview.md` | [Systematic review/meta-analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC9168511/) | author not recorded locally | 2022 inferred from filename | condensed Markdown summary/transformation | source is labeled open access locally; redistribution terms not independently verified |
| `docs/rag/tools/2023_ECG_Initial-Serial_Guidance.md` | [Open-access ED evaluation article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10324464/) | author not recorded locally | 2023 inferred from filename | locally compiled guidance summary/transformation | source is labeled open access locally; redistribution terms not independently verified |

## Local demo text

| Local file | Recorded source | Year/version | Form in repository | Rights/provenance status |
| --- | --- | --- | --- | --- |
| `docs/diabetes_management.txt` | none | none | short local demo guideline text | treated as a synthetic/local demo fixture; authorship and source rights are not recorded |
| `docs/medical_guidelines.txt` | none | none | short local chest-pain demo text | treated as a synthetic/local demo fixture; authorship and source rights are not recorded |

These two files contain medical-sounding instructions despite lacking source
metadata. Their inclusion in the retriever does not validate their content.

## Derived retrieval artifacts

- `rag_index/meta.json` stores the 49 chunk texts and source offsets.
- `rag_index/index.faiss` stores 384-dimensional
  `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- `rag_index/build_summary.json` records 15 indexed files, while the committed
  `meta.json` contains chunks from the 14 files listed above. The repository
  does not preserve enough build provenance to explain that discrepancy.
- `data/rag/eval_queries.json` contains 20 synthetic evaluation queries with
  exact graded chunk-ID relevance judgments.
- `data/rag/eval_manifest.json` pins source, metadata, index, synonyms, and
  evaluation fixtures by SHA-256.

The committed index is a reproducibility fixture. Rebuilding it scans supported
files under `docs/`, so documentation changes can alter the corpus unless the
build input is narrowed and the manifest is intentionally regenerated.
