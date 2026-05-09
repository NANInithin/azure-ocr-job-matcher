import re
from typing import Any


COMMON_SKILLS = [
    "python", "pytorch", "tensorflow", "opencv", "cuda", "c++", "sql",
    "fastapi", "docker", "kubernetes", "azure", "machine learning",
    "deep learning", "computer vision", "nlp", "rag", "linux", "git",
    "pandas", "numpy", "keras", "cnn", "vae", "gan"
]


class JobProfileService:
    def parse_job_text(self, job_text: str) -> dict[str, Any]:
        text = job_text.strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        lower_text = text.lower()
        notes = []

        title = self._extract_title(lines)
        company = self._extract_company(lines)
        location = self._extract_location(text)
        minimum_years_experience = self._extract_years_experience(lower_text)

        required_section = self._extract_section(
            text=lower_text,
            start_keywords=["required", "requirements", "must have", "minimum qualifications", "qualifications"],
            stop_keywords=["preferred", "nice to have", "good to have", "bonus", "benefits", "about us"]
        )
        preferred_section = self._extract_section(
            text=lower_text,
            start_keywords=["preferred", "nice to have", "good to have", "bonus", "preferred qualifications"],
            stop_keywords=["benefits", "about us", "how to apply", "application process"]
        )
        fallback_section = self._extract_section(
            text=lower_text,
            start_keywords=["skills", "stack", "technologies", "experience"],
            stop_keywords=["benefits", "about us", "how to apply"]
        )

        if not title:
            notes.append("Could not confidently extract job title.")
        if not location:
            notes.append("Location not found explicitly in job text.")
        if minimum_years_experience is None:
            notes.append("Minimum years of experience not found explicitly.")

        if required_section:
            required_skills = self._extract_skills(required_section)
        elif fallback_section:
            required_skills = self._extract_skills(fallback_section)
            notes.append("Required skills inferred from a general skills/experience section.")
        else:
            required_skills = self._extract_skills(lower_text)
            notes.append("Required skills inferred from full job text because no explicit requirements section was found.")

        if preferred_section:
            preferred_skills = self._extract_skills(preferred_section)
        else:
            preferred_skills = []
            notes.append("No explicit preferred-skills section found.")

        preferred_set = set(preferred_skills)
        required_skills = [skill for skill in required_skills if skill not in preferred_set]

        if not required_skills:
            notes.append("No known skills matched from the parser skill list.")

        return {
            "title": title,
            "company": company,
            "location": location,
            "required_skills": sorted(set(required_skills)),
            "preferred_skills": sorted(set(preferred_skills)),
            "minimum_years_experience": minimum_years_experience,
            "notes": notes,
            "field_confidence": self._compute_confidence(
                title=title,
                company=company,
                location=location,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                minimum_years_experience=minimum_years_experience,
                notes=notes,
            ),
        }

    def _compute_confidence(
        self,
        title: str | None,
        company: str | None,
        location: str | None,
        required_skills: list[str],
        preferred_skills: list[str],
        minimum_years_experience: int | None,
        notes: list[str],
    ) -> dict[str, float]:
        title_conf = 0.7 if title else 0.0
        company_conf = 0.9 if company else 0.0
        location_conf = 1.0 if location else 0.0

        inferred = any("inferred" in n.lower() for n in notes)
        full_text_fallback = any("full job text" in n.lower() for n in notes)
        n_req = len(required_skills)
        if n_req == 0:
            req_conf = 0.0
        elif full_text_fallback:
            req_conf = 0.4
        elif inferred:
            req_conf = 0.6
        else:
            req_conf = 0.85 if n_req >= 3 else 0.7

        pref_conf = 0.8 if preferred_skills else 0.0
        exp_conf = 0.95 if minimum_years_experience is not None else 0.0

        return {
            "title": round(title_conf, 2),
            "company": round(company_conf, 2),
            "location": round(location_conf, 2),
            "required_skills": round(req_conf, 2),
            "preferred_skills": round(pref_conf, 2),
            "minimum_years_experience": round(exp_conf, 2),
        }

    def _extract_title(self, lines: list[str]) -> str | None:
        banned_prefixes = (
            "location:", "based in:", "job location:", "about", "company", "team",
            "responsibilities", "requirements", "qualifications", "preferred"
        )
        for line in lines[:6]:
            clean = line.strip()
            lower = clean.lower()
            if not clean:
                continue
            if any(lower.startswith(prefix) for prefix in banned_prefixes):
                continue
            if len(clean.split()) <= 8:
                return clean
        return None

    def _extract_company(self, lines: list[str]) -> str | None:
        patterns = [
            r"(?i)^company:\s*(.+)$",
            r"(?i)^about\s+([A-Z][A-Za-z0-9&,. \-]+)$",
            r"(?i)^join\s+([A-Z][A-Za-z0-9&,. \-]+)$",
        ]
        for line in lines[:10]:
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1).strip()
        return None

    def _extract_location(self, text: str) -> str | None:
        patterns = [
            r"(?im)^\s*location:\s*([^\n\r]+)",
            r"(?im)^\s*based in:\s*([^\n\r]+)",
            r"(?im)^\s*job location:\s*([^\n\r]+)",
            r"(?im)^\s*location\s*-\s*([^\n\r]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_years_experience(self, text: str) -> int | None:
        patterns = [
            r"(\d+)\+?\s+years?\s+of\s+experience",
            r"minimum of\s+(\d+)\s+years?\s+experience",
            r"minimum of\s+(\d+)\s+years?",
            r"(\d+)\+?\s+years?\s+in",
            r"(\d+)\s*-\s*\d+\s+years?\s+of\s+experience",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _extract_section(self, text: str, start_keywords: list[str], stop_keywords: list[str]) -> str:
        start_idx = -1
        for keyword in start_keywords:
            idx = text.find(keyword)
            if idx != -1 and (start_idx == -1 or idx < start_idx):
                start_idx = idx
        if start_idx == -1:
            return ""
        section = text[start_idx:]
        stop_idx = -1
        for keyword in stop_keywords:
            idx = section.find(keyword)
            if idx != -1 and idx > 0 and (stop_idx == -1 or idx < stop_idx):
                stop_idx = idx
        if stop_idx != -1:
            section = section[:stop_idx]
        return section[:1500]

    def _extract_skills(self, text: str) -> list[str]:
        found = []
        for skill in COMMON_SKILLS:
            pattern = self._skill_pattern(skill)
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(skill)
        return found

    def _skill_pattern(self, skill: str) -> str:
        escaped = re.escape(skill)
        return rf"(?<!\w){escaped}(?!\w)"