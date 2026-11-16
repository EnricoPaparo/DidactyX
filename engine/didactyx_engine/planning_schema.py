"""Contratti dei risultati generativi e controlli indipendenti sul percorso."""

import math


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


S = {"type": "string"}
N = {"type": "number"}
def array(item): return {"type": "array", "items": item}
STRINGS = array(S)
GOAL = obj({"id": S, "description": S})
HOURS = obj({"theory": N, "laboratory": N, "assessment": N})
CONTEXT = obj({
    "subject": S, "school_context": S, "class_profile": S, "starting_knowledge": STRINGS,
    "goals": array(GOAL), "required_topics": STRINGS, "optional_topics": STRINGS,
    "preferences": STRINGS, "total_hours": N,
    "hours": obj({**HOURS["properties"], "recovery": N, "buffer": N}),
    "assumptions": STRINGS, "curriculum_references": STRINGS,
})
UDA_PROPERTIES = {
    "id": S, "title": S, "description": S, "period": S, "prerequisites": STRINGS,
    "annual_goal_ids": STRINGS, "objectives": array(GOAL), "knowledge": STRINGS,
    "skills": STRINGS, "competences": STRINGS, "topics": STRINGS, "optional_topics": STRINGS,
    "methods": STRINGS, "assessment": STRINGS, "hours": HOURS,
}
PROJECT = obj({"id": S, "title": S, "description": S, "competences": STRINGS,
               "milestones": array(obj({"uda_id": S, "description": S, "deliverable": S}))})
STRUCTURE = obj({"udas": array(obj(UDA_PROPERTIES)), "projects": array(PROJECT), "review_notes": STRINGS})
LESSON = obj({
    "id": S, "title": S, "description": S,
    "kind": {"type": "string", "enum": ["theory", "laboratory", "assessment"]},
    "duration_hours": N, "objective_ids": STRINGS, "concepts": STRINGS,
    "prerequisite_lesson_ids": STRINGS, "methods": STRINGS, "project_ids": STRINGS,
})
PLAN = obj({"context": CONTEXT, "udas": array(obj({**UDA_PROPERTIES, "lessons": array(LESSON)})),
            "projects": array(PROJECT), "review_notes": STRINGS})
REVIEW = obj({"summary": S, "findings": array(obj({
    "kind": {"type": "string", "enum": ["error", "coherence", "didactic"]},
    "location": S, "description": S, "suggestion": S,
}))})


def validate(value, schema, path="$"):
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                validate(value, option, path)
                return
            except (ValueError, TypeError): pass
        raise ValueError(f"{path}: blocco non riconosciuto")
    kind = schema["type"]
    if kind == "object":
        if not isinstance(value, dict) or set(value) != set(schema["properties"]):
            raise ValueError(f"{path}: campi diversi dal contratto previsto")
        for key, child in schema["properties"].items(): validate(value[key], child, f"{path}.{key}")
    elif kind == "array":
        if not isinstance(value, list): raise ValueError(f"{path}: elenco atteso")
        for i, item in enumerate(value): validate(item, schema["items"], f"{path}[{i}]")
    elif kind == "string":
        if not isinstance(value, str): raise ValueError(f"{path}: testo atteso")
    elif kind == "number":
        if type(value) not in (int, float) or not math.isfinite(value): raise ValueError(f"{path}: numero non valido")
    elif kind == "boolean":
        if type(value) is not bool: raise ValueError(f"{path}: valore booleano atteso")
    if "enum" in schema and value not in schema["enum"]: raise ValueError(f"{path}: valore non previsto")


def plan_errors(plan):
    """Vincoli strutturali e quantitativi, separati dal giudizio del modello."""
    try: validate(plan, PLAN)
    except ValueError as error: return [str(error)]
    errors = []
    context = plan["context"]
    if context["total_hours"] <= 0: errors.append("Il monte ore annuale deve essere positivo.")
    if any(value < 0 for value in context["hours"].values()): errors.append("Le ore annuali non possono essere negative.")
    if not math.isclose(sum(context["hours"].values()), context["total_hours"], abs_tol=0.01):
        errors.append("La ripartizione delle ore non coincide con il totale annuale.")
    if not plan["udas"]: errors.append("Mancano le UDA.")
    if not context["goals"]: errors.append("Mancano gli obiettivi annuali.")
    all_ids = []
    def ids(items, label):
        found = [item["id"] for item in items]
        if any(not value.strip() for value in found) or len(found) != len(set(found)):
            errors.append(f"Identificativi vuoti o duplicati in {label}.")
        all_ids.extend(found)
        return set(found)
    goals = ids(context["goals"], "obiettivi annuali")
    uda_ids = ids(plan["udas"], "UDA")
    project_ids = ids(plan["projects"], "progetti")
    lessons = [lesson for uda in plan["udas"] for lesson in uda["lessons"]]
    lesson_ids = ids(lessons, "lezioni")
    positions = {lesson["id"]: index for index, lesson in enumerate(lessons)}
    totals = {key: 0 for key in HOURS["properties"]}
    covered_goals = set()
    for uda in plan["udas"]:
        name = uda["title"] or uda["id"]
        objectives = ids(uda["objectives"], f"obiettivi di {name}")
        if not objectives: errors.append(f"{name}: obiettivi assenti.")
        if not uda["lessons"]: errors.append(f"{name}: lezioni assenti.")
        if not uda["title"].strip(): errors.append("Un'UDA è priva di titolo.")
        if set(uda["annual_goal_ids"]) - goals: errors.append(f"{name}: obiettivi annuali inesistenti.")
        covered_goals.update(uda["annual_goal_ids"])
        subtotal = {key: 0 for key in totals}
        covered_objectives = set()
        for lesson in uda["lessons"]:
            if not lesson["title"].strip() or lesson["duration_hours"] <= 0:
                errors.append(f"{name}: titolo o durata della lezione non validi.")
            subtotal[lesson["kind"]] += lesson["duration_hours"]
            if not lesson["objective_ids"] or set(lesson["objective_ids"]) - objectives:
                errors.append(f"{lesson['title']}: collegamento agli obiettivi dell'UDA non valido.")
            covered_objectives.update(lesson["objective_ids"])
            if set(lesson["project_ids"]) - project_ids: errors.append(f"{lesson['title']}: progetto inesistente.")
            for prerequisite in lesson["prerequisite_lesson_ids"]:
                if prerequisite not in lesson_ids or positions[prerequisite] >= positions[lesson["id"]]:
                    errors.append(f"{lesson['title']}: prerequisito non precedente o inesistente ({prerequisite}).")
        if objectives - covered_objectives: errors.append(f"{name}: alcuni obiettivi non sono coperti dalle lezioni.")
        for key in totals:
            if uda["hours"][key] < 0 or not math.isclose(subtotal[key], uda["hours"][key], abs_tol=0.01):
                errors.append(f"{name}: ore {key} diverse dalla somma delle lezioni.")
            totals[key] += uda["hours"][key]
    for key in totals:
        if not math.isclose(totals[key], context["hours"][key], abs_tol=0.01):
            errors.append(f"Le ore {key} delle UDA non coincidono con quelle annuali.")
    if goals - covered_goals: errors.append("Alcuni obiettivi annuali non sono collegati alle UDA.")
    for project in plan["projects"]:
        for milestone in project["milestones"]:
            if milestone["uda_id"] not in uda_ids: errors.append(f"{project['title']}: tappa in un'UDA inesistente.")
    if len(all_ids) != len(set(all_ids)): errors.append("Gli identificativi devono essere univoci nell'intero percorso, inclusi gli obiettivi.")
    return errors
