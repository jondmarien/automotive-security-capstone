# Detection Accuracy Validation Results
Generated: 2025-07-30 20:21:00

## Accuracy Metrics
Overall Accuracy: 81.00%
Average Confidence Score: 0.00

### Class Metrics
| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|--------|
| brute_force_attack | 1.00 | 0.86 | 0.92 | 7 |
| signal_cloning_attack | 1.00 | 0.45 | 0.62 | 11 |
| replay_attack | 1.00 | 1.00 | 1.00 | 13 |
| benign | 0.71 | 1.00 | 0.83 | 46 |
| relay_attack | 1.00 | 0.55 | 0.71 | 11 |
| jamming_attack | 1.00 | 0.42 | 0.59 | 12 |

## Performance Metrics
Average Processing Time: 0.02 ms
Minimum Processing Time: 0.00 ms
Maximum Processing Time: 0.52 ms
95th Percentile Processing Time: 0.00 ms
99th Percentile Processing Time: 0.52 ms
Real-time Requirement Met: Yes

## Classification Report
```
                       precision    recall  f1-score   support

               benign       0.71      1.00      0.83        46
   brute_force_attack       1.00      0.86      0.92         7
       jamming_attack       1.00      0.42      0.59        12
         relay_attack       1.00      0.55      0.71        11
        replay_attack       1.00      1.00      1.00        13
signal_cloning_attack       1.00      0.45      0.62        11

             accuracy                           0.81       100
            macro avg       0.95      0.71      0.78       100
         weighted avg       0.87      0.81      0.79       100

```
