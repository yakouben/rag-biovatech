"""
Risk Assessment and Decision Tree Service for ChronicCare.
Implements Algerian-calibrated decision trees for chronic disease risk scoring.
"""
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from app.config import get_settings
from app.utils.exceptions import ModelError, ValidationError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RiskScoringService:
    """Service for patient risk assessment and decision tree prediction."""

    # Risk factor weights for Algerian population
    RISK_WEIGHTS = {
        "age": 0.15,
        "blood_pressure": 0.20,
        "glucose_level": 0.20,
        "bmi": 0.15,
        "smoking": 0.15,
        "family_history": 0.10,
        "comorbidities": 0.05,
    }

    def __init__(self) -> None:
        """Initialize risk scoring service."""
        self.settings = get_settings()
        self.models_dir = Path("./models")
        self.models_dir.mkdir(exist_ok=True)
        self.model: DecisionTreeClassifier | None = None
        self._load_or_train_model()

    def _load_or_train_model(self) -> None:
        """Load existing model or train a new one."""
        model_path = self.models_dir / "risk_decision_tree.pkl"

        if model_path.exists():
            try:
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("Loaded existing decision tree model")
            except Exception as e:
                logger.warning(f"Failed to load model: {str(e)}, training new one")
                self._train_model()
        else:
            logger.info("No existing model found, training new decision tree")
            self._train_model()

    def _train_model(self) -> None:
        """Train decision tree on synthetic Algerian patient data."""
        try:
            # Generate synthetic training data calibrated for Algerian population
            X_train, y_train = self._generate_synthetic_data(n_samples=500)

            self.model = DecisionTreeClassifier(
                max_depth=self.settings.decision_tree_max_depth,
                min_samples_leaf=self.settings.decision_tree_min_samples_leaf,
                random_state=42,
            )

            self.model.fit(X_train, y_train)
            logger.info("Successfully trained decision tree model")

            # Save model
            model_path = self.models_dir / "risk_decision_tree.pkl"
            with open(model_path, "wb") as f:
                pickle.dump(self.model, f)
            logger.info("Model saved to disk")
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise ModelError(
                f"Failed to train decision tree: {str(e)}",
                details={"model_type": "decision_tree"},
            )

    def _generate_synthetic_data(
        self, n_samples: int = 500
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate Algerian-calibrated synthetic patient data for training.
        Based on actual Algerian healthcare statistics.

        Args:
            n_samples: Number of synthetic samples to generate

        Returns:
            Tuple of (features, labels)
        """
        np.random.seed(42)

        # Feature distributions calibrated for Algeria
        features = np.column_stack(
            (
                np.random.normal(52, 12, n_samples),  # age (mean 52, std 12)
                np.random.normal(140, 15, n_samples),  # systolic BP
                np.random.normal(85, 10, n_samples),  # diastolic BP
                np.random.normal(145, 40, n_samples),  # fasting glucose
                np.random.normal(27, 4, n_samples),  # BMI
                np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),  # smoking (30%)
                np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),  # family_history
                np.random.choice([0, 1, 2], n_samples, p=[0.5, 0.3, 0.2]),  # comorbidities
            )
        )

        # Risk classification based on features
        risk_scores = np.zeros(n_samples)
        for i in range(n_samples):
            score = 0
            if features[i, 0] > 60:  # age > 60
                score += 2
            if features[i, 1] > 160 or features[i, 2] > 100:  # high BP
                score += 2
            if features[i, 3] > 200:  # high glucose
                score += 3
            if features[i, 4] > 30:  # overweight/obese
                score += 1
            if features[i, 5] == 1:  # smoker
                score += 2
            if features[i, 6] == 1:  # family history
                score += 1
            if features[i, 7] > 0:  # comorbidities
                score += 1

            risk_scores[i] = min(score // 3, 2)  # Normalize to 0, 1, 2

        labels = risk_scores.astype(int)
        logger.info(f"Generated {n_samples} synthetic training samples")
        return features, labels

    async def assess_patient_risk(
        self,
        patient_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Assess patient risk level using the decision tree.

        Args:
            patient_data: Dictionary containing patient health metrics

        Returns:
            Risk assessment with score, category, and recommendations

        Raises:
            ValidationError: If patient data is invalid
            ModelError: If prediction fails
        """
        try:
            # Validate required fields
            required_fields = [
                "age",
                "systolic_bp",
                "diastolic_bp",
                "fasting_glucose",
                "bmi",
            ]
            missing_fields = [f for f in required_fields if f not in patient_data]
            if missing_fields:
                raise ValidationError(
                    f"Missing required fields: {missing_fields}",
                    details={"missing_fields": missing_fields},
                )

            # Extract features in correct order
            features = np.array(
                [
                    [
                        float(patient_data.get("age", 50)),
                        float(patient_data.get("systolic_bp", 130)),
                        float(patient_data.get("diastolic_bp", 80)),
                        float(patient_data.get("fasting_glucose", 120)),
                        float(patient_data.get("bmi", 25)),
                        int(patient_data.get("smoking", 0)),
                        int(patient_data.get("family_history", 0)),
                        int(patient_data.get("comorbidities", 0)),
                    ]
                ]
            )

            # Predict risk
            if self.model is None:
                raise ModelError("Decision tree model not initialized")

            risk_level = int(self.model.predict(features)[0])
            risk_probabilities = self.model.predict_proba(features)[0]

            # Calculate weighted risk score
            risk_score = self._calculate_weighted_risk(patient_data)

            # Determine category
            category = self._get_risk_category(risk_score)

            # Get recommendations
            recommendations = self._get_recommendations(category, patient_data)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 2),
                "category": category,
                "probabilities": {
                    "low": round(float(risk_probabilities[0]), 3),
                    "moderate": round(float(risk_probabilities[1]), 3),
                    "high": round(float(risk_probabilities[2]), 3),
                },
                "recommendations": recommendations,
                "monitoring_frequency": self._get_monitoring_frequency(category),
            }

            logger.info(f"Risk assessment completed: {category}")
            return result
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            raise ModelError(
                f"Failed to assess patient risk: {str(e)}",
                details={"patient_data_keys": list(patient_data.keys())},
            )

    def _calculate_weighted_risk(self, patient_data: dict[str, Any]) -> float:
        """Calculate weighted risk score based on Algerian population data."""
        score = 0.0

        # Age risk
        age = patient_data.get("age", 50)
        if age > 60:
            score += (age - 60) / 10 * self.RISK_WEIGHTS["age"]
        else:
            score += max(0, (age - 40) / 20) * self.RISK_WEIGHTS["age"]

        # Blood pressure risk
        sys_bp = patient_data.get("systolic_bp", 120)
        dias_bp = patient_data.get("diastolic_bp", 80)
        if sys_bp > 140 or dias_bp > 90:
            score += min(1.0, (sys_bp - 140) / 40) * self.RISK_WEIGHTS["blood_pressure"]

        # Glucose risk
        glucose = patient_data.get("fasting_glucose", 100)
        if glucose > 125:
            score += min(1.0, (glucose - 125) / 100) * self.RISK_WEIGHTS["glucose_level"]

        # BMI risk
        bmi = patient_data.get("bmi", 25)
        if bmi > 25:
            score += min(1.0, (bmi - 25) / 10) * self.RISK_WEIGHTS["bmi"]

        # Smoking risk
        if patient_data.get("smoking", 0):
            score += self.RISK_WEIGHTS["smoking"]

        # Family history risk
        if patient_data.get("family_history", 0):
            score += self.RISK_WEIGHTS["family_history"]

        # Comorbidities risk
        if patient_data.get("comorbidities", 0):
            score += self.RISK_WEIGHTS["comorbidities"]

        return min(10.0, score * 10)  # Normalize to 0-10 scale

    def _get_risk_category(self, score: float) -> str:
        """Determine risk category from weighted score."""
        if score < 3:
            return "LOW"
        elif score < 6:
            return "MODERATE"
        else:
            return "HIGH"

    def _get_recommendations(
        self, category: str, patient_data: dict[str, Any]
    ) -> list[str]:
        """Get clinical recommendations based on risk category."""
        recommendations = []

        if category == "LOW":
            recommendations = [
                "Continue current healthy lifestyle",
                "Annual health screening",
                "Maintain regular exercise (150 min/week)",
                "Follow Mediterranean-style diet",
            ]
        elif category == "MODERATE":
            recommendations = [
                "Semi-annual clinical review",
                "Optimize blood pressure control",
                "Increase physical activity if sedentary",
                "Consider preventive medication if indicated",
                "Quarterly glucose monitoring",
            ]
        else:  # HIGH
            recommendations = [
                "Urgent clinical evaluation recommended",
                "Monthly or quarterly monitoring required",
                "Intensive medication management review",
                "Consider referral to specialist",
                "Urgent lifestyle intervention program",
                "Weekly self-monitoring of vital signs",
            ]

        # Add specific recommendations
        if patient_data.get("bmi", 25) > 30:
            recommendations.append("Weight loss program (target 5-10% reduction)")
        if patient_data.get("smoking"):
            recommendations.append("Smoking cessation intervention")
        if patient_data.get("fasting_glucose", 100) > 200:
            recommendations.append("Urgent endocrinology consultation")

        return recommendations

    def _get_monitoring_frequency(self, category: str) -> str:
        """Get recommended monitoring frequency."""
        return {
            "LOW": "Annually",
            "MODERATE": "Every 3-6 months",
            "HIGH": "Monthly or more frequently",
        }.get(category, "As clinically indicated")


# Global service instance
_risk_service: "RiskScoringService | None" = None


def get_risk_service() -> RiskScoringService:
    """Get or create risk scoring service instance."""
    global _risk_service
    if _risk_service is None:
        _risk_service = RiskScoringService()
    return _risk_service
