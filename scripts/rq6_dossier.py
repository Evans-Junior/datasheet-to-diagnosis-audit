"""Build the RQ6 evidence dossier and the AI-draft column of the coding sheet.

WHY THIS EXISTS, AND WHAT IT DELIBERATELY DOES NOT DO (D098)
------------------------------------------------------------
`docs/codebook.md` §6 fixes RQ6 as independent double coding by two named human
coders, with Cohen's kappa computed on the PRE-ADJUDICATION codes. That design is
the only thing standing between "we read ten documents" and "we measured ten
documents", and it has one failure mode that matters here: if a machine fills one
coder's column, the kappa stops being a reliability statistic. It becomes a
measure of how well a human agrees with a machine, reported under a name that
claims something else.

So this script writes THREE things and never a fourth:

  1. `docs/rq6_dossier.md`  -- per document and dimension, the passages that bear
     on the code, verbatim, with locators, plus the boundary question a coder has
     to answer. This is preparation, not judgement: it means a coder decides
     against quotations instead of re-reading 1.1 MB of source.
  2. the `ai_draft_*` columns of `docs/rq6_coding_sheet.csv` -- a machine-proposed
     code with its rationale, in columns of its own. Same pattern as D038: AI
     drafting behind a human gate, labelled where it cannot be mistaken for
     human work.
  3. `results/tables/rq6_codes.csv` once humans have coded, via
     `scripts/rq6_reliability.py`.

  NOT WRITTEN, EVER: `evans_code`, `aymen_code`, `agreed_code`. If a future
  version of this file touches those columns, the kappa in the paper is void.

The draft is also genuinely useful as a third rater: agreement between the AI
draft and the two humans can be reported as a secondary diagnostic, which is a
result about machine coding rather than a substitute for human coding.
"""

from __future__ import annotations

import pathlib
import re
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RAW = ROOT / "data/raw/rq6"
SHEET = ROOT / "docs/rq6_coding_sheet.csv"
DOSSIER = ROOT / "docs/rq6_dossier.md"
COUNTS = ROOT / "results/tables/rq6_search_counts.csv"

# Columns this script is allowed to write. Enforced below.
AI_COLS = ["ai_draft_code", "ai_draft_rationale", "ai_draft_boundary"]
HUMAN_COLS = ["evans_code", "evans_passage_ids", "evans_quote",
              "aymen_code", "aymen_passage_ids", "aymen_quote", "agreed_code"]

# The four calls that decide a large share of the 80 cells, listed in the
# dossier's calibration section and tagged where they occur. Keep in sync with
# build_dossier's numbered list.
ADJUDICATE = {
    ("01_pile_paper", "D1"),          # association vs composition
    ("03_pythia_model_card", "D2"),   # D2 adjacency rule
    ("07b_olmo2_model_card", "D2"),   # the same rule, other side
    ("05_dolma_paper", "D1"),         # D1 level 1 requires gender to be named
    ("01_pile_paper", "D5"),          # scope note vs reference
    ("04_pythia_paper", "D5"),        # the same rule, other document
}

DIM_TITLES = {
    "D1": "Gender composition of the corpus",
    "D2": "Gender-related downstream risk",
    "D3": "Health or medical content acknowledgement",
    "D4": "Health x demographic intersection",
    "D5": "Gender identity beyond the binary",
    "D6": "Stated scope of appropriate use",
    "D7": "Measurement or assertion (qualifier)",
    "D8": "Traceability (qualifier)",
}

# ---------------------------------------------------------------------------
# The evidence. Every `q` is verbatim from the file named in `loc`, read at
# source on 2026-11-10. OCR artefacts in the PDF-derived text (broken ligatures,
# stray hyphens, spaced letters) are preserved rather than tidied, because a
# tidied quotation is no longer a quotation and §5 of the codebook turns on that.
# `draft` is a machine proposal. `boundary` states the call a human has to make,
# and is empty only where the evidence admits one reading.
# ---------------------------------------------------------------------------

E: dict[tuple[str, str], dict] = {}


def ev(doc, dim, draft, rationale, boundary="", quotes=()):
    E[(doc, dim)] = {"draft": draft, "rationale": rationale,
                     "boundary": boundary, "quotes": list(quotes)}


# ========================= 01 Pile paper ==================================
ev("01_pile_paper", "D1", "3",
   "Section 6.4.1 reports a measured gender statistic over this corpus with the "
   "method stated: co-occurrence differences for binary pronouns, weighted by "
   "root frequency, plus per-component sentiment in Figure 13. Method detail is "
   "sufficient to know what was counted.",
   "THE CENTRAL ADJUDICATION OF THE WHOLE CODING. D1 is headed 'gender "
   "composition' and asks about the gender DISTRIBUTION of the text. What 6.4.1 "
   "measures is gender ASSOCIATION (which adjectives co-occur with he/she) and "
   "sentiment, not what share of the corpus concerns women or men. A strict "
   "composition reading gives 2 (implies a skew, reports no composition "
   "number); a 'measured gender statistic with a method' reading gives 3. "
   "Decide this before coding anything else, because it sets the headline: "
   "under 3, RQ6's finding is not that nobody measured gender, it is that the "
   "measurement and the medical content were never joined (see D4).",
   [("The Pile paper, section 6.4.1 Gender",
     "We computed gender associations by computing co-occurrences for binary "
     "pronouns. For each word, we computed the difference in the rate it "
     "co-occurs with \"he\" and \"she\" and weighed it by the square root of its "
     "frequency. We report the top 15 most biased adjectives or adverbs (Loper "
     "and Bird, 2002) for each in Table 10."),
    ("section 6.4.1",
     "We see that words like “mil- itary”, “criminal”, and "
     "“offensive” strongly bias towards men, while “little”, "
     "“married”, “sexual”, and “happy” bias towards "
     "women."),
    ("section 6.4.1",
     "In addition, we computed the average senti- ment (Baccianella et al., "
     "2010) of words co- occurring with the gendered pronouns across each "
     "dataset in Figure 13. Generally, we ﬁnd no sig- niﬁcant sentiment "
     "bias towards men or women. This, of course, does not mean that the dataset "
     "is free of gender bias (as our co-occurrence tests show)."),
    ("section 6.4, opening",
     "As language models may pick up unexpected biases from the training data, "
     "we performed a preliminary analysis of the different components that make "
     "up the Pile. Because models with different charac- teristics may be "
     "trained on the Pile, we aimed to document the biases of the data and not a "
     "speciﬁc model.")])

ev("01_pile_paper", "D2", "2",
   "Section 6.4 states the consequence explicitly: biases in the training data "
   "may be picked up by models, and the documentation exists so users can choose "
   "components accordingly. Gender is one of the three attributes analysed. No "
   "high-stakes domain is named anywhere in the paper, so level 3 is unavailable.",
   "",
   [("section 6.4",
     "Our goal is to provide users of this dataset with preliminary guidance on "
     "how the different components are biased so that they can make deci- sions "
     "on which components to train on.")])

ev("01_pile_paper", "D3", "2",
   "Health content is discussed as a content category and the paper states what "
   "it is expected to be good for, which is the level-2 clause. Level 3 would "
   "need the limitations or risks of health text as training data, and the paper "
   "discusses PMC's risks nowhere.",
   "",
   [("section 2.2 PubMed Central",
     "We included PMC in the hopes that it will beneﬁt potential downstream "
     "ap- plications to the medical domain."),
    ("section 2.11 PubMed Abstracts",
     "PubMed Abstracts consists of the abstracts from 30 million publications in "
     "PubMed, the online repos- itory for biomedical articles run by the "
     "National Library of Medicine.")])

ev("01_pile_paper", "D4", "0",
   "Nine windows in this document contain a demographic term and a health term "
   "within 400 characters. All nine are artefacts: the author-contribution list, "
   "the axis labels of Figure 13 (whose dataset list places 'PubMed Central' "
   "near the 'male female' legend), and the per-component topic tables in "
   "Appendix F, where the PubMed Abstracts topic row reads as word salad. None "
   "is a claim relating gender composition to health content. Under the codebook "
   "rule that co-occurrence is not a join, this is 0.",
   "The one arguable case is the topic table: the PubMed Abstracts topic row is "
   "literally 'women patients positive hiv cancer health data care', so both "
   "topics do appear in one cell, which fits level 1's 'a list in which both "
   "appear without an asserted relation'. Against that, the codebook's own "
   "coding rule says a bias caveat in one section and a PubMed row in a table in "
   "another is level 0, which signals that the authors of the codebook meant "
   "table co-occurrence to score 0. Draft is 0; a coder arguing 1 is not wrong.",
   [("Appendix F, topic table, PubMed Abstracts row",
     "PubMed Abstracts women patients positive hiv cancer health data care based"),
    ("Figure 13 axis labels",
     "male female StackExchange OpenWebText2 Pile-CC FreeLaw Books3 Wikipedia "
     "(en) HackerNews OpenSubtitles PubMed Central PubMed Abstracts Enron Emails")])

ev("01_pile_paper", "D5", "0",
   "No reference to gender identity beyond the binary. The term search returns "
   "zero for non-binary, nonbinary, transgender and 'trans ', and the gender "
   "analysis states its own binary scope.",
   "Section 6.4.1 says the analysis uses 'binary pronouns', which is a scope "
   "statement about the method rather than a reference to non-binary identity. "
   "Draft reads that as 0. A coder could argue level 1 on the grounds that "
   "naming the binary acknowledges what lies outside it; the stricter reading is "
   "that a methodological scope note is not a reference to an identity.",
   [("section 6.4.1",
     "We computed gender associations by computing co- occurrences for binary "
     "pronouns.")])

ev("01_pile_paper", "D6", "1",
   "Generic research framing only. The paper's use-related statements are about "
   "empowering researchers and about copyright, and the single 'not intended' "
   "in the document is a disclaimer that the copyright discussion is not legal "
   "advice. No out-of-scope task is named, and medical use is not mentioned.",
   "",
   [("section 6, Investigating and Documenting the Datasets",
     "What is and is not appropriate data to train on can therefore vary wildly "
     "with the application context. In our view, the best approach is to "
     "document rather than eliminate potentially con- cerning aspects of "
     "datasets, particularly since the purpose of the Pile is to train "
     "general-purpose lan- guage models. The primary goal of our documen- "
     "tation, therefore, is to empower NLP researchers to make informed "
     "decisions.")])

ev("01_pile_paper", "D7", "M",
   "A measurement is reported with a method: co-occurrence rates for binary "
   "pronouns weighted by root frequency, and SentiWordNet sentiment averaged per "
   "component. Both are the paper's own computation, not an attributed one.",
   "")

ev("01_pile_paper", "D8", "T",
   "The method is stated, the tool is cited (Loper and Bird for POS tagging, "
   "Baccianella et al. for sentiment), the corpus is public, and the quantity is "
   "defined well enough to recompute. A reader could reproduce the claim.",
   "Reproducible in principle rather than from an artefact: no code or word list "
   "for section 6.4 is pointed to from the paper. A coder holding out for "
   "released code would say P.")


# ========================= 02 Pile datasheet ==============================
ev("02_pile_datasheet", "D1", "2",
   "The Wikipedia component answer states that gender bias in that component has "
   "been widely studied and cites four studies of it. That is a claim about a "
   "component of THIS corpus, carried by citation rather than by a number, which "
   "is level 2 with D7 = R. Everywhere else gender appears only as one item in "
   "the repeated subpopulation list, which is level 1 on its own.",
   "",
   [("Datasheet for the Pile, subpopulation question, Wikipedia (en)",
     "Wikipedia (en): Wikipedia (en) identiﬁes many subpopulations, and the "
     "way that this m anifests and its relation to sociopolitical dynamics has "
     "been widely studied, including alo ng the lines of race [Adams et al., "
     "2019, Xing and Vetter, 2020], gender [Reagle and Rhue, 2011, Wagn er et "
     "al., 2015, Hargittai and Shaw, 2015, Graells-Garrido et al., 2015], "
     "ability [Phillips, 2016, Derby, 2012 ], nation of origin [Rask, 2008, Lee "
     "and Chun, 2017], religion [Callahan and Herring, 2011, Ball, 2021], a nd "
     "sexual orientation [Eisner, 2013].")])

ev("02_pile_datasheet", "D2", "1",
   "No statement anywhere that gender composition has a consequence for model "
   "behaviour. The document is a composition and provenance datasheet; its risk "
   "language is generic and not gender-specific.",
   "")

ev("02_pile_datasheet", "D3", "2",
   "Health content is discussed as a content category well beyond a composition "
   "table: each PubMed component gets its provenance, its creator and its "
   "statutory purpose.",
   "Level 2's distinguishing clause is 'including what it is expected to be good "
   "for', and the datasheet gives provenance rather than expected use. Level 1 "
   "says 'listed in a composition table only, with no commentary', which also "
   "does not fit, since there is substantial commentary. Neither level fits "
   "cleanly. Draft takes 2 on the strength of the commentary; a coder reading "
   "the 'good for' clause as binding would say 1. Worth an adjudication rule.",
   [("Datasheet for the Pile, composition",
     "PubMed Central: The PubMed Central dataset is a subset of the PubMed "
     "online repos itory for biomedical articles run by the United States of "
     "America’s National Ce nter for Biotechnology Information (NCBI)."),
    ("Datasheet for the Pile, creation motivation",
     "PubMed Central: The PubMed Central dataset was created to be included in "
     "the Pile. T he underlying data comes from the PubMed Central database, "
     "which was create d to allow public access to the results of research "
     "funded by the U.S. National Institute of Health")])

ev("02_pile_datasheet", "D4", "1",
   "THE ONLY GENUINE JOIN IN THE ENTIRE DOCUMENT SET. Three component answers "
   "put medical content and gender in one continuous passage, and assert "
   "something about them together: that papers studying gender are confirmed "
   "present in the medical subsets. Both topics are joined, but no relation "
   "between demographic skew and clinical use is asserted, so level 1 and not 2.",
   "Read the direction of the claim before coding, because it cuts against the "
   "obvious reading. The datasheet does not say the medical content may be "
   "demographically skewed. It says the medical content includes papers that "
   "study gender, which if anything implies adequacy. A coder who treats 'papers "
   "that study gender are present' as an asserted relation would reach 2; the "
   "draft holds that presence is not a relation.",
   [("Datasheet for the Pile, subpopulation question, PubMed Central",
     "PubMed Central: Many medical papers identify subpopulations in the course "
     "of their s tudies. We have conﬁrmed the presence of papers that study "
     "race, gender, abilit y, nation of origin, religion, and sexual "
     "orientation."),
    ("same question, PubMed Abstracts",
     "PubMed Abstracts: Many medical papers identify subpopulations in the "
     "course of their s tudies. We have conﬁrmed the presence of papers "
     "that study race, gender , ability, nation of origin, religion, and sexual "
     "orientation."),
    ("same question, NIH ExPORTER",
     "NIH ExPORTER: Many medical papers identify subpopulations in the course of "
     "their s tudies. We have conﬁrmed the presence of papers that study "
     "race, gender , ability, nation of origin, religion, and sexual "
     "orientation.")])

ev("02_pile_datasheet", "D5", "0",
   "Zero references. The term search records one hit for 'trans ', and that hit "
   "is the title 'Big bird: Transformers for longer sequences' in the "
   "bibliography. Recording this matters because the search-count table is "
   "published as evidence, so its one apparent hit needs its explanation beside "
   "it.",
   "",
   [("bibliography, false positive for the term 'trans '",
     "Big bird: Trans formers for longer sequences. Advances in Neural "
     "Information Processing Systems , 33, 2020.")])

ev("02_pile_datasheet", "D6", "1",
   "The document's scope statements are about itself, not about appropriate use "
   "of the data: it says it is not a substitute for the component datasheets. No "
   "task is named as out of scope, and medical use is not mentioned.",
   "",
   [("Datasheet for the Pile, preamble",
     "This document is not intended to be – and should not be used as "
     "– a substitute for a datasheet for the original versions of the "
     "component datase ts.")])

ev("02_pile_datasheet", "D7", "R",
   "The one substantive gender claim is a measurement attributed elsewhere: four "
   "studies of gender bias in Wikipedia, cited, with no measurement performed in "
   "this document.",
   "")

ev("02_pile_datasheet", "D8", "N",
   "THE FINDING THAT PAIRS WITH RQ1, AND THE REASON TO CODE THIS DOCUMENT AT "
   "ALL. The Gebru datasheet question asks, in terms, for the DISTRIBUTION of "
   "subpopulations. It is asked twice and answered neither time. At the "
   "instance-level question the distribution clause is simply passed over for a "
   "description of text cleaning; at the dedicated question the answer gives the "
   "PRESENCE of papers that study gender. Presence is not distribution, so no "
   "reader could reproduce a composition claim from this document.",
   "",
   [("Gebru instance question, asked",
     "What data does each instance consist of ? “Raw” data (e.g., un "
     "processed text or images)? F eatures/attributes? Is there a label/target "
     "associated w ith instances? If the instances re- lated to people, are "
     "subpopulations identiﬁed (e.g., by age , gender, etc.) and what is "
     "their distribution?"),
    ("the answer given",
     "The Pile: Instances are text ﬁles, processed for readability and to "
     "remove autogenerated text, garbage generated during parsing, and code "
     "fragments picked up from web sites."),
    ("Gebru subpopulation question, asked",
     "Does the dataset identify any subpopulations (e.g., by age, gender)? If "
     "so, please describe how these subpopulations are identiﬁed and "
     "provide a descripti on of their respective distributions within the "
     "dataset.")])


# ========================= 03 Pythia model card ===========================
ev("03_pythia_model_card", "D1", "1",
   "Gender is named in a list of documented biases, with the claim itself "
   "delegated to section 6 of the Pile paper. No claim about distribution is "
   "made in the card, which is level 1 with D7 = R.",
   "",
   [("Pythia model card, Limitations and biases",
     "This model was trained on [the Pile](https://pile.eleuther.ai/), a dataset "
     "known to contain profanity and texts that are lewd or otherwise offensive. "
     "See [Section 6 of the Pile paper](https://arxiv.org/abs/2101.00027) for a "
     "discussion of documented biases with regards to gender, religion, and "
     "race.")])

ev("03_pythia_model_card", "D2", "2",
   "The card runs a consequence chain in one continuous passage: trained on the "
   "Pile, the Pile has documented gender biases, this model may produce socially "
   "unacceptable text. That names a gender-related downstream risk with the "
   "domain unspecified.",
   "The sentence naming gender and the sentence naming the harm are adjacent but "
   "distinct, and the harm sentence does not itself say gender. A coder reading "
   "them separately gets level 1 (generic harm, gender not specified); a coder "
   "reading the passage as continuous gets 2. Draft takes 2 because the passage "
   "is causally ordered. This is the second adjudication to settle up front, "
   "since the same question recurs for 07b.",
   [("Pythia model card, Limitations and biases",
     "Pythia-70M may produce socially unacceptable or undesirable text, *even "
     "if* the prompt itself does not include anything explicitly offensive.")])

ev("03_pythia_model_card", "D3", "0",
   "No reference to medical or health content. The term search returns zero for "
   "medical, clinical, health, patient, diagnosis and PubMed across the whole "
   "card, so the Pile's advertised medical components are not mentioned in the "
   "document a practitioner actually reads.",
   "")

ev("03_pythia_model_card", "D4", "0",
   "Absent, and absent by construction: with zero health terms in the document "
   "there is no passage in which the two topics could be joined.",
   "")

ev("03_pythia_model_card", "D5", "0",
   "No reference. Zero hits for non-binary, nonbinary, transgender, 'trans ' and "
   "identity.",
   "")

ev("03_pythia_model_card", "D6", "2",
   "Named out-of-scope uses, and medical use is not among them. This is the "
   "strongest use-scope statement in the whole document set, and the codebook "
   "requires it to be reported as a point in the documentation's favour. Level 3 "
   "would need medical, clinical or health-advice use named, and it is not.",
   "Note the tension the codebook flagged for D6. 'Cannot be used for "
   "human-facing interactions' arguably covers clinical advice implicitly, and a "
   "coder might stretch to 3 on that basis. The draft holds at 2 because D6 "
   "level 3 asks for the domain to be NAMED, and an implicit cover is what the "
   "codebook warns against letting stand in for a disclosure.",
   [("Pythia model card, Out-of-scope use",
     "The Pythia Suite is **not** intended for deployment. It is not a in itself "
     "a product and cannot be used for human-facing interactions. For example, "
     "the model may generate harmful or offensive text. Please evaluate the "
     "risks associated with your particular use case."),
    ("same section",
     "Pythia models are English-language only, and are not suitable for "
     "translation or generating text in other languages.")])

ev("03_pythia_model_card", "D7", "R",
   "The gender claim is attributed: the card points at section 6 of the Pile "
   "paper and performs no measurement itself.",
   "")

ev("03_pythia_model_card", "D8", "P",
   "The pointer is specific enough to follow, naming the document and the "
   "section, but the card supplies no method, no parameters and no data, so the "
   "claim is not reproducible from this document.",
   "P versus N is a real call. The draft takes P because a named section of a "
   "named paper is more than nothing; a coder holding that 'from what the "
   "document provides' means this document alone would say N.")


# ========================= 04 Pythia paper ================================
ev("04_pythia_paper", "D1", "2",
   "The paper implies a masculine skew in the corpus without reporting a number: "
   "the intervention replaces masculine pronouns with feminine ones and is "
   "described as modifying the frequency of gendered terms, which only makes "
   "sense against a masculine-majority baseline. No baseline frequency is "
   "reported anywhere, so level 3 is unavailable.",
   "",
   [("Pythia paper, section 3.1 case study",
     "we take a checkpoint and optimizer state 21B tokens (7%) prior to the end "
     "of training, and resume training of the model such that it sees the exact "
     "same data until the end of training, but with morphologically masculine "
     "pronouns replaced by their feminine counterparts."),
    ("Pythia paper, related work",
     "To demonstrate what is now possible with Pythia, we analyze whether "
     "deliberately modifying the frequency of gendered terms in the pretrain- "
     "ing data of a language model can have an impact on its downstream "
     "behavior and biases."),
    ("Pythia paper, section 3.1",
     "yet little is known about the role of specific corpus statistics in the "
     "emergence of bias during pretraining.")])

ev("04_pythia_paper", "D2", "2",
   "Gender-specific downstream harm is named and measured, with a scale finding "
   "attached. Domain is unspecified: the paper has zero hits for medical, "
   "clinical, health, patient and diagnosis, so level 3 is unavailable.",
   "",
   [("Pythia paper, section 3.1 results",
     "we can clearly see a reduction in the bias as a result of swapping the "
     "gendered pronouns in the last 7% or 21% of the training for all model "
     "sizes, but most prominently for the larger ones, although these are also "
     "more biased to begin with."),
    ("same section",
     "We hypothesize that because larger models are bet- ter at modeling "
     "correlations and distributions within their corpora, their increased "
     "capacity causes features of bias to be more strongly or robustly learned.")])

ev("04_pythia_paper", "D3", "0",
   "No reference to medical or health content anywhere in the paper. Zero hits "
   "for medical, clinical, health, patient, diagnosis and PubMed.",
   "")

ev("04_pythia_paper", "D4", "0",
   "Absent by construction: zero health terms, so zero joint windows.",
   "")

ev("04_pythia_paper", "D5", "0",
   "No reference. Zero hits for non-binary, nonbinary, transgender, 'trans ' and "
   "identity. The design is binary throughout, by stated construction.",
   "Appendix C.1 states 'we intervene on gendered pronouns' and the method is "
   "masculine-to-feminine replacement, which is the same scope-note question as "
   "01/D5 and should be decided the same way.",
   [("Pythia paper, Appendix C.1",
     "We evaluate our models only on the English subset for gender bias, since "
     "our models are monolingual and we intervene on gendered pronouns.")])

ev("04_pythia_paper", "D6", "1",
   "Generic research framing. Pythia is described as a suite for scientific "
   "research on language models; no out-of-scope task is named and medical use "
   "is not mentioned.",
   "",
   [("Pythia paper, Requirements for a Scientific Suite of LLMs",
     "Pythia is envisioned as a suite for enabling and empowering scientific "
     "research on the capacities and limitations of large language models.")])

ev("04_pythia_paper", "D7", "M",
   "Measurements are performed and reported with method: CrowS-Pairs and "
   "WinoBias under modifications documented in Appendix C.1, against a "
   "counterfactually retrained checkpoint.",
   "")

ev("04_pythia_paper", "D8", "T",
   "Checkpoints, the training data order and the public codebase are released, "
   "the benchmark modifications are described in Appendix C.1, and the "
   "intervention is specified by token count. This is the most traceable claim "
   "in the document set.",
   "")


# ========================= 05 Dolma paper =================================
ev("05_dolma_paper", "D1", "0",
   "THE SHARPEST ASYMMETRY IN THE SET, AND IT NEEDS STATING CAREFULLY. Dolma "
   "does disclose composition skew, and does so unusually well: not "
   "representative, STEM-skewed in peS2o, global-north-biased in Wikipedia, with "
   "an explicit admission that no correction was attempted. It never names "
   "gender. In 244 KB of text the word 'gender' occurs exactly once, inside the "
   "Gebru question template. D1 level 1 requires gender to be NAMED in the list "
   "of biases, so a document that discloses skew along discipline and geography "
   "while omitting gender scores 0 on this dimension.",
   "This is the dimension most likely to split the two coders, and for a good "
   "reason: coding it 0 feels wrong next to a document that is manifestly candid "
   "about skew. The defence is codebook section 1 on false presence, which was "
   "written to stop exactly this inference. If a coder wants level 1 for "
   "'communities' and 'social groups' as implicitly covering gender, that is a "
   "legitimate reading and must be adjudicated, but note where it leads: it "
   "makes every generic social-bias caveat in the set a gender disclosure.",
   [("Dolma paper, datasheet, unfair advantage question",
     "Dolma is not a representative sample of none of its sources. It might "
     "underrepresent or overrepresent some communities on the internet; further, "
     "papers in the peS2o subset are skewed towards STEM disciplines; books in "
     "the Gutenberg library are mostly from the public domain (at the time of "
     "publication, books published before 1927); finally, the English and Simple "
     "subset of Wikipedia and Wikibooks might be biased towards events and "
     "people from the global north."),
    ("same answer",
     "We did not attempt to alter distribution of social groups in Dolma. "
     "Large-scale interventions to correct societal biases in large datasets "
     "remain challenging, and are left to future work."),
    ("Dolma paper, datasheet, instance question: asked and deferred",
     "There are no labels associated with instances. Many text instances were "
     "likely created by people or groups of people, but in the vast majority of "
     "cases authorship infor- mation is unavailable let alone subpopulation "
     "metadata. we leave aggregation and reporting of these statistics to future "
     "work.")])

ev("05_dolma_paper", "D2", "1",
   "Generic harm language only, with gender never specified. The document "
   "discusses societal bias and risk at length but attaches no gender-specific "
   "consequence to model behaviour.",
   "")

ev("05_dolma_paper", "D3", "0",
   "No reference to medical or health content. The single 'medical' hit is in a "
   "Gebru question template about obligations to ethically protected subjects, "
   "and health, clinical, patient and PubMed return zero. peS2o is described as "
   "academic papers skewed to STEM, never as containing biomedical literature, "
   "although in fact it does.",
   "A coder who knows peS2o derives from S2ORC and therefore contains medical "
   "papers may be tempted to code 1. Resist it: the codebook codes the document, "
   "not the corpus, and no cross-document or outside knowledge is admissible "
   "under section 5. That the corpus contains medical text the document never "
   "mentions is itself the finding.",
   [("Dolma paper, datasheet, ethically protected subjects question",
     "If it relates to other ethically protected subjects, have appropriate "
     "obligations been met? (e.g., medical data might include information "
     "collected from animals) Due to the nature of and size of Dolma, it is "
     "impossible to determine which obligations, if any, are appropriate."),
    ("Dolma paper, peS2o description",
     "(S2ORC; Lo et al., 2020). As this dataset has been created for language "
     "modeling purposes, we use it as-is.")])

ev("05_dolma_paper", "D4", "0",
   "Zero joint windows in 244 KB. No passage contains a demographic term and a "
   "health term within 400 characters of each other.",
   "")

ev("05_dolma_paper", "D5", "0",
   "No reference. Zero hits for non-binary, nonbinary and transgender; the five "
   "'identity' hits are language identification and one Jigsaw toxicity label, "
   "'identity hate'.",
   "",
   [("Dolma paper, toxicity filtering, false positive for 'identity'",
     "and/or “identity hate ” alongside unlabeled com-")])

ev("05_dolma_paper", "D6", "2",
   "An out-of-scope use is named, and medical use is not among it. The answer "
   "names direct consumption of original content as the unsuitable task and "
   "otherwise refers users to the licence.",
   "",
   [("Dolma paper, datasheet, out-of-scope question",
     "Are there obvious tasks for which it should not be used? Due to the myriad "
     "transformations applied to the orig- inal source materials to derive our "
     "dataset, we believe it is ill-suited as a replacement for users seeking to "
     "di- rectly consume the original content.")])

ev("05_dolma_paper", "D7", "A",
   "The composition claims are asserted, not measured: 'might underrepresent or "
   "overrepresent', 'might be biased towards', with no statistic and with the "
   "measurement explicitly deferred to future work.",
   "D7 is defined as applying to D1 or D2 codes above 0. If D1 is coded 0 and D2 "
   "is coded 1, the qualifier attaches to D2's generic harm language, which is "
   "also an assertion. The code is A either way, but record which dimension it "
   "is qualifying.")

ev("05_dolma_paper", "D8", "N",
   "Not reproducible. The document states that subpopulation metadata is "
   "unavailable and that aggregation and reporting of these statistics is left "
   "to future work, which forecloses reproduction from the document.",
   "")


# ================== 06 olmo-mix-1124 dataset card =========================
ev("06_olmomix_dataset_card", "D1", "0",
   "THE HEADLINE PAIRING WITH RQ1. This is the dataset card for the corpus OLMo "
   "2 is actually trained on, and the document a practitioner reads before using "
   "it. It is 6 KB, and it consists of a YAML feature schema, a seven-row table "
   "of token and byte counts, a licence paragraph, a pointer to the tech report "
   "and the sentence 'A technical manuscript is forthcoming!'. All thirty search "
   "terms return zero. There is no prose in which a disclosure could occur.",
   "",
   [("olmo-mix-1124 dataset card, in full, after the YAML block and size table",
     "Please refer to the OLMo2 Tech Report for further details. ## Licensing "
     "Information This **collection** is released under the **Open Data Commons "
     "Attribution License (ODC-By) v1.0** license. The use of this dataset is "
     "also subject to CommonCrawl's Terms of Use. ## Citation A technical "
     "manuscript is forthcoming!")])

ev("06_olmomix_dataset_card", "D2", "0", "No risk statement of any kind.", "")
ev("06_olmomix_dataset_card", "D3", "0",
   "No health source is named. The component table lists DCLM-Baseline, Arxiv, "
   "pes2o, starcoder, Algebraic-stack, OpenWebMath and Wiki, none of them "
   "identified as medical content.",
   "pes2o again contains biomedical literature in fact. Same rule as 05/D3: the "
   "document is the unit, and it says nothing.")
ev("06_olmomix_dataset_card", "D4", "0", "Absent, with no prose to join.", "")
ev("06_olmomix_dataset_card", "D5", "0", "No reference.", "")
ev("06_olmomix_dataset_card", "D6", "1",
   "Generic licence and terms-of-use language is the only use-related content. "
   "No task is named as out of scope.",
   "Arguably 0: a licence is a legal restriction rather than a scope statement "
   "about appropriate use, and the YAML 'task_categories: text-generation' is a "
   "declaration rather than a restriction. Draft takes 1 on the as-is reading.")
ev("06_olmomix_dataset_card", "D7", "not_applicable",
   "Not applicable: D7 applies only to a D1 or D2 code above 0, and both are 0.",
   "")
ev("06_olmomix_dataset_card", "D8", "not_applicable",
   "Not applicable: no claim is made, so there is nothing to trace.",
   "")


# ===================== 07a OLMo 2 technical report ========================
ev("07a_olmo2_report", "D1", "0",
   "No reference to gender composition. Zero hits for gender, sex, demographic, "
   "identity, stereotype, fairness, disparity and equity across a 185 KB "
   "technical report.",
   "")

ev("07a_olmo2_report", "D2", "0",
   "THE FALSE-PRESENCE TRAP IN THE SEARCH TABLE, AND IT MUST BE RECORDED. The "
   "search counts show bias = 4 and harm = 6 for this document, which a reader "
   "of rq6_search_counts.csv alone would take for partial disclosure. All four "
   "'bias' hits are the architectural bias term, and all six 'harm' hits are "
   "author surnames in the bibliography. There is no social-bias or harm "
   "discussion in the document at all.",
   "",
   [("OLMo 2 report, architecture, false positive for 'bias'",
     "• No biases:We exclude all bias terms from our architecture "
     "(Groeneveld et al., 2024; Chowdhery et al.,"),
    ("OLMo 2 report, architecture table, false positive for 'bias'",
     "Biases None None None"),
    ("OLMo 2 report, bibliography, false positive for 'harm'",
     "M. Lučić, X. Zhai, D. Keysers, J. Harmsen, and N. Houlsby. "
     "Scaling vision transformers to 22 billion parameters,")])

ev("07a_olmo2_report", "D3", "0",
   "No reference to medical or health content. The three 'health' hits are a "
   "healthy region of embedding norms and two mentions of GPU health checks in "
   "the cluster tooling. Medical, clinical, patient, diagnosis and PubMed return "
   "zero.",
   "",
   [("OLMo 2 report, training stability, false positive for 'health'",
     "and observe that embedding norms settle in a healthy region as training "
     "progresses."),
    ("OLMo 2 report, infrastructure, false positive for 'health'",
     "GPU health checksBeaker executes a simple program prior to running "
     "workloads on the assigned GPUs.")])

ev("07a_olmo2_report", "D4", "0", "Zero joint windows.", "")
ev("07a_olmo2_report", "D5", "0", "No reference.", "")
ev("07a_olmo2_report", "D6", "0",
   "No use-scope statement. The two 'should not' hits are about how often to log "
   "training metrics and about the required format of a model response in a "
   "prompt template.",
   "",
   [("OLMo 2 report, training telemetry, false positive for 'should not'",
     "a host-device sync, it should not be done on every training step. More "
     "commonly, metrics are logged")])
ev("07a_olmo2_report", "D7", "not_applicable", "Not applicable: D1 and D2 are both 0.", "")
ev("07a_olmo2_report", "D8", "not_applicable", "Not applicable: no claim is made.", "")


# ===================== 07b OLMo 2 7B model card ===========================
ev("07b_olmo2_model_card", "D1", "0",
   "No reference to gender. The card's only bias language is generic and names "
   "no attribute.",
   "")

ev("07b_olmo2_model_card", "D2", "1",
   "Generic harm language with gender not specified. The card has a 'Bias, "
   "Risks, and Limitations' heading and one paragraph under it, which names "
   "harmful and sensitive content and bias in the abstract.",
   "This is the same adjacency question as 03/D2 but it resolves the other way, "
   "and the contrast is worth preserving: the Pythia card names gender in its "
   "limitations passage and this card does not name any attribute at all. If a "
   "coder reaches 2 here, the Pythia-versus-OLMo contrast disappears, so settle "
   "the rule once and apply it to both.",
   [("OLMo 2 7B model card, Bias, Risks, and Limitations",
     "Like any base language model or fine-tuned model without safety "
     "filtering, these models can easily be prompted by users to generate "
     "harmful and sensitive content. Such content may also be produced "
     "unintentionally, especially in cases involving bias, so we recommend that "
     "users consider the risks when applying this technology. Additionally, many "
     "statements from OLMo or any LLM are often inaccurate, so facts should be "
     "verified.")])

ev("07b_olmo2_model_card", "D3", "0",
   "No reference to medical or health content. Zero hits across all health terms.",
   "")
ev("07b_olmo2_model_card", "D4", "0", "Absent; zero joint windows.", "")
ev("07b_olmo2_model_card", "D5", "0", "No reference.", "")
ev("07b_olmo2_model_card", "D6", "1",
   "Generic 'consider the risks' language. The card has no intended-use or "
   "out-of-scope section: its headings run Model Details, Installation, "
   "Inference, Fine-tuning, Evaluation, Pretraining, Model Merging, then Bias, "
   "Risks, and Limitations, then Citation. No task is named as out of scope.",
   "")
ev("07b_olmo2_model_card", "D7", "A",
   "Assertion. The risk paragraph reports no measurement and cites no source for "
   "its bias claim.",
   "")
ev("07b_olmo2_model_card", "D8", "N",
   "Not reproducible: a generic risk assertion with no method, data or citation.",
   "")


# ===================== 08a Qwen3 technical report =========================
ev("08a_qwen3_report", "D1", "0",
   "THE CLOSED-DATA COMPARATOR, AND THE COMPARISON IS CLEAN. Zero hits for "
   "gender, sex, female, demographic, identity, stereotype, fairness, disparity "
   "and equity. The search table's one 'man' and four 'men' hits are all author "
   "names in the contributor list and bibliography: 'Man Yuan' and 'Rui Men'. "
   "There is no human-referent gender language in the document.",
   "",
   [("Qwen3 technical report, contributor list, false positive for 'man'",
     "Langshi Chen, Le Jiang, Lei Zhang, Linjuan Wu, Man Yuan, Mingkun Yang, "
     "Minmin Sun, Mouxiang Chen, Na Ni"),
    ("Qwen3 technical report, contributor list, false positive for 'men'",
     "Mingfeng Xue, Mingze Li, Pei Zhang, Peng Wang, Qin Zhu, Rui Men, Ruize "
     "Gao, Shixuan Liu")])

ev("08a_qwen3_report", "D2", "0",
   "No gender-related downstream risk. The single 'bias' hit is QKV-bias in the "
   "architecture description and both 'harm' hits are bibliography surnames.",
   "",
   [("Qwen3 technical report, architecture, false positive for 'bias'",
     "we remove QKV-bias used in Qwen2 (Yang et al., 2024a) and introduce "
     "QK-Norm (Dehghani et al., 2023)")])

ev("08a_qwen3_report", "D3", "0",
   "No reference to medical or health content. Zero hits for medical, clinical, "
   "health, patient, diagnosis and PubMed.",
   "")
ev("08a_qwen3_report", "D4", "0", "Zero joint windows.", "")
ev("08a_qwen3_report", "D5", "0", "No reference.", "")
ev("08a_qwen3_report", "D6", "0", "No use-scope statement.", "")
ev("08a_qwen3_report", "D7", "not_applicable", "Not applicable: D1 and D2 are both 0.", "")
ev("08a_qwen3_report", "D8", "not_applicable", "Not applicable: no claim is made.", "")


# ===================== 08b Qwen3-8B model card ============================
ev("08b_qwen3_model_card", "D1", "0",
   "Zero hits on all thirty search terms. The card is architecture, benchmarks "
   "and usage instructions.",
   "")
ev("08b_qwen3_model_card", "D2", "0", "No risk statement of any kind.", "")
ev("08b_qwen3_model_card", "D3", "0", "No reference to medical or health content.", "")
ev("08b_qwen3_model_card", "D4", "0", "Absent, with nothing to join.", "")
ev("08b_qwen3_model_card", "D5", "0", "No reference.", "")
ev("08b_qwen3_model_card", "D6", "0",
   "No use-scope statement: no intended-use section, no out-of-scope section, "
   "and no risk language.",
   "")
ev("08b_qwen3_model_card", "D7", "not_applicable", "Not applicable: D1 and D2 are both 0.", "")
ev("08b_qwen3_model_card", "D8", "not_applicable", "Not applicable: no claim is made.", "")


# ---------------------------------------------------------------------------

def search_table() -> dict[str, dict[str, int]]:
    """Per document, the term -> hit count map from the published search table."""
    if not COUNTS.exists():
        return {}
    d = pd.read_csv(COUNTS)
    return {doc: dict(zip(g.term, g.hits)) for doc, g in d.groupby("document")}


def build_dossier(sheet: pd.DataFrame) -> str:
    counts = search_table()
    docs = list(dict.fromkeys(sheet.document))
    out: list[str] = []
    w = out.append

    w("# RQ6 evidence dossier\n")
    w("Generated by `scripts/rq6_dossier.py`. Do not hand-edit: edit the "
      "evidence spec in that script and regenerate.\n")
    w("> **This file is preparation, not coding.** It gathers, per document and "
      "dimension, the passages that bear on the code, so that a coder decides "
      "against quotations instead of re-reading 1.1 MB of source. The `AI draft` "
      "lines are a machine proposal recorded in their own column of the coding "
      "sheet. They are **not** a coder. `docs/codebook.md` §6 requires two "
      "independent human coders and computes Cohen's κ on the pre-adjudication "
      "codes; if a draft is copied into `evans_code` or `aymen_code`, that κ "
      "measures agreement with a machine and the reliability claim in the paper "
      "is void.\n")
    w("**How to use it.** Settle the four boundary questions marked "
      "`ADJUDICATE FIRST` below, as the calibration step (§6.1), on document 2 "
      "and on the three listed cross-document rules. Then code all ten "
      "documents independently, without reading each other's columns. The AI "
      "draft is visible here, which is a known contamination risk: if you want "
      "a clean independent pass, code from `docs/rq6_passages.csv` and the raw "
      "documents first, and read this file only to check you have not missed a "
      "passage.\n")
    w("Quotations preserve the OCR artefacts of the PDF-derived text, including "
      "broken ligatures and spaced letters. A tidied quotation is no longer a "
      "quotation.\n")

    # The adjudication list, pulled from the boundary notes flagged as central.
    w("---\n\n## Settle these first (calibration, §6.1)\n")
    w("Four calls decide a large share of the 80 cells. Each one changes what "
      "RQ6 concludes, so they are listed here rather than left to be discovered "
      "mid-coding.\n")
    w("1. **D1 on the Pile paper: is gender *association* a disclosure of "
      "gender *composition*?** Section 6.4.1 measures which adjectives "
      "co-occur with he and she, with a stated method. It never reports what "
      "share of the corpus concerns women or men. Code 3 and RQ6's finding "
      "becomes 'they measured gender, they described medical content, and never "
      "joined the two'. Code 2 and it stays closer to 'the measurement was "
      "incomplete'. The draft takes **3**, because it is the harder claim to "
      "attack and the resulting paper is stronger.\n")
    w("2. **D2 adjacency: does a limitations paragraph that names gender in one "
      "sentence and harm in the next state a gender-related risk?** Affects "
      "`03_pythia_model_card` (draft 2) and `07b_olmo2_model_card` (draft 1). "
      "Decide once and apply to both, and note what is at stake: the contrast "
      "between the two cards exists only under the reading that distinguishes "
      "them.\n")
    w("3. **D1 level 1 requires gender to be *named*.** Affects "
      "`05_dolma_paper`, which discloses skew candidly along discipline and "
      "geography and never names gender (one occurrence in 244 KB, inside the "
      "Gebru question template). Draft codes **0**. If 'communities' and "
      "'social groups' are read as covering gender, every generic bias caveat "
      "in the set becomes a gender disclosure.\n")
    w("4. **Methodological scope notes versus references.** 'We computed gender "
      "associations for binary pronouns' names the binary. Is that a reference "
      "to identity beyond it? Affects D5 on `01_pile_paper` and "
      "`04_pythia_paper`. Draft codes **0** both times.\n")

    w("---\n\n## What the search table does not tell you\n")
    w("`results/tables/rq6_search_counts.csv` is published as evidence for every "
      "level-0 code, and read alone it overstates disclosure in three "
      "documents. The coding pass resolved each apparent hit at source:\n")
    w("| Document | Term | Hits | What they actually are |\n|---|---|---|---|")
    w("| `07a_olmo2_report` | `bias` | 4 | the architectural bias term "
      "(\"We exclude all bias terms from our architecture\") |")
    w("| `07a_olmo2_report` | `harm` | 6 | author surnames in the bibliography "
      "(Harmsen, Sharma, Shajnfeld) |")
    w("| `07a_olmo2_report` | `health` | 3 | embedding norms in \"a healthy "
      "region\", and GPU health checks |")
    w("| `08a_qwen3_report` | `bias` | 1 | QKV-bias in the architecture |")
    w("| `08a_qwen3_report` | `man`, `men` | 1, 4 | contributor names: "
      "\"Man Yuan\", \"Rui Men\" |")
    w("| `02_pile_datasheet` | `trans ` | 1 | the title \"Big bird: "
      "Transformers for longer sequences\" |")
    w("\nThe search script matches on word boundaries, which was verified: a "
      "substring match would have returned 108 for `man` in the Qwen3 report "
      "instead of 1. The table is sound; it is the *reading* of a raw hit count "
      "that is not.\n")

    for doc in docs:
        w(f"---\n\n## {doc}\n")
        c = counts.get(doc, {})
        if c:
            nz = {k: v for k, v in c.items() if v}
            w(f"Search protocol step 2, non-zero terms ({len(nz)} of {len(c)}): "
              + (", ".join(f"`{k}` {v}" for k, v in sorted(nz.items(),
                                                           key=lambda kv: -kv[1]))
                 if nz else "**none: all thirty terms return zero**") + "\n")
        for dim in [f"D{i}" for i in range(1, 9)]:
            e = E.get((doc, dim))
            if e is None:
                continue
            w(f"### {dim} · {DIM_TITLES[dim]}\n")
            w(f"**AI draft: `{e['draft']}`** (a proposal, not a code)\n")
            w(f"{e['rationale']}\n")
            if e["boundary"]:
                tag = ("**ADJUDICATE FIRST.** " if (doc, dim) in ADJUDICATE
                       else "**Boundary.** ")
                w(f"{tag}{e['boundary']}\n")
            for loc, q in e["quotes"]:
                w(f"> {q}\n>\n> — {loc}\n")
    return "\n".join(out) + "\n"


def main() -> int:
    if not SHEET.exists():
        print(f"missing {SHEET}")
        return 1
    # keep_default_na=False: a cell reading 'n/a', 'NA' or 'None' is a
    # coder's literal answer, not a missing value.
    sheet = pd.read_csv(SHEET, dtype=str, keep_default_na=False)

    before = {c: sheet[c].copy() for c in HUMAN_COLS if c in sheet.columns}

    missing = [(d, m) for d, m in zip(sheet.document, sheet.dimension)
               if (d, m) not in E]
    if missing:
        print(f"no evidence spec for {len(missing)} cell(s): {missing[:5]}")
        return 1

    for col in AI_COLS:
        if col not in sheet.columns:
            sheet[col] = ""
    for i, r in sheet.iterrows():
        e = E[(r.document, r.dimension)]
        sheet.at[i, "ai_draft_code"] = e["draft"]
        sheet.at[i, "ai_draft_rationale"] = " ".join(e["rationale"].split())
        sheet.at[i, "ai_draft_boundary"] = " ".join(e["boundary"].split())

    # The guard. A human column changed by this script is a bug, not a feature.
    for c, old in before.items():
        if not old.astype(str).equals(sheet[c].astype(str)):
            print(f"REFUSING TO WRITE: this script changed the human column "
                  f"'{c}'. The kappa in docs/codebook.md section 6 is computed "
                  f"on the human columns, so a machine write there voids it.")
            return 1

    SHEET.write_text(sheet.to_csv(index=False), encoding="utf-8")
    DOSSIER.write_text(build_dossier(sheet), encoding="utf-8")

    nz = sum(1 for v in sheet.ai_draft_code if str(v) not in ("0", "not_applicable"))
    print(f"wrote {SHEET.relative_to(ROOT)}  "
          f"({len(sheet)} rows, {len(AI_COLS)} draft columns added)")
    print(f"wrote {DOSSIER.relative_to(ROOT)}  "
          f"({len(DOSSIER.read_text(encoding='utf-8')):,} chars)")
    print(f"draft: {nz} of {len(sheet)} cells above 0 or applicable")
    print()
    print("human columns untouched: " + ", ".join(HUMAN_COLS))
    print("Next: calibration on document 2 per codebook section 6.1, then two "
          "independent passes, then scripts/rq6_reliability.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
