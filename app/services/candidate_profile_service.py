import re
from typing import Any


COMMON_SKILLS = [
    "python", "pytorch", "tensorflow", "opencv", "cuda", "c++", "sql",
    "fastapi", "docker", "kubernetes", "azure", "machine learning",
    "deep learning", "computer vision", "nlp", "rag", "linux", "git",
    "pandas", "numpy", "keras", "opencv", "cnn", "vae", "gan"
]


class CandidateProfileService:
    def extract_profile(self, text: str) -> dict[str, Any]:
        cleaned_text = text.strip()

        lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
        first_lines = lines[:8]

        email = self._extract_email(cleaned_text)
        phone = self._extract_phone(cleaned_text)
        linkedin = self._extract_link(cleaned_text, "linkedin.com")
        github = self._extract_link(cleaned_text, "github.com")
        portfolio = self._extract_portfolio(cleaned_text)
        name = self._extract_name(first_lines, email)
        skills = self._extract_skills(cleaned_text)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "skills": skills,
            "top_lines": first_lines[:5],
        }

    def _extract_email(self, text: str) -> str | None:
        match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> str | None:
        match = re.search(r"(\+?\d[\d\-\s]{7,}\d)", text)
        return match.group(0).strip() if match else None

    def _extract_link(self, text: str, domain: str) -> str | None:
        pattern = rf"(https?://[^\s]*{re.escape(domain)}[^\s]*|{re.escape(domain)}/[^\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_portfolio(self, text: str) -> str | None:
        matches = re.findall(r"(https?://[^\s]+|www\.[^\s]+)", text, re.IGNORECASE)
        for url in matches:
            lower = url.lower()
            if "linkedin.com" not in lower and "github.com" not in lower:
                return url
        return None

    def _extract_name(self, first_lines: list[str], email: str | None) -> str | None:
        for line in first_lines:
            if len(line.split()) <= 5 and "@" not in line and "linkedin" not in line.lower() and "github" not in line.lower():
                if not any(char.isdigit() for char in line):
                    return line
        if email:
            return email.split("@")[0].replace(".", " ").replace("_", " ").title()
        return None

    def _extract_skills(self, text: str) -> list[str]:
        lower_text = text.lower()
        found = []
        for skill in COMMON_SKILLS:
            if skill in lower_text:
                found.append(skill)
        return sorted(set(found))