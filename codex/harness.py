#!/usr/bin/env python3
"""Veil Codex harness — package validation.

TIER 1 INVARIANTS (blocking): build freshness, asset completeness, ledger schema
structure across all canonical collections, id uniqueness, ref resolution, ordered
ruling/changelog parity, timeline anchors, scene parity, structural text defects,
ruled-canon regressions.
TIER 2 LINT (non-blocking): mechanical publication defects + editorial phrasing watches.

Build correctness and story quality are deliberately not the same test.
"""
from pathlib import Path
import json, re, sys, collections
import build as _b

def read(p): return Path(p).read_text(encoding="utf-8")
CORE="Veil_Core_World_Bible.md"; ANNEX="Veil_Operational_Annexes.md"
MASTER="Veil_Unified_World_Bible.md"; LEDGER="veil_canon_ledger.json"; SCENES="Veil_Scenes.md"
core=read(CORE); annex=read(ANNEX); master=read(MASTER); scenes=read(SCENES)
db=json.loads(read(LEDGER)); s=json.dumps(db)
core_body=core.split("# CANON CHANGELOG")[0]

INV, LINT = [], []
def inv(c,m):
    if not c: INV.append(m)
def lint(c,m):
    if not c: LINT.append(m)

# ---- 0. build freshness + asset completeness ----
_ce,_ae=_b.build(master)
inv(core==_ce,"core: STALE — rerun build.py")
inv(annex==_ae,"annex: STALE — rerun build.py")
for r in _b.local_resources(master, core, annex, scenes):
    inv(Path(r).exists(), f"package: missing local resource '{r}' — artifacts not reproducible")

inv(master.startswith("# The Veil Codex — Unified World Bible"),
    "master: H1 title malformed")
inv(core.startswith("# The Veil Codex — Core World Bible"),
    "core: H1 title malformed")

# ---- 1. revision sync (parsed from master) ----
rev=_b.revision(master)
rev_core=rev.lstrip("# ").strip()          # compare content, not heading markup
for name,txt in [("core",core),("annex",annex),("scenes",scenes)]:
    inv(rev_core in txt, f"{name}: revision out of sync with master")
m=re.search(r"canon (CR[\d.]+) · build (CR[\d.]+) · narrative (NF\d+)", rev)
if m:
    c,b,n=m.groups(); mt=db["meta"]
    inv((mt.get("canon_revision"),mt.get("build_revision"),mt.get("narrative_revision"))==(c,b,n),
        "ledger: revision metadata out of sync")

# ---- 2. structural schema across ALL canonical collections (centralized discovery) ----
def canonical_collections(d):
    """Any list of dicts where >=1 member has both id and tag."""
    out={}
    def walk(o,path="root"):
        if isinstance(o,dict):
            for k,v in o.items(): walk(v,f"{path}.{k}")
        elif isinstance(o,list):
            if any(isinstance(x,dict) and "id" in x and "tag" in x for x in o):
                out[path]=o
            for i,v in enumerate(o): walk(v,f"{path}[{i}]")
    walk(d); return out
REQUIRED={"identity_status","narrative_status","game_state_status","unfiled"}
ENUM={"identity_status":{"C","D","P","R"},"narrative_status":{"C","D","P","R"},"game_state_status":{"G","n/a"}}
for cname, items in canonical_collections(db).items():
    for i,e in enumerate(items):
        if not (isinstance(e,dict) and "tag" in e): continue
        where=f"{cname}[{i}] ({e.get('id','?')})"
        st=e.get("status")
        inv(isinstance(st,dict), f"ledger: {where} status is not an object")
        if isinstance(st,dict):
            miss=REQUIRED-set(st)
            inv(not miss, f"ledger: {where} status missing {sorted(miss)}")
            for k,allowed in ENUM.items():
                if k in st: inv(st[k] in allowed, f"ledger: {where} status.{k}={st[k]!r} invalid")
            inv(isinstance(st.get("unfiled"),bool), f"ledger: {where} status.unfiled not boolean")

# ---- 3. id uniqueness + ref resolution ----
ids=collections.Counter(); refs=[]
SKIP_REF_PATHS={"meta"}                    # documentation blocks describe fields named `ref`
def walk(o):
    if isinstance(o,dict):
        if isinstance(o.get("id"),str): ids[o["id"]]+=1
        if isinstance(o.get("ref"),str): refs.append(o["ref"])
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
for k,v in db.items():
    if k in SKIP_REF_PATHS: continue
    walk(v)
for k,v in ids.items():
    if v>1: INV.append(f"ledger: duplicate id '{k}' ({v}) — cross-references must use `ref`")
canonical_ids={e["id"] for coll in canonical_collections(db).values() for e in coll
               if isinstance(e,dict) and isinstance(e.get("id"),str)}
for r in set(refs):
    inv(r in canonical_ids, f"ledger: unresolved ref '{r}' — not a canonical entity id")

# ---- 4. ORDERED ruling/changelog parity ----
led=[r["id"] for r in db["rulings_log"]]
chg=master.split("# CANON CHANGELOG")[1] if "# CANON CHANGELOG" in master else ""
mst=re.findall(r"\*\*([A-Z][A-Za-z0-9.]*\d(?:\.\d)?) — ", chg)
inv(led==mst, f"changelog: order differs from rulings_log (first divergence at index "
              f"{next((i for i,(a,b) in enumerate(zip(led,mst)) if a!=b), min(len(led),len(mst)))})")
seqs=[r.get("sequence") for r in db["rulings_log"]]
inv(seqs==list(range(1,len(seqs)+1)),
    "ledger: `sequence` must be unique, contiguous and ordered 1..N")
max_seq=max(x for x in seqs if x is not None)
inv(db["meta"].get("latest_ruling_sequence")==max_seq,
    f"ledger: latest_ruling_sequence stale ({db['meta'].get('latest_ruling_sequence')} != {max_seq})")
_eng=[r for r in db["rulings_log"] if r.get("kind")=="engineering"]
if _eng:
    inv(db["meta"].get("engineering_revision")==max(_eng,key=lambda r:r["sequence"])["id"],
        "ledger: engineering_revision stale")
_readme=Path("README.md")
if _readme.exists():
    _rt=_readme.read_text(encoding="utf-8")
    inv(_rt==_b.render_readme(db), "README: stale or hand-modified — rerun build.py")
EXPECTED_PRECEDENCE=[(1,"rulings",None),(2,"scenes","interior_state"),
                     (3,"doctrine_and_event_records","external_and_metaphysical_fact"),
                     (4,"merged_source_prose","default"),(5,"R4","same_generation_wording_only")]
_prec=db["meta"].get("canon_precedence")
inv(isinstance(_prec,list),"ledger: canon_precedence must be structured data, not prose")
if isinstance(_prec,list):
    inv(len(_prec)==5,f"ledger: canon_precedence must have 5 ranks (has {len(_prec)})")
    for rank,src,scope in EXPECTED_PRECEDENCE:
        row=next((p for p in _prec if p.get("rank")==rank),None)
        inv(row is not None,f"ledger: canon_precedence missing rank {rank}")
        if row:
            inv(row.get("source")==src,f"ledger: precedence rank {rank} source={row.get('source')!r}, expected {src!r}")
            if scope: inv(row.get("scope")==scope,f"ledger: precedence rank {rank} scope={row.get('scope')!r}, expected {scope!r}")
inv(all(r.get("kind") for r in db["rulings_log"]), "ledger: rulings missing `kind`")

# ---- 5. timeline anchors ----
tl=" ".join(f"{e.get('date','')} {e.get('event','')}" for e in db.get("events_timeline",{}).get("entries",[]))
for anchor in ["0 A.V.","450 A.V.","570","579","1983","1984","2325"]:
    inv(anchor in tl, f"ledger: timeline missing load-bearing anchor '{anchor}'")

# ---- 6. scene parity ----
for e in db.get("scenes",{}).get("entries",[]):
    inv(e.get("title","§") in scenes, f"scenes: ledger entry '{e.get('id')}' has no matching document heading")
doc_ids=re.findall(r"<!--\s*scene-id:\s*([a-z0-9\-]+)\s*-->", scenes)
led_ids=[e.get("id") for e in db.get("scenes",{}).get("entries",[])]
inv(doc_ids==led_ids, f"scenes: document ids {doc_ids} != ledger ids {led_ids}")
inv(len(re.findall(r"^## Scene \d+", scenes, re.M))==len(led_ids),
    "scenes: document scene count differs from ledger entries")

# ---- 7. structural text defects ----
def orphans(txt):
    out=[]
    for p in txt.split("\n\n"):
        d=0
        for i,ch in enumerate(p):
            if ch=="(": d+=1
            elif ch==")":
                if d==0:
                    pv=p[i-1] if i else ""
                    if pv.isalpha() or pv in "*”\"'": out.append(p[max(0,i-45):i+1].replace("\n"," "))
                else: d-=1
    return out
for doc,name in [(annex,"annex"),(core,"core"),(scenes,"scenes")]:
    for o in orphans(doc): INV.append(f"{name}: orphan paren …{o}")
inv(" |  |\n" not in core,"core: empty third table cells")
inv(not re.search(r"(?<=[a-z]{3})\.(?=[A-Z][a-z]{2})",core),"core: sentence concatenation")
inv("FIELD ERRATA" in annex,"annex: Vine manual missing Field Errata (IA1)")
for tok in ["#:~:text","real-world","fantasy foes","Edson",".edu","WWII"]:
    inv(tok not in annex,f"annex: external-source token '{tok}'")

# ---- 8. ruled-canon regressions ----
for bad in ["Shepherds are formed","Cycle of Kings and the Veil begin","normally witnessed once every 250",
            "43 autonomous Divisions","monarchy ceremonial","Rhen-Vel's long revenge is not",
            "not a plot necessity. It is a syllogism","the ordinary man is the unwritten man",
            "veteran of the Rift campaigns","Founding Location: Arclight Sprawl",
            "From this came the Order of the Silent Rose","self-sustaining harmonic ordinance",
            "platonic and pure","[NF2 counterweight]"]:
    inv(bad not in core_body,f"core: ruled-canon regression '{bad}'")
for good in ["Ruling CR2 — Eclipsera and the Arclight Sprawl","43 autonomous Directorates",
             "Doctrine of the Two Crowns","Raven scholars *suspect* Rhen-Vel","Design counterweights",
             "divergence, not virtue","government nobody elected","peoples are never threatforms",
             "Dramatized scene canon","He dared not","self-executing"]:
    inv(good in core,f"core: missing ruled canon '{good}'")
inv("eleven centuries" not in scenes,"scenes: 'eleven centuries' chronology error")

# ---- TIER 2: mechanical lint + phrasing watches ----
MECH=[(r"\b(the|a|an|on|at|to|from|toward|into)\s+\.", "article/preposition + blank + period"),
      (r"\s+[.,;:]", "space before punctuation"),
      (r"(?m)^\d{1,3}\*$", "dangling markdown numeral"),
      (r"\*{4,}", "overnested emphasis"),
      (r"[a-z]\.\d+\.\s*[A-Z]", "joined numbered-list entries"),
      (r",\s*—", "comma before em dash"),
      (r"—\s*,", "em dash before comma"),
      (r"Auto-updated|Canonical [Uu]pdate|^Sources$", "compiler/import artifact")]
def odd_emphasis(txt):
    """Odd '*' count in a paragraph = unbalanced emphasis (nested italic+bold is even)."""
    out=[]
    for p in txt.split("\n\n"):
        if re.search(r"\s\*\s", p) or p.lstrip().startswith("```"): continue   # multiplication / code
        if p.count("*") % 2: out.append(p.strip()[:60].replace("\n"," "))
    return out
for label, text in [("core",core),("annex",annex),("scenes",scenes)]:
    odd=odd_emphasis(text)
    lint(not odd, f"lint[{label}]: unbalanced emphasis ×{len(odd)}" + (f" e.g. {odd[:2]}" if odd else ""))
    for pat,why in MECH:
        hits=re.findall(pat,text,re.M)     # search CONTENT (probe-verified)
        sample="; ".join(str(x)[:30] for x in hits[:3])
        lint(not hits, f"lint[{label}]: {why} ×{len(hits)}" + (f" e.g. {sample}" if sample else ""))
for phrase,why in [("correct as ever","narration endorsing Strand"),
                   ("and unambiguously good","Compact framed without cost"),
                   ("eleven million","population figure pending baseline"),
                   ("the only person in her life","erases Serin"),
                   ("and he is right","narrator certifying Tobbin")]:
    lint(phrase not in core_body,f"lint: '{phrase}' — {why}")

print(f"INVARIANTS: {'PASS' if not INV else str(len(INV))+' FAILURES'}")
for f in INV: print("  ✗",f)
print(f"LINT:       {'clean' if not LINT else str(len(LINT))+' warnings'}")
for w in LINT: print("  •",w)
sys.exit(1 if INV else 0)
