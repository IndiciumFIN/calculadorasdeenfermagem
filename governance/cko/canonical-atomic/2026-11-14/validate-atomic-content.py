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
  blob=hashlib.sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()
  check(blob==a["git_blob"],"wrong Git blob SHA-1 "+p.name)
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
 # Verificação completa do registro PMO: ausência, lacunas e vínculos devem falhar.
snapshot=d/"PMO_REGISTER_SNAPSHOT_M08_M09.json"
check(snapshot.is_file(),"PMO snapshot is required")
check(manifest.get("publication_allowed") is False,"manifest publication hold")
check(manifest.get("release_status")=="CANDIDATE_HOLD_HUMAN","manifest release status")
check(manifest.get("content",{}).get("total",{}).get("approved_claims")==0,"approved claims must be zero")
check(manifest.get("content",{}).get("total",{}).get("published")==0,"published resources must be zero")
if snapshot.is_file():
 try:
  pmo=json.loads(snapshot.read_text(encoding="utf-8"))
  groups=pmo.get("registers",[])
  check(isinstance(groups,list),"PMO register list")
  regs={x["register"]:x["rows"] for x in groups}
  expected={"CLAIM_LEDGER":46,"EVIDENCE_ATOMS":43,"CONTENT_REGISTER":6,
            "SOURCE_REGISTER":2,"DOCUMENT_REGISTER":2,"CHANGE_IMPACT":2,
            "CONFLICT_REGISTER":1,"HOLD_HUMAN":1,"PMO_MASTER":1}
  check(len(groups)==len(expected) and set(regs)==set(expected),"PMO register names / duplicates")
  check(all(isinstance(regs.get(k),list) and len(regs[k])==n for k,n in expected.items()),
        "PMO register row counts")
  check(pmo.get("totals")==expected,"PMO declared totals")
  check(sum(len(x.get("rows",[])) for x in groups)==104,"PMO must have exactly 104 rows")
  check(pmo.get("release_allowed") is False,"PMO release must be false")
  for name,rows in regs.items():
   ids=[r[0] for r in rows if isinstance(r,list) and r and isinstance(r[0],str)]
   check(len(ids)==len(rows) and len(ids)==len(set(ids)),
         "PMO duplicate or missing row IDs: "+name)
  required=set(expected)
  if required.issubset(regs):
   claim_ids={x["claim_id"] for x in claims}
   evidence_ids={x["evidence_atom_id"] for x in claims}
   claim_rows=regs["CLAIM_LEDGER"]
   evidence_rows=regs["EVIDENCE_ATOMS"]
   source_ids={x[0] for x in regs["SOURCE_REGISTER"]}
   docs={x[0]:x[1] for x in regs["DOCUMENT_REGISTER"]}
   check({x[0] for x in claim_rows}==claim_ids,"PMO claim IDs mismatch")
   check({x[0] for x in evidence_rows}==evidence_ids,"PMO evidence IDs mismatch")
   check(all(x[4] in evidence_ids for x in claim_rows),"Claim references missing evidence")
   check(all(x[1] in docs and x[3] in claim_ids for x in evidence_rows),
         "Evidence references missing document or claim")
   check(all(s in source_ids for s in docs.values()),"Document references unknown source")
   check(all(len(x)>10 and x[9]=="PENDING_CLINICAL_AND_EDITORIAL_REVIEW"
             and x[10]=="EVIDENCE_BOUND_HOLD" for x in claim_rows),
         "Claim clinical/editorial hold bypass")
   check(all(len(x)>11 and x[11]=="EVIDENCE_BOUND_NOT_CLINICALLY_APPROVED"
             for x in evidence_rows),"Evidence approval bypass")
   masters=regs["CONTENT_REGISTER"]
   check(all(len(x)>10 and x[9]=="HOLD_HUMAN"
             and x[10]=="CANDIDATE_NO_PUBLICATION" for x in masters),
         "Content publication hold bypass")
   for row in masters:
    sources=[y.strip() for y in row[6].split(";") if y.strip()]
    linked=[y.strip() for y in row[7].split(";") if y.strip()]
    check(bool(sources) and set(sources).issubset(source_ids),
          "Content references unknown source: "+row[0])
    check(bool(linked) and set(linked).issubset(claim_ids),
          "Content references unknown claim: "+row[0])
   check(all(len(x)>8 and x[8]=="OPEN" for x in regs["HOLD_HUMAN"]),
         "Human hold removed from PMO")
 except (ValueError,TypeError,KeyError,IndexError,AttributeError) as exc:
  check(False,"PMO malformed: "+type(exc).__name__)
print(json.dumps({"status":"FAIL" if errors else "PASS","claims":46,"distinct_atoms":43,"publication":False,"scope":"artifact integrity only; clinical/legal HOLD","errors":errors},ensure_ascii=False))
raise SystemExit(bool(errors))
