from PyQt5.QtCore import QThread, pyqtSignal


class EvalWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, evaluator):
        super().__init__()
        self.evaluator = evaluator

    def run(self):
        metrics = self.evaluator.run_dataset("Test")
        self.finished.emit(metrics)