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

        title = self._extract_title(lines)
        location = self._extract_location(text)
        minimum_years_experience = self._extract_years_experience(lower_text)

        required_section = self._extract_between_keywords(
            lower_text,
            start_keywords=["required", "requirements", "must have", "qualifications"],
            stop_keywords=["preferred", "nice to have", "good to have", "bonus"]
        )

        preferred_section = self._extract_between_keywords(
            lower_text,
            start_keywords=["preferred", "nice to have", "good to have", "bonus"],
            stop_keywords=[]
        )

        if required_section:
            required_skills = self._extract_skills(required_section)
        else:
            required_skills = self._extract_skills(lower_text)

        preferred_skills = self._extract_skills(preferred_section) if preferred_section else []

        preferred_set = set(preferred_skills)
        required_skills = [skill for skill in required_skills if skill not in preferred_set]

        return {
            "title": title,
            "company": None,
            "location": location,
            "required_skills": sorted(set(required_skills)),
            "preferred_skills": sorted(set(preferred_skills)),
            "minimum_years_experience": minimum_years_experience,
        }

    def _extract_title(self, lines: list[str]) -> str | None:
        for line in lines[:5]:
            clean = line.strip()
            if len(clean.split()) <= 8 and ":" not in clean.lower():
                return clean
        return None

    def _extract_location(self, text: str) -> str | None:
        patterns = [
            r"(?im)^location:\s*([^\n\r]+)",
            r"(?im)^based in:\s*([^\n\r]+)",
            r"(?im)^job location:\s*([^\n\r]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return None

    def _extract_years_experience(self, text: str) -> int | None:
        match = re.search(r"(\d+)\+?\s+years? of experience", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def _extract_between_keywords(
        self,
        text: str,
        start_keywords: list[str],
        stop_keywords: list[str]
    ) -> str:
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

        return section[:1200]

    def _extract_skills(self, text: str) -> list[str]:
        found = []
        for skill in COMMON_SKILLS:
            if skill in text:
                found.append(skill)
        return found