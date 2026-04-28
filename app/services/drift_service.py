"""
Model Drift Detection Service for ChronicCare.
Monitors model performance degradation and triggers retraining.
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pickle

from app.services.adherence_service import get_adherence_service
from app.services.gemini_service import get_gemini_service
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DriftDetectionService:
    """Service for detecting and handling model drift."""

    def __init__(self, drift_threshold: float = 0.05) -> None:
        """
        Initialize drift detection service.

        Args:
            drift_threshold: Threshold for detecting significant drift (0-1)
        """
        self.drift_threshold = drift_threshold
        self.metrics_dir = Path("./metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        self.metrics_file = self.metrics_dir / "model_metrics.pkl"
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> dict[str, Any]:
        """Load historical metrics from disk."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metrics: {str(e)}")
        return {
            "accuracy_history": [],
            "precision_history": [],
            "recall_history": [],
            "last_retraining": datetime.now().isoformat(),
            "drift_detected": False,
        }

    def _save_metrics(self) -> None:
        """Save metrics to disk."""
        try:
            with open(self.metrics_file, "wb") as f:
                pickle.dump(self.metrics, f)
        except Exception as e:
            logger.error(f"Failed to save metrics: {str(e)}")

    async def record_prediction(
        self,
        predicted_risk: str,
        actual_risk: str,
        confidence: float,
    ) -> None:
        """
        Record a prediction for drift detection.

        Args:
            predicted_risk: Model's predicted risk category
            actual_risk: Actual/verified risk category
            confidence: Model's confidence score
        """
        try:
            is_correct = predicted_risk == actual_risk
            timestamp = datetime.now().isoformat()

            if "predictions" not in self.metrics:
                self.metrics["predictions"] = []

            self.metrics["predictions"].append(
                {
                    "timestamp": timestamp,
                    "predicted": predicted_risk,
                    "actual": actual_risk,
                    "correct": is_correct,
                    "confidence": confidence,
                }
            )

            # Keep only last 1000 predictions
            if len(self.metrics["predictions"]) > 1000:
                self.metrics["predictions"] = self.metrics["predictions"][-1000:]

            self._save_metrics()
            logger.info(
                f"Recorded prediction: {predicted_risk} vs {actual_risk} (correct={is_correct})"
            )
        except Exception as e:
            logger.error(f"Failed to record prediction: {str(e)}")

    async def detect_drift(self) -> dict[str, Any]:
        """
        Detect model drift based on recent predictions.

        Returns:
            Drift detection report with metrics and recommendations
        """
        try:
            if "predictions" not in self.metrics or len(self.metrics["predictions"]) < 20:
                return {
                    "drift_detected": False,
                    "reason": "Insufficient predictions for drift detection",
                    "predictions_count": len(self.metrics.get("predictions", [])),
                }

            # Calculate recent accuracy
            recent_preds = self.metrics["predictions"][-100:]
            recent_accuracy = sum(1 for p in recent_preds if p["correct"]) / len(
                recent_preds
            )

            # Get historical accuracy baseline
            if self.metrics["accuracy_history"]:
                baseline_accuracy = sum(self.metrics["accuracy_history"]) / len(
                    self.metrics["accuracy_history"]
                )
            else:
                baseline_accuracy = recent_accuracy

            # Calculate drift
            accuracy_drift = baseline_accuracy - recent_accuracy
            drift_detected = accuracy_drift > self.drift_threshold

            if drift_detected:
                self.metrics["drift_detected"] = True
                logger.warning(
                    f"Model drift detected: {accuracy_drift:.3f} (threshold: {self.drift_threshold})"
                )

            # Analyze by risk category
            category_performance = self._analyze_category_performance(recent_preds)

            report = {
                "drift_detected": drift_detected,
                "accuracy_drift": round(accuracy_drift, 4),
                "recent_accuracy": round(recent_accuracy, 4),
                "baseline_accuracy": round(baseline_accuracy, 4),
                "threshold": self.drift_threshold,
                "predictions_analyzed": len(recent_preds),
                "category_performance": category_performance,
                "recommendation": self._get_drift_recommendation(
                    drift_detected, accuracy_drift
                ),
            }

            # Update history
            self.metrics["accuracy_history"].append(recent_accuracy)
            if len(self.metrics["accuracy_history"]) > 100:
                self.metrics["accuracy_history"] = self.metrics["accuracy_history"][-100:]
            self._save_metrics()

            return report
        except Exception as e:
            logger.error(f"Drift detection failed: {str(e)}")
            return {
                "drift_detected": False,
                "error": str(e),
            }

    def _analyze_category_performance(
        self, predictions: list[dict[str, Any]]
    ) -> dict[str, dict[str, float]]:
        """Analyze performance by risk category."""
        by_category = {}

        for pred in predictions:
            category = pred["predicted"]
            if category not in by_category:
                by_category[category] = {"total": 0, "correct": 0}

            by_category[category]["total"] += 1
            if pred["correct"]:
                by_category[category]["correct"] += 1

        # Calculate accuracy per category
        result = {}
        for category, stats in by_category.items():
            if stats["total"] > 0:
                result[category] = {
                    "accuracy": round(stats["correct"] / stats["total"], 4),
                    "count": stats["total"],
                }

        return result

    def _get_drift_recommendation(self, drift_detected: bool, drift_value: float) -> str:
        """Get recommendation based on drift status."""
        if not drift_detected:
            return "Model performance is stable. Continue monitoring."

        if drift_value < 0.1:
            return "Minor drift detected. Monitor closely and consider retraining if drift increases."
        else:
            return "Significant drift detected. Immediate model retraining recommended."

    async def get_drift_metrics(self) -> dict[str, Any]:
        """Get current drift metrics summary."""
        return {
            "drift_detected": self.metrics.get("drift_detected", False),
            "predictions_recorded": len(self.metrics.get("predictions", [])),
            "accuracy_history_size": len(self.metrics.get("accuracy_history", [])),
            "last_retraining": self.metrics.get("last_retraining"),
            "threshold": self.drift_threshold,
        }

    async def analyze_adherence_proactively(self, patient_id: str) -> dict[str, Any]:
        """
        Detect sharp drops in medication adherence (Clinical Drift).
        If short-term adherence (3 days) is significantly lower than 
        long-term adherence (30 days), trigger a nurture notification.
        """
        try:
            adherence_service = get_adherence_service()
            gemini_service = get_gemini_service()

            # Calculate short-term vs long-term adherence
            long_term = await adherence_service.calculate_adherence(patient_id, days=30)
            short_term = await adherence_service.calculate_adherence(patient_id, days=3)

            # Detect drop
            drop = long_term - short_term
            trigger_notification = drop > 0.3 and short_term < 0.6

            nurture_message = ""
            if trigger_notification:
                logger.warning(f"Sharp adherence drop detected for {patient_id}: {long_term:.2f} -> {short_term:.2f}")
                
                # Generate warm Darija message using Gemini
                nurture_message = await gemini_service.generate_nurture_notification(
                    patient_name="Khalti/Ammi" # General respectful terms
                )
                # Note: Overriding the generic reasoning with a specific nurture prompt if possible, 
                # or I'll just use a dedicated generation method. 
                # Let's add a simpler one for this purpose.

            return {
                "patient_id": patient_id,
                "long_term_adherence": round(long_term, 2),
                "short_term_adherence": round(short_term, 2),
                "adherence_drop": round(drop, 2),
                "trigger_notification": trigger_notification,
                "nurture_message_darija": nurture_message if trigger_notification else None
            }
        except Exception as e:
            logger.error(f"Proactive adherence analysis failed: {str(e)}")
            return {"error": str(e)}


# Global service instance
_drift_service: "DriftDetectionService | None" = None


def get_drift_service() -> DriftDetectionService:
    """Get or create drift detection service instance."""
    global _drift_service
    if _drift_service is None:
        _drift_service = DriftDetectionService()
    return _drift_service
