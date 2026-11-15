#!/usr/bin/env python3
"""Deterministic, fail-closed CKO curriculum/market audit. No network or DB writes.

Reads existing versioned *candidate* catalogs from W7; writes derived reports only.
Does NOT approve clinical, editorial, legal, curriculum, or release gates.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path

DATA_ROOT = Path("governance/cko/reconciliation/2026-11-14/w7/curriculum")
REQUIRED_KEYS = (
    "cofen", "programs", "academicComponents", "ufcspaComponents",
    "marketAds", "marketTaxonomy", "marketCrosswalk", "rightsCoverage", "contentIndex",
)


def json_file(path: Path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def json_lines(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as handle:
        result = []
        for number, raw in enumerate(handle, 1):
            if raw.strip():
                item = json.loads(raw)
                if not isinstance(item, dict):
                    raise ValueError(f"{path}:{number}: expected object")
                result.append(item)
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def assert_unique(items: list[dict], key: str, name: str) -> None:
    values = [item.get(key) for item in items]
    if not values or any(not v or not isinstance(v, str) for v in values):
        raise ValueError(f"{name}: missing or invalid {key}")
    if len(set(values)) != len(values):
        raise ValueError(f"{name}: duplicate {key}")


def build_report(repo_root: Path, revision: str = "UNKNOWN") -> dict:
    root = repo_root / DATA_ROOT
    manifest_path = root / "management/EXECUTION_MANIFEST_v1.0.0.json"
    wo_path = root / "management/WORK_ORDERS_v1.0.0.jsonl"
    manifest = json_file(manifest_path)
    if manifest.get("schema_version") != "1.0.0":
        raise ValueError("Unrecognized execution manifest schema")
    paths = manifest["sources_relative_to_w7_curriculum"]
    if any(key not in paths for key in REQUIRED_KEYS):
        raise ValueError("Manifest has missing mandatory source path")
    # Do not let a modified manifest invent legal/clinical approval.
    if any(bool(v) for v in manifest["publication_gates"].values()):
        raise ValueError("Publication gate unexpectedly true: human review required")
    if manifest["automation_contract"]["mode"] != "AUDIT_REPORT_ONLY":
        raise ValueError("Automation must remain audit-only")

    inputs = {"manifest": manifest_path, "workorders": wo_path}
    for key in REQUIRED_KEYS:
        p = Path(paths[key])
        if p.is_absolute() or ".." in p.parts:
            raise ValueError(f"Unsafe input path for {key}")
        inputs[key] = root / p
    for name, p in inputs.items():
        if not p.is_file():
            raise FileNotFoundError(f"Missing mandatory input {name}: {p}")

    cofen = json_lines(inputs["cofen"])
    programs = json_lines(inputs["programs"])
    components = json_lines(inputs["academicComponents"])
    ufc = json_lines(inputs["ufcspaComponents"])
    jobs = json_lines(inputs["marketAds"])
    taxonomy = json_file(inputs["marketTaxonomy"])
    prior_crosswalk = json_file(inputs["marketCrosswalk"])
    rights = json_file(inputs["rightsCoverage"])
    content = json_file(inputs["contentIndex"])
    orders = json_lines(inputs["workorders"])
    for name, rows, field in [
        ("cofen", cofen, "specialty_id"), ("programs", programs, "program_id"),
        ("curricular_components", components, "candidate_item_id"),
        ("ufcspa", ufc, "id"), ("job", jobs, "job_id"),
        ("work_orders", orders, "work_order_id"),
    ]:
        assert_unique(rows, field, name)
    valid_specialties = {s["specialty_id"] for s in cofen}
    valid_programs = {p["program_id"] for p in programs}
    skills_dict = taxonomy["skill_taxonomy"]
    if any(not j.get("source_url", "").startswith("https://") for j in jobs):
        raise ValueError("Job source URL missing/invalid")
    for j in jobs:
        if j.get("cofen_specialty_id") not in valid_specialties:
            raise ValueError(f"Unknown specialty on job {j['job_id']}")
        signals = j.get("skill_signals", {})
        for cls in ("required", "preferred", "responsibilities", "behavioral_explicit"):
            if not isinstance(signals.get(cls), list):
                raise ValueError(f"Missing classification {cls} on job {j['job_id']}")
            if any(code not in skills_dict for code in signals[cls]):
                raise ValueError(f"Unknown skill code on job {j['job_id']}")
        if j.get("status_observed") not in ("NOT_VERIFIED", "CLOSED", "TALENT_POOL"):
            raise ValueError("Unverified active/open status must not be inferred")
    for c in components:
        if c.get("clinical_publication_allowed") or c.get("curricular_semantics_approved"):
            raise ValueError("Candidate curriculum component has unauthorized approval")
    for c in ufc:
        if c.get("publication_allowed") or c.get("clinical_approval"):
            raise ValueError("UFCSPA component has unauthorized approval")
    if any(w.get("automatic_promotion_allowed") or w.get("clinical_publication_allowed") for w in orders):
        raise ValueError("Work order cannot contain auto-approval")
    order_ids = {w["work_order_id"] for w in orders}
    for w in orders:
        if any(dep not in order_ids for dep in w.get("depends_on", [])):
            raise ValueError(f"WO has unknown dependency: {w['work_order_id']}")
    if content.get("gates", {}).get("clinical_publication") or content.get("limits", {}).get("publication_allowed"):
        raise ValueError("Content publication gate is not allowed")
    if prior_crosswalk.get("publication_allowed"):
        raise ValueError("Prior market crosswalk has publication gate enabled")

    by_spec = collections.defaultdict(list)
    by_role = collections.defaultdict(list)
    for job in jobs:
        by_spec[job["cofen_specialty_id"]].append(job)
        by_role[job["specialty_group"]].append(job)
    candidate_titles = len(components) + len(ufc)
    specialty_rows = []
    backlog = []
    for s in cofen:
        sid = s["specialty_id"]
        linked = s.get("external_program_ids", [])
        sources = by_spec.get(sid, [])
        if not isinstance(linked, list):
            raise ValueError(f"Invalid program ids for {sid}")
        skills = collections.Counter()
        class_counts = {k: collections.Counter() for k in
                        ("required", "preferred", "responsibilities", "behavioral_explicit")}
        for job in sources:
            union = set()
            for cls, values in job["skill_signals"].items():
                union.update(values)
                class_counts[cls].update(set(values))
            skills.update(union)
        valid_links = sorted(set(linked).intersection(valid_programs))
        unresolved_links = sorted(set(linked).difference(valid_programs))
        row = {
            "specialty_id": sid,
            "cofen_area": s.get("area", ""),
            "specialty_name": s.get("name_as_displayed", ""),
            "cofen_subareas": len(s.get("child_lines", [])),
            "job_ad_count": len(sources),
            "job_roles": ",".join(sorted({j["specialty_group"] for j in sources})),
            "job_status": "CANDIDATE_SAMPLE" if sources else "NO_AD_IN_SAMPLE_NOT_NO_DEMAND",
            "candidate_program_count": len(valid_links),
            "candidate_program_ids": ";".join(valid_links),
            "unresolved_program_ids": ";".join(unresolved_links),
            "curriculum_status": "CODE_LINK_CANDIDATE_ONLY" if valid_links else "SOURCE_DISCOVERY_PENDING",
            "top_market_skills": "; ".join(
                f"{skills_dict[code]} ({count}/{len(sources)})"
                for code, count in sorted(skills.items(), key=lambda x: (-x[1], x[0]))[:5]
            ),
            "evidence_admission": "HOLD_SEMANTIC_AND_RIGHTS",
            "clinical_approval": "NO",
        }
        specialty_rows.append(row)
        if not sources:
            backlog.append({
                "id": f"CKO-{sid}-MARKET", "scope": sid, "priority": "P1",
                "status": "HOLD_MARKET_SAMPLE", "action": "Collect diverse, dated employer descriptions; do not infer zero demand",
                "source_count": 0, "human_approval": False,
            })
        elif len(sources) < 3:
            backlog.append({
                "id": f"CKO-{sid}-MARKET-DEPTH", "scope": sid, "priority": "P1",
                "status": "HOLD_SAMPLE_DEPTH", "action": "Expand employer/region/platform diversity; sample is too small",
                "source_count": len(sources), "human_approval": False,
            })
        if not valid_links:
            backlog.append({
                "id": f"CKO-{sid}-CURRICULUM", "scope": sid, "priority": "P1",
                "status": "HOLD_CURRICULUM_SOURCE", "action": "Find edition-specific primary syllabus or document justified absence",
                "source_count": 0, "human_approval": False,
            })
        elif unresolved_links:
            backlog.append({
                "id": f"CKO-{sid}-PROGRAM-ID", "scope": sid, "priority": "P0",
                "status": "HOLD_ID_CONFLICT", "action": "Reconcile referenced program ID against canonical inventory",
                "source_count": len(unresolved_links), "human_approval": False,
            })
        backlog.append({
            "id": f"CKO-{sid}-COMPETENCY", "scope": sid, "priority": "P1",
            "status": "HOLD_HUMAN_SEMANTIC", "action": "Review B/I/A prerequisites, ementa/skills/claims and PART_OF links",
            "source_count": len(valid_links), "human_approval": False,
        })
    if len(specialty_rows) != len(valid_specialties):
        raise ValueError("Incomplete specialty matrix")
    current = {
        "cofen_main": len(cofen),
        "cofen_subareas": sum(len(x.get("child_lines", [])) for x in cofen),
        "prior_programs": len(programs),
        "additional_title_occurrences": candidate_titles,
        "employer_ads_sample": len(jobs),
        "role_groups": len(by_role),
        "cofen_specialties_with_ads": len(by_spec),
        "cofen_specialties_with_no_ads_in_sample": len(cofen) - len(by_spec),
        "microtopic_drafts_w7": content.get("cumulative", {}).get("micro_lessons"),
        "articles_w7": content.get("cumulative", {}).get("articles"),
        "questions_w7": content.get("cumulative", {}).get("structured_quiz_items"),
    }
    old = manifest["baselines_observed"]
    drift = {
        k: {"baseline": old[k], "observed": v}
        for k, v in current.items()
        if k in old and old[k] != v
    }
    blocks = [
        {"id": "P0-RIGHTS", "status": "HOLD_RIGHTS", "detail": "No wholesale rights/license approval for 118 Drive vs 157 Supabase sources"},
        {"id": "P0-SOURCE-HASH", "status": "HOLD_SOURCE_VERSION" if not rights.get("hash_match") else "CHECK", "detail": "Different microtopic registry SHA snapshots require byte-level reconciliation"},
        {"id": "P0-SECURITY", "status": "HOLD_SECURITY", "detail": "Confirm RLS, grants and exposure for seven cko_evidence tables (historical audit)"},
        {"id": "P0-CLINICAL", "status": "HOLD_CLINICAL", "detail": "No automated human clinical or editorial approval"},
        {"id": "P0-PR70", "status": "HOLD_CI", "detail": "PR #70 must pass repository protections and required Gate Agregador"},
    ]
    for b in blocks:
        backlog.append({
            "id": b["id"], "scope": "GLOBAL", "priority": "P0",
            "status": b["status"], "action": b["detail"],
            "source_count": 0, "human_approval": False,
        })
    rights_state = rights.get("rights_snapshot", {}).get("rights_by_status", {})
    result = {
        "schema_version": "1.0.0",
        "baseline_date": manifest["baseline_date"],
        "reviewed_revision": revision,
        "counts": current,
        "source_catalog_rights_counts": rights_state,
        "rights_review_pending": rights_state.get("rights_audit_required"),
        "rates": {
            "job_ads_specialties": {"numerator": len(by_spec), "denominator": len(cofen)},
            "topic_authorial_drafts_partial_scope": {
                "numerator": content.get("cumulative", {}).get("micro_lessons"),
                "denominator": rights.get("total_microtopics"),
                "warning": "Work+Urgency only; NOT all COFEN specialties or clinical approvals",
            },
        },
        "baseline_drifts_not_silent_promotions": drift,
        "work_order_status": {w["work_order_id"]: w["status"] for w in orders},
        "blockers": blocks,
        "no_global_percent": True,
        "no_clinical_or_legal_approval": True,
        "no_database_change_or_publication": True,
        "input_files_sha256": {
            k: sha256_file(p) for k, p in sorted(inputs.items())
        },
        "specialties": specialty_rows,
        "backlog": backlog,
        "crosswalk_unmodified_original": True,
    }
    return result


def write_outputs(result: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage.json").write_text(
        json.dumps({k: v for k, v in result.items() if k not in ("specialties", "backlog")}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    rows = result["specialties"]
    with (out_dir / "specialty_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (out_dir / "backlog.jsonl").open("w", encoding="utf-8") as handle:
        for item in result["backlog"]:
            handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    counts = result["counts"]
    holds = collections.Counter(x["status"] for x in result["backlog"])
    state = [
        "# CKO — relatório automatizado de auditoria (NÃO é aprovação clínica)",
        "",
        f"**Baseline:** {result['baseline_date']} · **Revision:** \`{result['reviewed_revision']}\`",
        "",
        "| Indicador | Quantidade |",
        "|---|---:|",
    ]
    for name, value in counts.items():
        state.append(f"| {name} | {value} |")
    state += [
        "",
        f"**Cobertura de anúncios na amostra:** {result['rates']['job_ads_specialties']['numerator']}/{result['rates']['job_ads_specialties']['denominator']} especialidades (não é demanda nacional).",
        f"**Microaulas candidatas Work/Urg:** {result['rates']['topic_authorial_drafts_partial_scope']['numerator']}/{result['rates']['topic_authorial_drafts_partial_scope']['denominator']} — NÃO é cobertura geral Cofen.",
        "",
        "## Pendências geradas",
        "",
    ]
    state += [f"- {status}: {count}" for status, count in sorted(holds.items())]
    state += [
        "",
        "## Bloqueios de release", "",
    ]
    state += [f"- **{b['status']}** — {b['detail']}" for b in result["blockers"]]
    state += ["", "## Divergências de baseline", ""]
    if result["baseline_drifts_not_silent_promotions"]:
        for name, d in result["baseline_drifts_not_silent_promotions"].items():
            state.append(f"- {name}: esperado {d['baseline']}, observado {d['observed']}; revisar causa")
    else:
        state.append("- Nenhuma divergência numérica para as métricas monitoradas.")
    state += [
        "", "**Conclusão automática:** inventário auditado, pendências preservadas. NÃO promover conteúdo ou editar bases originais.",
        ""
    ]
    (out_dir / "status.md").write_text("\n".join(state), encoding="utf-8")
    (out_dir / "run_manifest.json").write_text(
        json.dumps({
            "schema_version": "1.0.0", "reviewed_revision": result["reviewed_revision"],
            "input_files_sha256": result["input_files_sha256"],
            "outputs": ["coverage.json", "specialty_matrix.csv", "backlog.jsonl", "status.md", "run_manifest.json"],
            "clinical_publication_allowed": False, "supabase_write": False, "merge_main": False,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--revision", default=os.environ.get("GITHUB_SHA", "UNKNOWN"))
    args = parser.parse_args()
    result = build_report(Path(args.repo_root).resolve(), revision=args.revision)
    write_outputs(result, Path(args.out_dir).resolve())
    print(json.dumps({
        "specialties": result["counts"]["cofen_main"],
        "job_ads": result["counts"]["employer_ads_sample"],
        "backlog": len(result["backlog"]),
        "drift": result["baseline_drifts_not_silent_promotions"],
        "release_allowed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
