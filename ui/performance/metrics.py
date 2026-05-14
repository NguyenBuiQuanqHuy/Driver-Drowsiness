from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score
)


class MetricsCalculator:

    def __init__(self, labels):
        self.labels = labels

    def calculate(self, results):

        y_true = [r["ground_truth"] for r in results]
        y_pred = [r["prediction"] for r in results]

        cm = confusion_matrix(
            y_true,
            y_pred,
            labels=self.labels
        )

        report = classification_report(
            y_true,
            y_pred,
            labels=self.labels,
            output_dict=True,
            zero_division=0
        )

        accuracy = accuracy_score(y_true, y_pred)

        precision = precision_score(
            y_true,
            y_pred,
            average='macro',
            zero_division=0
        )

        recall = recall_score(
            y_true,
            y_pred,
            average='macro',
            zero_division=0
        )

        f1 = f1_score(
            y_true,
            y_pred,
            average='macro',
            zero_division=0
        )

        return {
            "confusion_matrix": cm,
            "classification_report": report,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }