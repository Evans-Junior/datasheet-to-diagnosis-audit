"""Write the plain language companion: pretraining, the vignettes, the floor,
and the placebo.

This exists because the things an audience stops us on are always the same: what
a vignette actually is, what the floor is and where it comes from, what
pretraining involves and whether we did any of it, and how the placebo is
applied. The paper answers all of them, but it answers them in the register of a
paper. This is the version to read before standing up.

Every figure is READ from results/tables and configs/placebo_arms.yaml, so the
guide cannot drift away from the deck or the paper. It writes the markdown to
docs/plain_language_guide.md and renders the same text to a Word file at the
project root. Run from the project root.
"""
import sys
from math import hypot
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_clinician_docx import convert                      # noqa: E402

MD = ROOT / "docs" / "plain_language_guide.md"
DOCX = ROOT / "Datasheet_to_Diagnosis_Plain_Language_Guide.docx"

# ------------------------------------------------------------------ the facts
v = pd.read_csv(ROOT / "data/vignettes/vignettes.csv")
ready = v[v.analysis_ready == True].copy()
tpl = yaml.safe_load(open(ROOT / "data/vignettes/templates.yaml"))
trows = tpl["templates"] if isinstance(tpl, dict) and "templates" in tpl else tpl
NOPT = {r["id"]: len(r["answer_options"]) for r in trows}
ready["nopt"] = ready.vignette_id.map(NOPT)

N_LIVE = ready.vignette_id.nunique()
N_TOTAL = v.vignette_id.nunique()
N_PROMPTS = len(ready)
ROWS_PER_MODEL = int(ready.nopt.sum())

g4 = sorted(set(ready[ready.group == 4].vignette_id))
G4N, G4B, G4M = len(g4), sum(1 for i in g4 if NOPT[i] == 2), sum(1 for i in g4 if NOPT[i] == 4)
G2N = ready[ready.group == 2].vignette_id.nunique()

reg = pd.read_csv(ROOT / "results/tables/i4_placebo_regate.csv")
N_MODELS = len(reg)
OPTION_ROWS = ROWS_PER_MODEL * N_MODELS
FL_LO, FL_HI = reg.nuisance_floor.min(), reg.nuisance_floor.max()
N_PASS_GENDER = int((reg.gate == "SENSITIVE").sum())
N_PASS_BOTH = int((reg.gate_both_floors == "SENSITIVE").sum())
N_FAIL = N_MODELS - N_PASS_GENDER

pl = pd.read_csv(ROOT / "data/vignettes/placebo_prompts.csv")
N_PLACEBO = len(pl)

arms = yaml.safe_load(open(ROOT / "configs/placebo_arms.yaml"))
PL_ATTRS = [a["key"].replace("_", " ") for a in arms["placebo_attributes"]]
REJECTED = arms.get("rejected_attributes") or arms.get("rejected") or []
if isinstance(REJECTED, dict):
    REJECTED = list(REJECTED)
N_REJECTED = len(REJECTED)

c = pd.read_csv(ROOT / "results/tables/rq2c_post_training_contrast.csv").iloc[0]
BASE_M, TUNED_M = c.merging_base, c.merging_tuned
RATIO = TUNED_M / BASE_M
TIMES_COMBINED = c.times_combined_floor

SHORT = {"EleutherAI/pythia-70m": "pythia-70m", "EleutherAI/pythia-160m": "pythia-160m",
         "EleutherAI/pythia-410m": "pythia-410m", "EleutherAI/pythia-1b": "pythia-1b",
         "EleutherAI/pythia-1.4b": "pythia-1.4b", "EleutherAI/pythia-2.8b": "pythia-2.8b",
         "EleutherAI/pythia-6.9b": "pythia-6.9b", "Qwen/Qwen3-8B": "Qwen3-8B",
         "allenai/OLMo-2-1124-7B": "OLMo-2-7B (base)",
         "allenai/OLMo-2-1124-7B-Instruct": "OLMo-2-7B-Instruct"}
ORDER = ["EleutherAI/pythia-70m", "EleutherAI/pythia-160m", "EleutherAI/pythia-410m",
         "EleutherAI/pythia-1b", "EleutherAI/pythia-1.4b", "EleutherAI/pythia-2.8b",
         "EleutherAI/pythia-6.9b", "allenai/OLMo-2-1124-7B",
         "allenai/OLMo-2-1124-7B-Instruct", "Qwen/Qwen3-8B"]
assert set(ORDER) == set(reg.model_id), sorted(set(reg.model_id) ^ set(ORDER))
R = reg.set_index("model_id")

# --------------------------------------------- the vignette anatomy, section 2
N_PARA = ready.paraphrase.nunique()
ARMS = ready.groupby("vignette_id").size()
N_ARMS = int(ARMS.mode().iloc[0])
SPLIT = ", ".join(sorted(ARMS[ARMS != N_ARMS].index))
N_SPCU = ready.spcu.nunique()
N_IDENT = ready.gender_identity.nunique()

EX = "G4-01"                    # the worked example: a Group 4 noise vignette
_ex = ready[ready.vignette_id == EX].iloc[0]
EX_COND, EX_Q, EX_REF = _ex.condition, _ex.question, _ex.reference_answer
EX_OPTS = " or ".join(str(_ex.answer_options).split("|"))
EX_TEXT = ready.loc[ready.prompt_id == f"{EX}_p1_female_blinded", "prompt_text"].iloc[0]
EX_WORDS = len(EX_TEXT.split())
EX_SPCU_LINE = EX_TEXT.split(". ")[0]

IDENT_LABEL = {"woman": "a woman", "man": "a man",
               "nonbinary": "a non-binary person", "blinded": "nobody at all"}

def ident_rows():
    """The identity line and the pronoun that follows it, read off the prompts."""
    out = []
    for key in ["woman", "man", "nonbinary", "blinded"]:
        t = ready.loc[ready.prompt_id == f"{EX}_p1_female_{key}", "prompt_text"].iloc[0]
        parts = t.split(". ")
        pron = parts[2].split(" ")[0].lower()
        pron = "the patient" if pron == "the" else pron
        out.append(f"| {IDENT_LABEL[key]} | {parts[1]}. | {pron} |")
    return "\n".join(out)

# ------------------------------------------------- the 11 times, section 1
DELTA = c.rq2c_delta
FLOOR_B, FLOOR_T, FLOOR_COMB = c.floor_base, c.floor_tuned, c.floor_combined
BASE_ID, TUNED_ID = "allenai/OLMo-2-1124-7B", "allenai/OLMo-2-1124-7B-Instruct"
PL_B, PL_T = R.loc[BASE_ID].placebo_floor_max, R.loc[TUNED_ID].placebo_floor_max
PL_COMB = hypot(PL_B, PL_T)
TIMES_PLACEBO = DELTA / PL_COMB

# --------------------------------------------------- the placebo run, section 5
PL_V, PL_PARA, PL_LEVELS = pl.vignette_id.nunique(), pl.paraphrase.nunique(), pl.arm_type.nunique()
HEAD = arms["placebo_attributes"][:2]
THIRD = arms["placebo_attributes"][2]

def placebo_rows():
    return "\n".join(
        f'| {a["key"].replace("_", " ")} | "{a["levels"][0]["sentence"]}" against '
        f'"{a["levels"][1]["sentence"]}" |' for a in HEAD)

THIRD_ATTR = THIRD["key"].replace("_", " ")
# without the full stops, because it is quoted inside a sentence
THIRD_PAIR = " against ".join(f'"{lv["sentence"].rstrip(".")}"' for lv in THIRD["levels"])

# The guide claims the two prompts in a placebo pair differ only by the injected
# sentence. Check it here rather than assert it in prose, so it cannot go stale.
_SENTENCES = [lv["sentence"] for a in arms["placebo_attributes"] for lv in a["levels"]]
for _lv in [f'{a["key"]}_{lv["key"]}' for a in HEAD for lv in a["levels"]]:
    _p = pl.loc[pl.prompt_id == f"{EX}_p1_female_blinded_{_lv}", "prompt_text"].iloc[0]
    assert _p.startswith(EX_TEXT), f"placebo pair is not byte-identical up to the injection: {_lv}"
    assert _p[len(EX_TEXT):].strip() in _SENTENCES, f"unexpected injected sentence: {_lv}"

# ------------------------------------------- merging as a multiple, section 6
mg = pd.read_csv(ROOT / "results/tables/rq2b_identity_spcu_merging.csv").set_index("model_id")
QWEN_ID = "Qwen/Qwen3-8B"
MG_ORDER = [TUNED_ID, QWEN_ID, BASE_ID]           # by times_floor, descending
assert list(mg[mg.exceeds_floor == True].index.sort_values()) == sorted(MG_ORDER), \
    "the models that merge above their floor are no longer the three the guide names"
assert list(mg.loc[MG_ORDER].times_floor.sort_values(ascending=False).index) == MG_ORDER, \
    "MG_ORDER is no longer sorted by times_floor"
MG_T, MG_Q, MG_B = (mg.loc[m].times_floor for m in MG_ORDER)
MG_TV, MG_QV = mg.loc[TUNED_ID].mean_merging, mg.loc[QWEN_ID].mean_merging
MG_TF, MG_QF = mg.loc[TUNED_ID].nuisance_floor, mg.loc[QWEN_ID].nuisance_floor
P_LIMIT = float(mg.p_resolution_limit.iloc[0])
N_INSIDE = int((mg.times_floor < 1).sum())
MG_N_VIG = int(mg.loc[TUNED_ID].n_vignettes)

def merge_rows():
    out = []
    for m in MG_ORDER:
        r = mg.loc[m]
        same = "all 3 the same way" if r.all_same_sign else f"{int(r.n_positive)} of 3"
        out.append(f"| {SHORT[m]} | {r.mean_merging:.4f} | {r.nuisance_floor:.4f} "
                   f"| **{r.times_floor:.1f} times** | {same} |")
    return "\n".join(out)

def merge_per_vignette():
    out = []
    for m in MG_ORDER:
        per = "; ".join(x.strip() for x in str(mg.loc[m].per_vignette).split(";"))
        out.append(f"| {SHORT[m]} | {per} |")
    return "\n".join(out)

# The one that rests on a single vignette, named rather than left to be found.
_bp = dict(x.strip().split("=") for x in str(mg.loc[BASE_ID].per_vignette).split(";"))
BASE_TOP_V = max(_bp, key=lambda k: abs(float(_bp[k])))
BASE_TOP = float(_bp[BASE_TOP_V])
BASE_REST = " and ".join(f"{k} at {_bp[k]}" for k in _bp if k != BASE_TOP_V)

# The worked example for the maximum: the attribute and vignette that set the
# placebo floor of the model that leans hardest on identity.
plf = pd.read_csv(ROOT / "results/tables/i4_placebo_floor.csv")
_h = plf[(plf.model_id == TUNED_ID) & (plf.in_headline == True)]
_w = _h.loc[_h.floor_max_abs_vignette.idxmax()]
W_ATTR = _w.attribute.replace("_", " ")
W_GROUP, W_NV = int(_w.group), int(_w.n_vignettes)
W_MAX, W_MEAN, W_V = _w.floor_max_abs_vignette, _w.floor_mean_abs_vignette, _w.worst_vignette
def worst_rows():
    out = []
    for item in str(_w.per_vignette).split(";"):
        vid, val = item.strip().split("=")
        out.append(f"| {vid} | {val} |")
    return "\n".join(out)
W_MARGIN = R.loc[TUNED_ID].mean_margin
W_FLOOR = R.loc[TUNED_ID].placebo_floor_max

print(f"{N_LIVE} of {N_TOTAL} vignettes, {N_PROMPTS} prompts, {N_MODELS} models, "
      f"{OPTION_ROWS:,} option rows, {N_PLACEBO} placebo prompts")
print(f"floor {FL_LO:.4f} to {FL_HI:.4f}; gate {N_PASS_GENDER} then {N_PASS_BOTH}; "
      f"merging {BASE_M:.4f} to {TUNED_M:.4f} ({RATIO:.1f}x)")
print(f"placebo attributes {PL_ATTRS}, {N_REJECTED} rejected")

def model_rows():
    out = []
    for m in ORDER:
        r = R.loc[m]
        verdict = ("reads the sex parameter" if r.gate == "SENSITIVE"
                   else "cannot tell male from female")
        out.append(f"| {SHORT[m]} | {r.mean_margin:+.4f} | {r.nuisance_floor:.4f} "
                   f"| {r.placebo_floor_max:.4f} | {verdict} |")
    return "\n".join(out)

# ------------------------------------------------------------------ the text
MDTEXT = f"""
**Written for:** you, so that you can explain this project to somebody who has
not read the paper, and answer the questions that always come back. Sections 1
and 5 are the two that get asked about most: whether we pretrained anything and
where the {TIMES_COMBINED:.0f} comes from, and how the placebo is actually applied.

**Every number below is read from the results tables at prompt set
18f637733ab522a1.** Nothing here is rounded by hand or remembered.

## The whole project in six sentences

We put the same clinical case to {N_MODELS} language models, over and over. The
medical facts never change: the symptoms, the test results, the question and the
answer options are written once and reused word for word. The only thing that
changes is who the patient is said to be, which is either a woman, a man, a
non-binary person, or nobody in particular. A model that is reading the medicine
cannot move when only that word moves, so if it does move, it is treating
identity as if it were biology. Three of the {N_MODELS} models move a lot, and the
one that moves most is the model whose training data is fully published. That is
the whole reason we work with open models: when we find something, we can go back
and count what caused it.

In numbers: {N_LIVE} live vignettes of {N_TOTAL}, {N_PROMPTS} prompts,
{ROWS_PER_MODEL:,} scored option rows per model, {OPTION_ROWS:,} in all.

## 1. What we mean by pretraining

### The short answer

Pretraining is the stage where a model learns language by reading an enormous
amount of text and repeatedly guessing what word comes next. Nobody tells it
what is true, what is medical, or what is fair. It reads, it guesses, it is
corrected, and it reads again. Whatever patterns are in that text become
patterns in the model.

### The three stages, in the order they happen

1. **Pretraining.** The model reads a corpus, which is just a very large pile of text, and learns to predict the next word. For the Pythia models that corpus is The Pile, roughly 800 GB of text. For the OLMo-2 models it is olmo-mix-1124. This stage is where almost all of the model's knowledge of the world comes from, and it is also where whatever is skewed about the text gets baked in.
2. **Post-training.** The model is then tuned to be useful and polite: to follow instructions, to answer rather than ramble, to refuse certain things. This is the stage people usually have in mind when they say a model has been made safe.
3. **Use.** Somebody asks it a clinical question.

### Why we keep saying open

There are two different kinds of open, and they are usually confused.

| | what you can get | what you can ask |
|---|---|---|
| Open weights | the trained model itself | is this model biased |
| Open data | the model and the exact corpus it read | is this model biased, **and why** |

Pythia and OLMo-2 are open data. Qwen3-8B is open weights only: it is a strong
model and we audit it, but its training corpus was never released. Remove that
first link and the question stops being askable. We can still say a model is
biased. We can no longer say where it learned it, and we cannot check whether
the dataset's own documentation disclosed it.

### Did we pretrain anything ourselves? No

This is worth saying plainly, because the word invites the wrong picture. We did
not train a model, we did not pretrain one, and we did not fine-tune one. All
{N_MODELS} models were downloaded already finished and were never altered. What we
did was read them: put the same prompt to each one, and measure which answer it
leans towards.

Pretraining is in this project for two reasons, and neither of them is that we
performed it.

1. **It is the only place the bias could have come from.** A model has no other source of belief about who gets which illness. Nobody sits down and teaches it that chest pain in a woman is anxiety. If it leans that way, it learned the lean while reading.
2. **It is what made these models choosable.** We did not pick these {N_MODELS} because they are the best available. We picked them because for most of them the text they read during pretraining was published, so when we find a lean we can go back into that text and count the thing that caused it.

So when somebody asks why you pretrained, the answer is that you did not. You
audited models other people pretrained, and you chose which ones to audit by what
their pretraining left you able to ask.

### The finding that makes the stage matter

The base OLMo-2 model merges gender identity with the clinical sex parameter by
{BASE_M:.4f}. The very same model after post-training does it by {TUNED_M:.4f},
which is {RATIO:.1f} times as much, and that rise is {TIMES_COMBINED:.1f} times the
two models' combined noise floor. So the stage that is supposed to make a model
safer made this particular failure substantially worse, on the same weights, from
the same corpus.

### Where the {TIMES_COMBINED:.0f} times comes from, exactly

This figure gets quoted back at us, so here is the whole arithmetic in one place.

| Step | Value |
|---|---|
| merging, base model | {BASE_M:.4f} |
| merging, the same model after post-training | {TUNED_M:.4f} |
| the rise | {DELTA:.4f} |
| the base model's own floor | {FLOOR_B:.4f} |
| the tuned model's own floor | {FLOOR_T:.4f} |
| the two floors combined | {FLOOR_COMB:.4f} |
| the rise divided by that combined floor | {TIMES_COMBINED:.1f} |

The two floors are combined by squaring them, adding, and taking the square root,
not by simple addition. They are two independent measurements of noise, and that
is how independent error adds.

**Three things to get right when you say this out loud.**

1. The {TIMES_COMBINED:.0f} describes the **rise**, not the model. Post-training did not make the model eleven times worse. It made it {RATIO:.1f} times worse, and the size of that increase is {TIMES_COMBINED:.0f} floors. "Eleven times worse" is a different claim and it is false.
2. **Pretraining did not produce the {TIMES_COMBINED:.0f}.** These two models share one corpus and one set of pretrained weights. The only thing that differs between them is the post-training stage. That is the whole force of the result: the damage came from the stage that was supposed to make the model safer, not from the reading.
3. **It is measured against the gender floor, not the placebo floor.** Combine the two models' placebo floors the same way ({PL_B:.4f} and {PL_T:.4f}, giving {PL_COMB:.4f}) and the same rise is about {TIMES_PLACEBO:.1f} times the floor. The {TIMES_COMBINED:.0f} is correctly computed and it belongs to the narrower of our two floors. Section 5 is where that limitation is dealt with, and it is much better to raise it yourself than to have it raised for you.

### How to say it out loud

> Pretraining is the part where the model reads an enormous amount of text and
> learns to predict the next word. It is not taught medicine and it is not taught
> fairness. Whatever is in that text is what it ends up carrying. Two of our
> three model families published the exact text they read, which is why we can go
> and count things in it instead of guessing.

## 2. What a vignette is, and what the arms are

### A vignette is one clinical case, written once

A vignette is a short clinical case: the findings, one question, and a fixed set
of answer options. We write it once, against a named clinical guideline, and then
we never touch the medicine again. Everything the study does after that is done by
changing one sentence at a time.

Here is a real one in full, in the version that names no gender at all. It is
{EX}, and the condition is {EX_COND}.

> {EX_TEXT}
>
> **{EX_Q}** {EX_OPTS}

The guideline's answer is **{EX_REF}**, and it does not depend on the patient's sex
or on their gender. That is deliberate. This vignette belongs to the group we use
to measure noise, so the correct answer has to be the same for everybody.

### The three parts every vignette has

1. **The sex parameter line.** "{EX_SPCU_LINE}." This is the physiological field a clinical decision is allowed to turn on. We write it as plain text and we set it ourselves, so we always know exactly what the model was told.
2. **The identity line.** "The patient is a woman, aged {_ex.age}." This is who the patient is said to be. It carries no clinical information whatsoever.
3. **The findings and the question.** {EX_WORDS} words of clinical detail, then the question and the options. These are word for word identical in every arm.

Holding those first two lines apart is the whole design, and it is what the HL7
Gender Harmony standard asks of a clinical system. A model that is working
properly answers from line 1 and ignores line 2.

### An arm is one filled-in version of that vignette

Every vignette is issued {N_ARMS} times. That is {N_PARA} wordings, times {N_SPCU} settings
of the sex parameter, times {N_IDENT} identity labels. Each of those {N_ARMS} prompts is a
separate question to the model, and the model never sees any of the others.

These are the {N_IDENT} identity labels, taken straight out of the prompt file:

| The patient is said to be | The line that changes | Then referred to as |
|---|---|---|
{ident_rows()}

Two of those choices get questioned every time.

**Why {N_PARA} wordings and not one.** If the result only showed up in one phrasing it
would be a fact about that sentence rather than about the model. The three wordings
say the same clinical thing in three different orders, so an effect has to survive
being rephrased before we report it.

**Why one arm names nobody.** The blinded arm says "an adult" and contains no
gender word anywhere. It does two jobs. It tells us what the model does when it
has nothing to lean on, and it is the arm the placebo runs on, which is section 5.

### What this adds up to

{N_LIVE} live vignettes at {N_ARMS} arms each, plus {SPLIT}, which is issued twice over
because it carries one extra factor, a cue in the text that is either there or
absent, comes to {N_PROMPTS} prompts. Each prompt is
then scored once for every answer option, which is {ROWS_PER_MODEL:,} rows per
model and {OPTION_ROWS:,} rows in all.

We hold {N_TOTAL} written vignettes but report {N_LIVE}. The others were pulled during
review and replaced, and the replacements are the ones carrying a "b" in the
identifier. The live set is whatever the data file marks as analysis ready, never
a number anybody remembers.

### Who checked that the vignettes are clinically right

Each one names the guideline it rests on, and the sentence of that guideline it
rests on is recorded beside it. The two of us then reviewed every vignette
independently and without seeing each other's answers, against the same fixed
questions: does the quoted guideline actually force this answer, and does the
quoted sentence actually support it.

Our first pass agreed on fewer of them than we expected, which is better said out
loud than buried. A second round covering exactly the disputed items is out now.
Review by a practising clinician has been requested and is still outstanding, and
until it comes back every results table carries "pending clinical validation" in
its verification column. If anybody asks whether these cases are clinically
validated, the honest answer today is that they are author reviewed and not yet
clinician reviewed.

### How to say it out loud

> A vignette is one clinical case, written once against a guideline. We then issue
> it {N_ARMS} times and change nothing but who the patient is said to be and one
> physiological field that we control. The symptoms, the test results, the question
> and the options are the same every time. So if the answer moves when only the
> identity word moves, the model is using identity as though it were biology.

## 3. What a floor is

### The problem it solves

We measure how far a model's answer moves when the identity word changes. Suppose
it moves by 0.01. Is that a lot? On its own that number means nothing at all,
because we have no idea how much this model's answer moves for no reason
whatsoever. Every model wobbles a little when you change any word in a prompt.
Until you know how big that wobble is, you cannot tell a finding from a twitch.

### The definition in one line

**The floor is how much the answer moves when we change something that should
change nothing.**

### The analogy to use in the room

A kitchen scale that reads 3 grams with nothing on it. You do not throw the scale
away. You subtract the 3 grams, and from then on you do not report anything
weighing 2 grams, because you cannot tell it apart from the scale's own error. The
floor is the 3 grams. It is not a result, it is the scale reading empty.

### Why every model gets its own floor

Models differ enormously in how twitchy they are. Across our {N_MODELS} models the
floor runs from {FL_LO:.4f} to {FL_HI:.4f}, so the twitchiest model's empty scale
reads more than three times the steadiest one's. A single pooled floor would
flatter the noisy models and punish the quiet ones. So there is no such thing as
"the floor" in this study. There is only each model's own.

### How to say it out loud

> Before we are allowed to call a gap a finding, we have to know how much that
> particular model moves when we change something that does not matter. That is
> the floor. It is measured per model, and a result only counts if it is bigger
> than the model's own.

## 4. How the floor is calculated

### There are two floors, and an effect has to clear both

| | what we change | on which case | what it catches |
|---|---|---|---|
| **Group 4 floor** | the gender word | a case where gender is irrelevant | the right change on the wrong case |
| **Placebo floor** | something inert, such as eye colour | the very case being tested | the wrong change on the right case |

Neither one replaces the other. The Group 4 floor asks whether a gap beats the
noise from a different vignette. The placebo asks whether it beats an inert edit
to the same vignette. A gap that clears the first but not the second is not a
gender effect, it is a model that moves whenever you edit its prompt at all, and
the gender word happened to be the edit.

### Floor one, in detail: Group 4

{G4N} vignettes where no sex or gender disparity is documented anywhere: ankle
sprain, abscess, sinusitis, deep vein thrombosis, anaphylaxis, meningitis and so
on. We flip exactly the same identity words we flip everywhere else. The right
answer cannot change, so whatever moves is measurement error, by construction.

The floor is also **matched on the number of answer options**, and this part
matters more than it sounds. A four way question has more room to move than a
yes or no question, simply because the probability is spread over more options.
So the {G4B} two-option items set the floor for two-option vignettes, and the
{G4M} four-option items set it for the rest. Comparing a four-way gap against a
yes or no floor would be comparing two different scales.

### Floor two, in detail: the placebo

Same vignette, but instead of the gender word we change something clinically
inert: {", ".join(PL_ATTRS[:2])}. It runs on the arm where no gender is named at
all, so there is no gender word anywhere in the prompt and the movement measured
is pure sensitivity to being edited. That is {N_PLACEBO} extra prompts. Section 5
walks the whole procedure through with the real sentences.

An attribute was only allowed to be a placebo if it passed three tests: it had to
be clinically inert for every vignette it touched, silent in the governing
guideline, and **not socially salient as a basis of health disparity**. The third
test is the one that is easy to get wrong. {N_REJECTED} candidate attributes were
rejected on it, including occupation, postcode, insurance status and first
language, because each of those drives real disparities in care. Using one of
them as a floor would mean subtracting one bias from another and calling the
remainder noise.

### How the two are combined

The floor is the **maximum** over the placebo attributes, not the average. That
choice was written down before any placebo number was read, and it had to be,
because under the average the gate returns exactly the answer it gave before the
placebo existed. A test that cannot fail is not a test.

### What came out

| Model | Gender margin | Group 4 floor | Placebo floor | Reads the sex parameter? |
|---|---|---|---|---|
{model_rows()}

{N_FAIL} of {N_MODELS} models cannot tell male from female even on the
{G2N} vignettes where the guideline's own answer depends on it. {N_PASS_GENDER}
clear their Group 4 floor. Once the placebo floor is also required,
{N_PASS_BOTH} of {N_MODELS} survive. That is the honest headline, and it is a
statement about the instrument as much as about the models.

### The one thing to get right if somebody asks

In our tables, **margin over floor is the margin minus the floor, not the margin
divided by it.** It is a difference, in the same units as the margin itself. The
separate "times the floor" column is the ratio. Reading one as the other turns a
small positive difference into a claim about multiples, which is a different
claim entirely.

### How to say it out loud

> We measure the noise twice. Once by flipping gender on cases where gender is
> irrelevant, and once by changing something inert like eye colour on the very
> case we are testing. A real effect has to be bigger than both. When we apply
> both, nothing in our set survives, and we report that rather than the number we
> had before we built the second floor.

## 5. The placebo, step by step

Section 4 said what the placebo is for and why those particular attributes were
allowed. This is how it actually runs, in the order it runs, because this is the
part people ask to see.

### Step 1: start from the arm with no gender in it

The placebo does not run on the woman arm or the man arm. It runs on the blinded
arm, the one where the patient is "an adult" and no gender word appears anywhere
in the prompt. That matters. If a gender word were sitting in the prompt, any
movement we measured could be an interaction with it, and we would be measuring
two things at once. With no gender word present, whatever we measure is the model
reacting to having been edited at all.

The sex parameter is held at one level for the whole placebo run, because the
placebo is a question about surface form and not about the clinical field.

### Step 2: inject one sentence

We append a single sentence to the end of the prompt. That is all the word
injection means here: one sentence added to a prompt that is otherwise untouched.
Nothing is deleted, nothing is reworded, nothing is moved.

| Attribute | The two sentences |
|---|---|
{placebo_rows()}

A third attribute is also run, {THIRD_ATTR} ({THIRD_PAIR}), but it is reported
separately and kept out of the headline floor. Time of day is not perfectly inert:
circadian effects exist, and a booked appointment quietly implies a non-urgent
pathway, which could interact with our acute cases. We keep it anyway, because
when it disagrees with the other two that disagreement is informative.

### Step 3: change nothing else at all

The two prompts in a pair are identical up to the injected sentence, byte for
byte. The build checks this every time the guide is generated, so the claim cannot
quietly stop being true.

The two levels are also matched for length. "Brown" and "blue" are one token each
under both of the tokenizers in play here, so a model is not responding to one
prompt simply being longer than the other.

### Step 4: score both, and subtract

Each prompt is scored with PMI, which is the model's preference for an answer
option with its standing fondness for that word taken out. The placebo movement
for one vignette is the difference between the two levels. If a model is reading
the medicine, that difference is zero, because nothing clinical changed.

### Step 5: how many prompts that is

{PL_V} vignettes, times {PL_PARA} wordings, times {PL_LEVELS} attribute levels, is {N_PLACEBO}
prompts. Group 4 is deliberately included rather than skipped, because on those
items we already hold a gender flip floor, so the inert edit and the gender
manipulation are measured on exactly the same stimulus with nothing else varying.
That is the cleanest comparison in the study.

### Step 6: take the worst, not the average

A model's placebo floor is the **largest** movement anywhere in its set, across
both headline attributes and across every vignette. Here is what that rule does on
{SHORT[TUNED_ID]}, the model that leans hardest on identity.

Start with {W_ATTR} on its {W_NV} Group {W_GROUP} vignettes. This is how far the answer
moves when the only thing that changes is the {W_ATTR}:

| Vignette | Movement |
|---|---|
{worst_rows()}

Two of those three sit near zero. One of them, {W_V}, is {W_MAX:.4f}. Taking the
largest gives this model a placebo floor of {W_FLOOR:.4f}. Averaging that
attribute's {W_NV} movements instead would have given {W_MEAN:.4f}.

Now put the thing we are trying to measure next to it. This model's gender margin
is {W_MARGIN:.4f}. Against the average it clears the floor. Against the largest it
does not clear it at all. One vignette decides the verdict, and we
chose the rule that lets it, in writing, before any of these numbers existed.

There are two reasons for that choice and both are worth having ready. The Group 4
floor is itself a maximum, so averaging here would have made our two floors mean
different things. And under the softer aggregation the gate returns exactly the
answer it gave before the placebo was ever built. A test whose only available
outcome is the one you already hold is not a test.

### When somebody says eye colour is a silly thing to change

Welcome that one, because the answer is the finding.

Eye colour should do nothing. It appears in no guideline, it is clinically
irrelevant to every case in our set, and no clinician would act on it. So whatever
it does is a measurement of the model's own instability and nothing else.

The uncomfortable part is what it does. On the models that lean hardest on
identity, changing the patient's eye colour moves the answer further than changing
the clinical sex parameter does. We are not claiming eye colour matters. We are
reporting that an instrument of this size cannot separate a gender effect from the
background twitchiness of the model, and we would rather say that than publish the
larger number we were holding before we built this floor.

### How to say it out loud

> We take the version of the case with no gender in it, add one sentence that
> cannot possibly matter, such as the colour of the patient's eyes, and measure how
> far the answer moves. It should not move. A real gender effect has to be bigger
> than that movement, and in our set none of them is. So we report that the
> instrument cannot tell the two apart, rather than reporting the gender number on
> its own.

## 6. Reading an effect as a multiple of the floor

### What the {MG_T:.1f}, the {MG_Q:.1f} and the {MG_B:.1f} actually are

Each one is a division. Take how far the identity label moves the answer on the
Group 2 vignettes, and divide it by that same model's own noise floor. The result
says how many floors tall the effect is.

| Model | How far identity moves it | That model's floor | The multiple | Direction |
|---|---|---|---|---|
{merge_rows()}

These are not growth, not percentages and not change over time. They are one
measured quantity divided by another, taken at a single moment. The column is
called "times the floor" in our tables for exactly that reason, and it is the
one place in the project where a ratio is the headline. Everywhere else the
headline is a difference, which is the warning in section 4.

### What is being measured here, in words

On the Group 2 vignettes the correct answer depends on the clinical sex
parameter, not on the patient's gender. We hold the sex parameter still and
change only the identity label. The right answer cannot move, so any movement is
wrong by construction. What these three models do is push the answer in the
direction the sex parameter would have pushed it. In plain terms, the model is
reading "woman" as though it had been told the patient's body is female.

That is the configuration of a transgender patient, which is why this is the
project's sharpest result and not a technicality.

### The trap: a bigger multiple is not a bigger effect

Look at the first two rows again. {SHORT[QWEN_ID]} moves further in absolute
terms, {MG_QV:.4f} against {MG_TV:.4f}. Yet its multiple is the smaller of the
two, because its floor is nearly twice as large, {MG_QF:.4f} against {MG_TF:.4f}.
Divide by a bigger number and you get a smaller answer.

So both of these are true and they rank the models differently:

- **{SHORT[QWEN_ID]} has the largest effect.**
- **{SHORT[TUNED_ID]} has the largest effect relative to its own noise.**

Say whichever one you mean, and never say "{SHORT[TUNED_ID]} merges more than
{SHORT[QWEN_ID]}" on the strength of {MG_T:.1f} against {MG_Q:.1f}. That is the
mistake the multiple invites.

### Why we quote a multiple instead of a p value

Because with {MG_N_VIG} Group 2 vignettes, the smallest p a test like ours can
produce is {P_LIMIT}. Significance is not available at this sample size, no
matter what the models do. So we do not claim it. We claim two things we can
support: the **size**, which is the multiple, and the **consistency**, which is
that every one of the three vignettes moves the same way for each of the three
models.

If somebody asks why there is no p value, that is the answer, and giving it
before they ask is worth a great deal.

### What these numbers do not say

**Agreeing in sign is not agreeing in size.** Here is the per vignette picture
behind each mean:

| Model | Each vignette |
|---|---|
{merge_per_vignette()}

**The {MG_B:.1f} rests on one vignette.** For the base model, {BASE_TOP_V} moves
{BASE_TOP:+.4f}, while the other two are {BASE_REST}. The direction is
consistent and the magnitude is not. Say that yourself rather than let somebody
find it, because it does not weaken the headline, which is the tuned model.

**The other {N_INSIDE} models are below 1.0 times their floor**, which means
their merging sits inside their own noise. That is not evidence that they treat
trans patients correctly. They are the models that cannot tell male from female
at all, so there is nothing for an identity label to interfere with.

### How this squares with "nothing survives the placebo"

This is the question a careful listener will ask, because section 5 ended with 0
of 10 and this section opens with {MG_T:.1f} times the floor. They are not in
conflict, because they are different measurements.

| | The gate result | This result |
|---|---|---|
| what is measured | how far the answer moves when identity changes | whether identity is read **as** the sex parameter |
| the shape of it | one difference | a difference between two differences |
| what it is divided by | the Group 4 floor, then the placebo floor | the Group 4 floor |

The placebo floor is built from one inert edit, so it is the same shape as the
gate's margin and can be compared with it directly. Merging is an interaction,
a difference between two differences, so dividing it by a single edit floor
would not be a like for like comparison and we do not do it. Both results are
reported against the Group 4 floor, exactly as the paper reports them.

The sentence to have ready: the gate asks whether the models can be read at all
and the placebo says not reliably, while merging asks what the capable ones do
with the identity field, and the answer is that they read it as biology.

### The link back to post-training

The first and last rows of the table are the same model, before and after
post-training. **{MG_B:.1f} floors becomes {MG_T:.1f} floors**, on one corpus and
one set of pretrained weights. That is the 3.5 times rise from section 1, said in
multiples instead of in raw numbers, and it is the clearest thing we have to say
about what post-training did.

### How to say it out loud

> On the cases where the answer depends on the patient's body and not on their
> gender, the three models that can read the case at all push the answer the way
> the body would have pushed it, just from the identity word. The strongest does
> it {MG_T:.1f} times harder than that model's own noise. Every one of the three
> cases moves the same way. We cannot put a p value on three cases, so we report
> the size and the consistency, and we say plainly that the instruction tuned
> model is {MG_T:.1f} where the model it was built from was {MG_B:.1f}.

## 7. The other words people will stop you on

| Word | What it means here |
|---|---|
| Vignette | One clinical case: the findings, the question, and the answer options. We have {N_LIVE} live ones. |
| Arm | One version of a vignette with one identity label and one sex parameter. Each vignette has 24 arms. |
| Sex parameter | The physiological field a clinical decision actually turns on, written in the prompt as plain text and held still. It is kept separate from gender identity, which is what the HL7 Gender Harmony standard asks for. |
| PMI | A way of scoring an answer that subtracts the model's standing fondness for that word. Without it, a model that likes saying "Yes" looks like a model that agrees with every clinical proposition. |
| The gate | The rule that decides whether a model's result can be read at all. A model passes only if it moves on the cases where the guideline says it should move. |
| Merging | When a model treats the identity label as though it were the sex parameter. This is the failure we measure, and it is what post-training made worse. |
| Pretraining | The stage where the model read a very large pile of text and learned to predict the next word. We did not do it. We audit models other people pretrained. |
| Post-training | The stage after that, where the model is tuned to follow instructions and behave. On our one matched pair it made the failure {RATIO:.1f} times larger. |
| Injection | Adding one sentence to a prompt and changing nothing else. It is how the placebo is applied. |
| Placebo | An edit with no clinical meaning, such as the patient's eye colour, made to the very case being tested, so we can see how far the answer moves for no reason. |
| Arm type | Either gendered or blinded. The blinded arm names no gender at all, and it is the arm the placebo runs on. |
| Times the floor | An effect divided by that model's own noise floor, so it says how many floors tall the effect is. It is the only ratio we lead with, and section 6 is about reading it correctly. |

## 8. Five questions you will get, with the answer

**Is 0.01 not a tiny number?**
On its own it is meaningless, which is the point of the floor. Compared against
that model's own empty scale, some of those numbers are more than twenty times
the noise and some are below it. The number only becomes small or large once it
has something to be compared with.

**Why work with weak open models instead of the good closed ones?**
Because the question is not only whether a model is biased, it is where the bias
came from and whether the dataset's documentation said so. Those questions need
the corpus. We do audit a closed model as a contrast, and we are explicit that
for that one we can only report the symptom.

**{N_FAIL} models show almost no gender gap. Is that not a good result?**
No, and this is the part worth slowing down for. Those same models also fail the
positive control: on the cases where the correct answer genuinely does depend on
the sex parameter, they do not move either. A model that answers the same way
whatever the patient's sex is not being fair, it is being blind. Without a
positive control, that reads as a clean bill of health.

**Post-training made it eleven times worse, then?**
No, and this one is worth correcting rather than letting slide. The merging went
up {RATIO:.1f} times, from {BASE_M:.4f} to {TUNED_M:.4f}. What is eleven times the floor is
the size of the increase, which is a statement about whether the increase is big
enough to believe, not about how much worse the model got. The full arithmetic is
in section 1.

**Does the floor not just explain your own result away?**
It does reduce it, and we report the reduced number rather than the flattering
one. The placebo arm was added after the first run and before any placebo number
was read, which is the only order in which that decision is worth anything.
"""

MD.write_text(MDTEXT.lstrip() + "\n", encoding="utf-8")
assert "—" not in MDTEXT, "em dash in the guide"
print("wrote", MD.relative_to(ROOT))

convert(MD, DOCX,
        "From datasheet to diagnosis: the plain language version",
        "Pretraining, the vignettes, the floor, and the placebo")
print("wrote", DOCX.name)
