"""Prova reale esplicita del workflow annuale, con dati esclusivamente fittizi."""

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
from didactyx_engine.server import Service
from didactyx_engine.planning_schema import plan_errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--regenerate", action="store_true")
    parser.add_argument("--minimal", action="store_true", help="Collaudo con solo partenza, traguardo e 12 ore")
    args = parser.parse_args()
    if args.minimal and args.regenerate: parser.error("Scegli --minimal oppure --regenerate.")
    args.data_dir = args.data_dir or ROOT / "tmp" / ("planning-minimal" if args.minimal else "planning-live")
    service = Service(args.data_dir)
    state_file = args.data_dir / "check-program.json"
    if state_file.exists():
        program_id = json.loads(state_file.read_text())["id"]
    else:
        program = service.store.create({"title": "Dal brief essenziale · collaudo" if args.minimal else "Fisica applicata · collaudo annuale", "class_label": "" if args.minimal else "2ª A · dati fittizi",
            "description": "Campione sintetico per verificare il workflow annuale.", "brief": {"free_text":
            "Parti dalle variabili e arriva alle condizioni if in Python. Ho 12 ore complessive." if args.minimal else
            "Classe seconda di istituto tecnico, studenti di 15-16 anni. Conoscono proporzioni e formule elementari ma faticano a collegarle ai fenomeni. "
            "Progetta un anno di 33 settimane per 66 ore: 28 teoria, 24 laboratorio, 6 verifiche, 4 recupero, 4 margine. "
            "Quattro UDA su misure ed errori, forze ed equilibrio, energia e calore, circuiti elettrici semplici. "
            "Obiettivi: misurare con consapevolezza, interpretare fenomeni con modelli semplici, descrivere esperimenti e collegare teoria e pratica. "
            "Laboratorio essenziale con materiali comuni. Un progetto progressivo deve collegare almeno due UDA. "
            "Le lezioni sono blocchi di una o due ore. Non sono forniti documenti curricolari ufficiali."}})
        program_id = program["id"]
        state_file.write_text(json.dumps({"id": program_id}))
    request = "Introduci i circuiti elettrici prima di energia e calore; mantieni quattro UDA e tutte le 66 ore con la ripartizione indicata. Ricalibra prerequisiti e progetto nell'intero anno." if args.regenerate else ""
    job = service.planning.start({"program_id": program_id, "change_request": request})
    print(json.dumps({"job_id": job["id"], "regeneration": args.regenerate}), flush=True)
    last = None
    try:
        while True:
            current = service.planning.store.job(job["id"])
            if (current["phase"], current["status"]) != last:
                print(json.dumps({key: current[key] for key in ("phase", "status", "message")}, ensure_ascii=False), flush=True)
                last = current["phase"], current["status"]
            if current["status"] != "running": break
            time.sleep(1)
        if current["status"] != "completed": raise RuntimeError(current.get("error") or current["message"])
        state = service.planning.store.state(program_id)
        plan = state["current_plan"]
        assert plan and not plan_errors(plan["data"])
        assert plan["data"]["context"]["total_hours"] == (12 if args.minimal else 66)
        if args.minimal:
            assert plan["data"]["context"]["assumptions"]
        else:
            assert len(plan["data"]["udas"]) == 4
            assert plan["data"]["context"]["hours"] == {"theory": 28, "laboratory": 24, "assessment": 6, "recovery": 4, "buffer": 4}
            assert all(l["duration_hours"] in (1, 2) for u in plan["data"]["udas"] for l in u["lessons"])
            assert any(len({m["uda_id"] for m in p["milestones"]}) >= 2 for p in plan["data"]["projects"])
        assert not plan["data"]["context"]["curriculum_references"]
        if args.regenerate:
            assert len(state["versions"]) >= 2
            titles = [u["title"].lower() for u in plan["data"]["udas"]]
            assert next(i for i,t in enumerate(titles) if "circuit" in t) < next(i for i,t in enumerate(titles) if "calore" in t)
        output = ROOT / "output" / "planning"
        output.mkdir(parents=True, exist_ok=True)
        filename = "minimal-plan.json" if args.minimal else f"annual-plan-v{plan['version']}.json"
        (output / filename).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({"passed": True, "version": plan["version"], "udas": len(plan["data"]["udas"]),
                          "lessons": sum(len(u["lessons"]) for u in plan["data"]["udas"]), "hours": plan["data"]["context"]["total_hours"]}), flush=True)
    finally: service.planning.shutdown()


if __name__ == "__main__": main()
