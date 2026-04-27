from typing import Any


class MatchingService:
    def match_candidate_to_job(self, profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
        candidate_skills = {skill.lower().strip() for skill in profile.get("skills", [])}
        required_skills = {skill.lower().strip() for skill in job.get("required_skills", [])}
        preferred_skills = {skill.lower().strip() for skill in job.get("preferred_skills", [])}

        matched_required = sorted(candidate_skills.intersection(required_skills))
        missing_required = sorted(required_skills.difference(candidate_skills))
        matched_preferred = sorted(candidate_skills.intersection(preferred_skills))

        required_score = (len(matched_required) / len(required_skills) * 70) if required_skills else 0
        preferred_score = (len(matched_preferred) / len(preferred_skills) * 20) if preferred_skills else 0
        profile_bonus = 10 if profile.get("linkedin") or profile.get("github") or profile.get("portfolio") else 0

        total_score = round(required_score + preferred_score + profile_bonus, 2)

        if len(missing_required) == 0 and total_score >= 75:
            decision = "strong_match"
        elif len(matched_required) > 0:
            decision = "partial_match"
        else:
            decision = "weak_match"

        notes = []
        if matched_required:
            notes.append(f"Matched required skills: {', '.join(matched_required)}")
        if missing_required:
            notes.append(f"Missing required skills: {', '.join(missing_required)}")
        if matched_preferred:
            notes.append(f"Matched preferred skills: {', '.join(matched_preferred)}")
        if profile_bonus:
            notes.append("Candidate has professional links or portfolio.")

        return {
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "score": total_score,
            "decision": decision,
            "notes": notes,
        }