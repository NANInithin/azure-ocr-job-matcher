from typing import Any


class MatchingService:
    def match_candidate_to_job(
        self,
        candidate_profile: dict[str, Any],
        job_profile: dict[str, Any],
        candidate_text: str | None = None,
    ) -> dict[str, Any]:
        candidate_skills = set(s.lower() for s in candidate_profile.get("skills", []))
        required_skills = set(s.lower() for s in job_profile.get("required_skills", []))
        preferred_skills = set(s.lower() for s in job_profile.get("preferred_skills", []))

        matched_required = sorted(required_skills.intersection(candidate_skills))
        missing_required = sorted(required_skills - candidate_skills)
        matched_preferred = sorted(preferred_skills.intersection(candidate_skills))

        score = self._calculate_score(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            matched_required=matched_required,
            matched_preferred=matched_preferred,
        )

        decision = self._make_decision(
            required_skills=required_skills,
            missing_required=missing_required,
            score=score,
        )

        evidence = self._build_evidence(matched_required + matched_preferred, candidate_text)
        notes = self._build_notes(missing_required, matched_preferred, required_skills)

        return {
            "job_title": job_profile.get("title"),
            "candidate_name": candidate_profile.get("name"),
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "score": score,
            "decision": decision,
            "evidence": evidence,
            "notes": notes,
        }

    def _calculate_score(
        self,
        required_skills: set[str],
        preferred_skills: set[str],
        matched_required: list[str],
        matched_preferred: list[str],
    ) -> int:
        required_score = 0
        preferred_score = 0

        if required_skills:
            required_score = int((len(matched_required) / len(required_skills)) * 80)

        if preferred_skills:
            preferred_score = int((len(matched_preferred) / len(preferred_skills)) * 20)

        return required_score + preferred_score

    def _make_decision(
        self,
        required_skills: set[str],
        missing_required: list[str],
        score: int,
    ) -> str:
        if required_skills and not missing_required and score >= 85:
            return "strong_match"
        if len(missing_required) <= 1 and score >= 60:
            return "moderate_match"
        return "weak_match"

    def _build_evidence(self, matched_skills: list[str], candidate_text: str | None) -> dict[str, str]:
        if not candidate_text:
            return {}

        lines = [line.strip() for line in candidate_text.splitlines() if line.strip()]
        evidence = {}

        for skill in matched_skills:
            skill_lower = skill.lower()
            for line in lines:
                if skill_lower in line.lower():
                    evidence[skill] = line
                    break

        return evidence

    def _build_notes(
        self,
        missing_required: list[str],
        matched_preferred: list[str],
        required_skills: set[str],
    ) -> list[str]:
        notes = []

        if required_skills and not missing_required:
            notes.append("Candidate matches all required skills.")
        elif missing_required:
            notes.append(f"Candidate is missing {len(missing_required)} required skill(s): {', '.join(missing_required)}.")

        if matched_preferred:
            notes.append(f"Candidate also matches {len(matched_preferred)} preferred skill(s).")

        if not notes:
            notes.append("Limited evidence available for this match decision.")

        return notes