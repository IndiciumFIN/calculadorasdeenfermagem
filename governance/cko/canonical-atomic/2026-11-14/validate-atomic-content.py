#!/usr/bin/env python3
import csv,hashlib,io,json,pathlib,zipfile
d=pathlib.Path(__file__).resolve().parent
manifest=json.loads((d/"GIT_SYNC_MANIFEST.json").read_text())
errors=[]
def check(x,msg):
 if not x:errors.append(msg)
def j(z,n):return json.loads(z.read(n))
def count(z,n):
 with io.TextIOWrapper(z.open(n),encoding="utf-8-sig",newline="") as f:return sum(1 for x in csv.DictReader(f))
for a in manifest["archives"]:
 p=d/"archives"/a["filename"]
 check(p.exists(),"missing archive "+a["filename"])
 if p.exists():
  data=p.read_bytes()
  check(hashlib.sha256(data).hexdigest()==a["sha256"],"wrong sha256 "+p.name)
  check(len(data)==a["bytes"],"wrong size "+p.name)
  with zipfile.ZipFile(p) as z:
   check(z.testzip() is None,"CRC issue "+p.name)
   check(len(z.namelist())==a["entries"],"wrong number of files "+p.name)
   check(all(".." not in pathlib.PurePosixPath(x).parts and not x.startswith("/") for x in z.namelist()),"unsafe path "+p.name)
with zipfile.ZipFile(d/"archives"/manifest["archives"][0]["filename"]) as a,zipfile.ZipFile(d/"archives"/manifest["archives"][1]["filename"]) as b:
 m08=j(a,"ATOMIC_ASSERTION_EVIDENCE_BINDINGS.json");m09=j(b,"M09_ATOMIC_ASSERTION_EVIDENCE_BINDINGS.json")
 claims=m08+m09
 check(len(m08)==34 and len(m09)==12,"claim counts")
 check(len({x["claim_id"] for x in claims})==46,"claim ids duplicated")
 check(len({x["evidence_atom_id"] for x in claims})==43,"source evidence count")
 check(len(j(a,"CONTENT_MASTERS_DRAFT.json"))==3 and len(j(b,"M09_CONTENT_MASTERS_REVISIONS_DRAFT.json"))==3,"content master count")
 check(len(j(a,"QUIZ_DRAFT.json"))==8 and len(j(b,"M09_QUIZ_DRAFT.json"))==3,"quiz count")
 check(len(j(a,"FLASHCARDS_DRAFT.json"))==10 and len(j(b,"M09_FLASHCARDS_DRAFT.json"))==4,"flashcard count")
 check(count(a,"CORPUS_EVIDENCE_ATOMS_28001_METADATA.csv")==28001,"evidence metadata rows")
 check(count(a,"CORPUS_TOPIC_EVIDENCE_9102_CANDIDATES.csv")==9102,"topic candidate rows")
 check(count(a,"LEGACY_29_CLAIMS_HOLD_REVIEW.csv")==29,"legacy held claims")
 check(all(x.get("approved",False) is False for x in claims),"claim prematurely approved")
 check(all(x.get("publication_allowed",x.get("release_allowed",False)) is False for x in claims),"claim release bypass")
 check(all(x.get("status")=="HOLD_HUMAN" for x in j(a,"CONTENT_MASTERS_DRAFT.json")+j(b,"M09_CONTENT_MASTERS_REVISIONS_DRAFT.json")),"content release bypass")
 snapshot=d/"PMO_REGISTER_SNAPSHOT_M08_M09.json"
 if snapshot.exists():
  regs={x["register"]:x["rows"] for x in json.loads(snapshot.read_text())["registers"]}
  check({x[0] for x in regs["CLAIM_LEDGER"]}=={x["claim_id"] for x in claims},"PMO claim mismatch")
  check({x[0] for x in regs["EVIDENCE_ATOMS"]}=={x["evidence_atom_id"] for x in claims},"PMO evidence mismatch")
print(json.dumps({"status":"FAIL" if errors else "PASS","claims":46,"distinct_atoms":43,"publication":False,"scope":"artifact integrity only; clinical/legal HOLD","errors":errors},ensure_ascii=False))
raise SystemExit(bool(errors))
