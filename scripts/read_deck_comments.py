"""Read PowerPoint comments out of a .pptx and say which slide and which shape.

python-pptx does not expose comments, so this reads the package directly. It is
deliberately format-agnostic: PowerPoint writes LEGACY comments
(ppt/comments/comment<N>.xml, PresentationML) on older builds and MODERN ones
(ppt/comments/modernComment_*.xml, the 2018 Microsoft extension) on current
ones, and a file can carry both. Rather than assume a schema, this pulls author,
timestamp, text and anchor out of whatever elements are present.

"Which card" is resolved geometrically: a comment carries an anchor point, so
the shape reported is the smallest shape whose box contains that point, or the
nearest shape if none contains it. The distance is printed so a weak match is
visible as a weak match.

    qa_venv/bin/python scripts/read_deck_comments.py <deck.pptx> [--json out.json]
"""
import sys, json, zipfile, re, posixpath
from xml.etree import ElementTree as ET
from pptx import Presentation
from pptx.util import Emu

R_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
EMU_IN = 914400.0


def local(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def rels_for(z, part):
    """part -> {rId: (type, resolved target)}"""
    d, base = posixpath.split(part)
    rp = posixpath.join(d, "_rels", base + ".rels")
    out = {}
    if rp not in z.namelist():
        return out
    for rel in ET.fromstring(z.read(rp)):
        tgt = rel.get("Target")
        if rel.get("TargetMode") == "External":
            continue
        out[rel.get("Id")] = (rel.get("Type", "").rsplit("/", 1)[-1],
                              posixpath.normpath(posixpath.join(d, tgt)))
    return out


def slide_ids(z):
    """presentation <p:sldId id=".."> -> 1-based position."""
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    out, i = {}, 0
    for lst in pres:
        if local(lst.tag) != "sldIdLst":
            continue
        for sld in lst:
            i += 1
            if sld.get("id"):
                out[sld.get("id")] = i
    return out


def slide_order(z):
    """presentation order -> slide part name, 1-based."""
    pres = ET.fromstring(z.read("ppt/presentation.xml"))
    rels = rels_for(z, "ppt/presentation.xml")
    order = []
    for lst in pres:
        if local(lst.tag) != "sldIdLst":
            continue
        for sld in lst:
            rid = next(v for k, v in sld.attrib.items() if k.endswith("}id"))
            order.append(rels[rid][1])
    return order


def authors(z):
    out = {}
    for part in ("ppt/commentAuthors.xml", "ppt/authors.xml"):
        if part not in z.namelist():
            continue
        for a in ET.fromstring(z.read(part)):
            aid = a.get("id") or a.get("{%s}id" % R_NS)
            nm = a.get("name") or a.get("initials") or "?"
            if aid is not None:
                out[str(aid)] = nm
            out[nm] = nm
    return out


def text_of(el):
    return " ".join(t.strip() for t in el.itertext() if t and t.strip())


def parse_comments(z, part):
    """Pull every comment element out of a comment part, whatever its schema."""
    root = ET.fromstring(z.read(part))
    found = []
    for el in root.iter():
        if local(el.tag) != "cm":
            continue
        pos = None
        for child in el.iter():
            if local(child.tag) == "pos":
                try:
                    pos = (int(child.get("x")), int(child.get("y")))
                except (TypeError, ValueError):
                    pass
                break
        body = ""
        for child in el:
            if local(child.tag) in ("text", "txBody"):
                body = text_of(child)
                break
        if not body:
            body = text_of(el)
        aid = el.get("authorId")
        # A modern comment records its target in a marker list rather than a
        # position: <ac:spMk id="46"/> is the shape, <ac:txMk cp=".." len=".."/>
        # the character range inside it, <pc:sldMk sldId=".."/> the slide. A
        # comment with ONLY a sldMk is attached to the slide as a whole.
        shape_id, txrange, sld_id = None, None, None
        for child in el.iter():
            t = local(child.tag)
            if t in ("spMk", "picMk", "graphicFrameMk", "cxnSpMk", "grpSpMk"):
                try:
                    shape_id = int(child.get("id"))
                except (TypeError, ValueError):
                    pass
            elif t == "txMk":
                try:
                    txrange = (int(child.get("cp")), int(child.get("len")))
                except (TypeError, ValueError):
                    pass
            elif t == "sldMk":
                sld_id = child.get("sldId")
        found.append(dict(author_id=aid, when=el.get("dt") or el.get("created"),
                          idx=el.get("idx") or el.get("id"), pos=pos,
                          shape_id=shape_id, txrange=txrange, sld_id=sld_id,
                          text=body, part=part))
    return found


def main(path, out_json=None):
    z = zipfile.ZipFile(path)
    comment_parts = [n for n in z.namelist()
                     if n.startswith("ppt/comments/") and n.endswith(".xml")]
    if not comment_parts:
        print("No comment parts in this file. Nothing was commented, or the "
              "comments were lost when the file was re-saved or regenerated.")
        return 1

    order = slide_order(z)
    sldmap = slide_ids(z)
    who = authors(z)
    prs = Presentation(path)
    # slide part name -> (1-based number, python-pptx slide)
    by_part = {}
    for i, part in enumerate(order):
        by_part[part] = (i + 1, prs.slides[i])

    # map each comment part to its slide, by relationship first, filename second
    owner = {}
    for part in order:
        for _t, tgt in rels_for(z, part).values():
            if tgt in comment_parts:
                owner[tgt] = part
    for cp in comment_parts:
        if cp in owner:
            continue
        m = re.search(r"comment[^0-9]*(\d+)", posixpath.basename(cp), re.I)
        if m:
            n = int(m.group(1))
            cand = f"ppt/slides/slide{n}.xml"
            if cand in by_part:
                owner[cp] = cand

    rows = []
    for cp in sorted(comment_parts):
        part = owner.get(cp)
        for c in parse_comments(z, cp):
            num, slide = (by_part[part] if part in by_part else (None, None))
            if num is None and c.get("sld_id") in sldmap:
                num = sldmap[c["sld_id"]]
                slide = prs.slides[num - 1]
            c["slide"] = num
            c["slide_part"] = part
            c["shape"], c["shape_text"], c["how"] = resolve(
                slide, c["pos"], c.get("shape_id"), c.get("txrange"))
            c["title"] = slide_title(slide) if slide is not None else None
            c["author"] = who.get(str(c["author_id"]), c["author_id"] or "?")
            rows.append(c)

    rows.sort(key=lambda r: (r["slide"] or 999, str(r["idx"])))
    print(f"{len(rows)} comment(s) in {path}\n")
    for c in rows:
        loc = f"slide {c['slide']}" if c["slide"] else f"unknown slide ({c['part']})"
        print(f"--- {loc}: {c['title'] or ''}")
        print(f"    on: {c['shape']}   [{c['how']}]")
        if c["shape_text"]:
            print(f"    that shape reads: {c['shape_text'][:110]}")
        print(f"    {c['author']}  {c['when'] or ''}")
        print(f"    > {c['text']}")
        print()
    if out_json:
        json.dump(rows, open(out_json, "w"), indent=1, default=str)
        print("written", out_json)
    return 0


def slide_title(slide):
    """The biggest piece of text in the top band. Robust across the hand-made
    slides and the generated ones, which name their title shape differently."""
    if slide is None:
        return None
    best, best_pt = "", -1.0
    for sh in slide.shapes:
        if not sh.has_text_frame or not sh.text_frame.text.strip():
            continue
        try:
            if int(sh.top) > 2.6 * EMU_IN:
                continue
        except (TypeError, ValueError):
            continue
        pt = max((r.font.size.pt for pa in sh.text_frame.paragraphs
                  for r in pa.runs if r.font.size), default=0.0)
        line = sh.text_frame.text.strip().split("\n")[0]
        if len(line) > 3 and pt > best_pt:
            best, best_pt = line[:70], pt
    if best:
        return best
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            return sh.text_frame.text.strip().split("\n")[0][:70]
    return ""


def resolve(slide, pos, shape_id=None, txrange=None):
    """Prefer the shape the comment NAMES; fall back to geometry."""
    if slide is None:
        return ("?", "", "no slide")
    if shape_id is not None:
        for sh in slide.shapes:
            if getattr(sh, "shape_id", None) != shape_id:
                continue
            txt = sh.text_frame.text.replace("\n", " / ") if sh.has_text_frame else ""
            how = f"anchored to shape id {shape_id}"
            if txrange and sh.has_text_frame:
                cp, ln = txrange
                picked = pick_range(sh, cp, ln)
                if picked:
                    return (sh.name, txt.strip(),
                            how + f', on the words "{picked}"')
            return (sh.name, txt.strip(), how)
        return (f"shape id {shape_id}", "",
                "the comment names a shape that is NOT in this file")
    if pos is None:
        return ("whole slide", "", "attached to the slide, not to any one shape")
    x, y = pos
    boxes = []
    for sh in slide.shapes:
        try:
            L, T, W, H = int(sh.left), int(sh.top), int(sh.width), int(sh.height)
        except (TypeError, ValueError):
            continue
        txt = sh.text_frame.text.strip().replace("\n", " / ") if sh.has_text_frame else ""
        boxes.append((sh.name, L, T, W, H, txt))
    inside = [b for b in boxes if b[1] <= x <= b[1] + b[3] and b[2] <= y <= b[2] + b[4]]
    if inside:
        # largest to smallest: the card, then whatever sits on it. Naming only
        # the innermost run gives "3 vignettes" when the useful answer is
        # "the GROUP 2 chip".
        inside.sort(key=lambda b: b[3] * b[4], reverse=True)
        chain = " > ".join(b[0] for b in inside[:4])
        tgt = inside[-1]
        return (chain, tgt[5],
                f"anchor at {x/EMU_IN:.2f}in, {y/EMU_IN:.2f}in, inside "
                f"{len(inside)} shape(s)")
    if not boxes:
        return ("whole slide", "", "slide has no shapes")
    def d(b):
        cx, cy = b[1] + b[3] / 2.0, b[2] + b[4] / 2.0
        return ((cx - x) ** 2 + (cy - y) ** 2) ** 0.5
    b = min(boxes, key=d)
    return (b[0], b[5], f"nearest shape, {d(b)/EMU_IN:.2f}in from the anchor")


def pick_range(sh, cp, ln):
    """The characters a txMk points at. cp counts within its own paragraph, so
    try each paragraph and return the first slice that is in range."""
    for para in sh.text_frame.paragraphs:
        t = "".join(r.text for r in para.runs)
        if cp + ln <= len(t):
            got = t[cp:cp + ln].strip()
            if got:
                return got
    whole = sh.text_frame.text
    return whole[cp:cp + ln].strip() if cp + ln <= len(whole) else ""


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    oj = None
    if "--json" in sys.argv:
        oj = sys.argv[sys.argv.index("--json") + 1]
    if not args:
        print(__doc__); sys.exit(2)
    sys.exit(main(args[0], oj))
