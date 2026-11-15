"""Prova separata di mappe strutturate e immagini native di Codex."""

import argparse
import json
from pathlib import Path
import shutil
import time

from probe_codex import AppServer, STRING, inspect, object_schema, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("output/feasibility"))
    parser.add_argument("--image", action="store_true", help="Esegue una richiesta reale di immagine nativa")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    server = AppServer(Path.cwd(), images=args.image)
    try:
        inspect(server)
        if args.image:
            image_probe(server, output)
        else:
            graph_probe(server, output)
    finally:
        server.close()


def graph_probe(server, output):
    lesson = json.loads((output / "lesson2.json").read_text())
    schema = object_schema({
        "title": STRING,
        "nodes": {"type": "array", "items": object_schema({"id": STRING, "label": STRING})},
        "edges": {"type": "array", "items": object_schema({"source": STRING, "target": STRING, "label": STRING})},
    })
    thread = server.start("Sei autore di mappe concettuali. Restituisci relazioni esplicite e verificabili.")
    graph, info = server.generate(thread["thread"]["id"],
        json.dumps(lesson, ensure_ascii=False) + "\nCrea una vera piccola mappa concettuale, non il diagramma dei passaggi di calcolo. Esattamente quattro nodi concettuali in quest'ordine: Equazione; Trasformazioni equivalenti; Soluzione; Verifica per sostituzione. Etichette al massimo di 32 caratteri. Tre archi collegano ogni concetto al successivo, con una breve relazione semantica esplicita (massimo 28 caratteri), per esempio: si risolve attraverso; permettono di trovare; si controlla mediante. Il titolo deve collegare la mappa al tema della lezione. Non mettere intere spiegazioni nelle etichette.", schema)
    ids = [node["id"] for node in graph["nodes"]]
    assert len(ids) == len(set(ids)) == 4
    assert len(graph["edges"]) == 3
    for index, edge in enumerate(graph["edges"]):
        assert edge["source"] == ids[index] and edge["target"] == ids[index + 1]
        assert edge["label"].strip()
    save(output / "concept_map.json", graph)
    save(output / "visual_results.json", {"structured_map": {**info, "nodes": 4, "edges": 3, "references_valid": True}})
    print("Mappa strutturata generata: quattro nodi e tre relazioni valide", flush=True)


def image_probe(server, output):
    thread = server.request("thread/start", {
        "cwd": str(output), "approvalPolicy": "never", "sandbox": "workspace-write", "ephemeral": True,
        "baseInstructions": "Sei un illustratore didattico. Usa esclusivamente il tool nativo di generazione immagini per produrre una vera immagine raster. Non usare shell, rete, skill, altri agenti o codice. Se il tool non è disponibile, dichiaralo senza simulare il risultato.",
    })
    thread_id = thread["thread"]["id"]
    server.current_thread = thread_id
    started = time.monotonic()
    turn_id = server.begin_turn(thread_id,
        "Genera una sola illustrazione didattica semplice: una bilancia a due piatti in equilibrio, su sfondo bianco, stile editoriale essenziale, linee blu scuro e accento ciano. Sul piatto sinistro una scatolina chiusa e tre piccoli pesi uguali; sul destro undici pesi uguali. Nessuna parola o numero nell'immagine. È una prova tecnica di accesso al tool immagini.")
    turn, text = server.finish_turn(turn_id, timeout=420)
    items = [n["params"]["item"] for n in server.notifications
             if n.get("method") == "item/completed" and n.get("params", {}).get("turnId") == turn_id
             and n.get("params", {}).get("item", {}).get("type") == "imageGeneration"]
    result = {"turn_status": turn["status"], "seconds": round(time.monotonic() - started, 2),
              "native_image_items": len(items), "image_saved": False, "assistant_response": text}
    for item in items:
        result["image_tool_status"] = item.get("status")
        saved_path = item.get("savedPath")
        if saved_path and Path(saved_path).is_file():
            suffix = Path(saved_path).suffix or ".png"
            target = output / ("native-illustration" + suffix)
            shutil.copyfile(saved_path, target)
            result["image_saved"] = True
            result["artifact"] = target.name
    save(output / "image_results.json", result)
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
