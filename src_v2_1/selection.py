"""Validation-only model selection and conservative collapse guard."""
from .compare import paired_delta
class ValidationSelector:
    def __init__(self,baseline_accuracy,baseline_path):
        self.best_accuracy=baseline_accuracy;self.best_path=str(baseline_path);self.best_step=0;self.history=[];self.stop=False
    def consider(self,step,accuracy,abstention_rate,path):
        safe=abstention_rate<=.40
        improved=safe and accuracy>self.best_accuracy
        if improved:self.best_accuracy=accuracy;self.best_step=step;self.best_path=str(path)
        self.stop=not safe
        event=dict(step=step,exact_outcome=accuracy,predicted_abstention_rate=abstention_rate,safe=safe,selected=improved,early_stop=self.stop,best_step=self.best_step,best_accuracy=self.best_accuracy)
        self.history.append(event);return event

def warm_start_gate(before,after):
    delta=paired_delta(before,after)
    accuracy=sum(x['exact_outcome'] for x in after)/len(after)
    return dict(passed=delta['ci95'][0]>0,criterion='Paired semantic-case bootstrap accuracy-change lower 95% bound > 0 versus the v2 15-step SFT validation baseline',accuracy=accuracy,paired_change=delta,exploratory=True,selection_caveat='Four epoch checkpoints were selected on this same validation set; this is an operational gate, not an independent confirmatory significance test.')
