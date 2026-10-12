import unittest

from recommendations import ground_recommendations


class RecommendationGroundingTests(unittest.TestCase):
    def test_recommendations_only_use_role_skills_and_resume_evidence(self):
        job = {
            "role": "Data Engineer",
            "required_skills": ["Python", "Kubernetes"],
            "preferred_skills": ["SQL"],
            "responsibilities": ["Deploy data services with Kubernetes."],
        }
        resume = {
            "skills": ["Python"],
            "experiences": [{"role": "Analyst", "description": "Built Python reports."}],
            "projects": [],
        }
        details = {"Matching skills": ["Python"], "Missing important skills": ["Kubernetes", "SQL"]}
        model_response = {
            "recommendations": [
                {
                    "skill": "Kubernetes",
                    "category": "Missing required skill",
                    "role_relevance": "Deploy services.",
                    "candidate_evidence": "No experience",
                    "learning_action": "Deploy a small containerized data service to a local Kubernetes cluster.",
                    "priority": "High",
                    "estimated_time": "2-4 weeks",
                },
                {
                    "skill": "Python",
                    "category": "Area with insufficient evidence",
                    "role_relevance": "Improve testing depth.",
                    "candidate_evidence": "Made up evidence",
                    "learning_action": "Add tests and performance profiling to a Python project.",
                    "priority": "Medium",
                    "estimated_time": None,
                },
                {
                    "skill": "Rust",
                    "category": "Missing required skill",
                    "role_relevance": "Not a job skill.",
                    "candidate_evidence": "Not demonstrated in the resume.",
                    "learning_action": "Build an example.",
                    "priority": "High",
                    "estimated_time": None,
                },
            ]
        }

        result = ground_recommendations(model_response, resume, job, details)
        by_skill = {item["skill"]: item for item in result}
        self.assertEqual(set(by_skill), {"Kubernetes", "Python"})
        self.assertEqual(by_skill["Kubernetes"]["category"], "Missing required skill")
        self.assertEqual(by_skill["Kubernetes"]["candidate_evidence"], "Not demonstrated in the resume.")
        self.assertIn("job description", by_skill["Kubernetes"]["role_relevance"])
        self.assertEqual(by_skill["Kubernetes"]["priority"], "High")
        self.assertEqual(by_skill["Kubernetes"]["estimated_time"], "2-4 weeks")
        self.assertEqual(by_skill["Python"]["category"], "Area with insufficient evidence")
        self.assertIn("Python", by_skill["Python"]["candidate_evidence"])

    def test_demonstrated_skill_is_not_reported_as_missing(self):
        result = ground_recommendations(
            [{
                "skill": "SQL",
                "category": "Missing preferred skill",
                "learning_action": "Build a query optimization project.",
                "priority": "Medium",
            }],
            {"skills": ["SQL"]},
            {"role": "Analyst", "required_skills": [], "preferred_skills": ["SQL"]},
            {},
        )
        self.assertEqual(result, [])

    def test_no_recommendation_for_skill_outside_actual_job_description(self):
        result = ground_recommendations(
            [{
                "skill": "Terraform",
                "category": "Missing required skill",
                "learning_action": "Build a small project.",
            }],
            {"skills": []},
            {"role": "Analyst", "required_skills": ["SQL"], "preferred_skills": []},
            {},
        )
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
