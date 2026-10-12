"""Validate and ground improvement recommendations in saved resume/job data."""

from __future__ import annotations

import re


_ALLOWED_CATEGORIES = {
    "Missing required skill",
    "Missing preferred skill",
    "Area with insufficient evidence",
}


def ground_recommendations(raw, resume_data, job_data, match_details):
    """Keep recommendations tied to actual job skills and candidate evidence."""
    if isinstance(raw, dict):
        raw = raw.get("recommendations", [])
    if not isinstance(raw, list):
        return []

    required = _skill_list(job_data, "required_skills")
    preferred = _skill_list(job_data, "preferred_skills")
    known = {skill.casefold(): (skill, "required") for skill in required}
    known.update({skill.casefold(): (skill, "preferred") for skill in preferred if skill.casefold() not in known})
    role = str(_value(job_data, "role") or "the target role").strip()
    responsibilities = _skill_list(job_data, "responsibilities")
    resume_evidence = _resume_evidence(resume_data)
    matched = _match_skills(match_details, "matching skills", "matched skills")
    output = []
    seen = set()

    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get("skill"), str):
            continue
        canonical = known.get(item["skill"].strip().casefold())
        if canonical is None:
            continue
        skill, requirement = canonical
        if skill.casefold() in seen:
            continue
        seen.add(skill.casefold())

        evidence = _find_evidence(skill, resume_evidence)
        if evidence is None and _contains_skill(skill, matched):
            evidence = f"The matching analysis lists {skill} as a matching skill."

        proposed_category = item.get("category")
        if evidence:
            # Existing evidence cannot be presented as a missing skill.
            if proposed_category != "Area with insufficient evidence":
                continue
            category = "Area with insufficient evidence"
        else:
            category = "Missing required skill" if requirement == "required" else "Missing preferred skill"
            evidence = "Not demonstrated in the resume."

        relevance = _ground_role_relevance(skill, requirement, role, responsibilities)
        action = _safe_text(item.get("learning_action"), limit=420)
        if not action or re.search(
            r"https?://|\bwww\.|\b(?:course|certification|certificate)\b|\bguarantee(?:d)?\b|\bensure selection\b",
            action,
            re.I,
        ):
            continue

        priority = {
            "Missing required skill": "High",
            "Missing preferred skill": "Medium",
            "Area with insufficient evidence": "Medium" if skill.casefold() in {value.casefold() for value in required} else "Low",
        }[category]
        estimate = item.get("estimated_time")
        if not isinstance(estimate, str) or not estimate.strip() or estimate.strip().lower() in {"unknown", "null", "n/a", "not enough information"}:
            estimate = None
        else:
            estimate = _safe_text(estimate, limit=80)

        output.append({
            "skill": skill,
            "category": category,
            "role_relevance": relevance,
            "candidate_evidence": evidence,
            "learning_action": action,
            "priority": priority,
            "estimated_time": estimate,
        })
    required_order = {skill.casefold(): index for index, skill in enumerate(required)}
    preferred_order = {skill.casefold(): index for index, skill in enumerate(preferred)}

    def recommendation_order(item):
        skill_key = item["skill"].casefold()
        if skill_key in required_order:
            return (0, required_order[skill_key])
        return (1, preferred_order.get(skill_key, len(preferred_order)))

    output.sort(key=recommendation_order)
    return output


def _value(data, key):
    if isinstance(data, dict):
        return data.get(key)
    return getattr(data, key, None)


def _skill_list(data, key):
    value = _value(data, key)
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item).strip() for item in value if isinstance(item, str) and item.strip()]


def _resume_evidence(data):
    relevant = {"skills", "experiences", "education", "projects", "certifications", "skills_used", "role", "description"}
    found = []

    def walk(value, key=""):
        if isinstance(value, dict):
            for child_key, child in value.items():
                if str(child_key).lower() in relevant:
                    walk(child, str(child_key).lower())
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child, key)
        elif isinstance(value, str) and value.strip():
            found.append(value.strip())

    walk(data)
    return found


def _find_evidence(skill, evidence):
    pattern = re.compile(rf"(?<![\w]){re.escape(skill)}(?![\w])", re.I)
    return next((entry for entry in evidence if pattern.search(entry)), None)


def _match_skills(details, *labels):
    if not isinstance(details, dict):
        return []
    normalized = {str(key).strip().lower().replace("_", " "): value for key, value in details.items()}
    for label in labels:
        value = normalized.get(label.lower().replace("_", " "))
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value]
    return []


def _contains_skill(skill, values):
    pattern = re.compile(rf"(?<![\w]){re.escape(skill)}(?![\w])", re.I)
    return any(pattern.search(value) for value in values)


def _ground_role_relevance(skill, requirement, role, responsibilities):
    for responsibility in responsibilities:
        if re.search(rf"(?<![\w]){re.escape(skill)}(?![\w])", responsibility, re.I):
            return f"The job description connects {skill} to this responsibility: {responsibility}"
    label = "required" if requirement == "required" else "preferred"
    return f"{skill} is listed as a {label} skill for the {role} role."


def _safe_text(value, limit):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:limit]
