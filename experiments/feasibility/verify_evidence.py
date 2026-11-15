"""Controlli offline sui risultati reali della prova, senza nuove richieste AI."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader

from probe_codex import save, validate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("output/feasibility"))
    args = parser.parse_args()
    output = args.input_dir.resolve()

    def load(name):
        return json.loads((output / name).read_text())

    results = load("results.json")
    assert results["completed"]
    assert results["environment"]["authentication"] == "chatgpt"
    assert results["checks"]["interruption"]["passed"]
    assert results["checks"]["resume_after_restart"]["passed"]
    assert not results["checks"]["resume_after_restart"]["context_reinjected"]
    schema = load("lesson.schema.json")
    for filename in ("lesson1.json", "lesson2.json"):
        validate(load(filename), schema)
    review = load("independent_review.json")
    assert {item["exercise_id"] for item in review["detected_errors"]} == {"E1"}
    assert review["exercise_count"] == 3 and review["teacher_instruction_preserved"]
    # Riscontro aritmetico indipendente sui tre casi fissi della prova.
    x1 = Fraction(19 - 3, 2)
    assert x1 == 8 and x1 != 16
    x2 = Fraction(62, 13)
    assert (3 * x2 - 2) / 4 + (x2 + 1) / 3 == 5
    assert -9 != 5  # E3 si riduce a -4x-9 = -4x+5.

    graph = load("concept_map.json")
    ids = {node["id"] for node in graph["nodes"]}
    assert len(ids) == 4 and len(graph["edges"]) == 3
    assert all(edge["source"] in ids and edge["target"] in ids and edge["label"].strip() for edge in graph["edges"])
    assert ET.parse(output / "concept-map.svg").getroot().tag.endswith("svg")

    image_result = load("image_results.json")
    assert image_result["image_saved"] and image_result["image_tool_status"] == "completed"
    with Image.open(output / image_result["artifact"]) as picture:
        picture.verify()

    reader = PdfReader(output / "didactyx-feasibility-sample.pdf")
    assert len(reader.pages) == 4
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert "Faro" in text and "Trasformazioni equivalenti" in text
    assert "\ufffd" not in text and "\u25a0" not in text
    assert len(list(reader.pages[-1].images)) >= 1
    summary = {"passed": True, "checks": ["chatgpt_authentication", "structured_lessons", "review_error_detection",
               "teacher_instruction_preserved", "independent_arithmetic", "valid_graph_references", "svg_parse",
               "native_raster_decode", "pdf_text_and_embedded_image", "interruption_and_resume"],
               "note": "Controlli tecnici sui campioni; non sostituiscono la valutazione didattica o visiva."}
    save(output / "offline_checks.json", summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
