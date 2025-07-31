# Detection Accuracy Validation Results
Generated: 2025-07-30 19:08:40

## Accuracy Metrics
Overall Accuracy: 94.00%
Average Confidence Score: 0.00

### Class Metrics
| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|--------|
| replay_attack | 1.00 | 1.00 | 1.00 | 16 |
| jamming_attack | 1.00 | 0.67 | 0.80 | 9 |
| brute_force_attack | 1.00 | 0.62 | 0.77 | 8 |
| benign | 0.92 | 1.00 | 0.96 | 67 |

## Performance Metrics
Average Processing Time: 0.03 ms
Minimum Processing Time: 0.00 ms
Maximum Processing Time: 0.68 ms
95th Percentile Processing Time: 0.02 ms
99th Percentile Processing Time: 0.52 ms
Real-time Requirement Met: Yes

## Classification Report
```
                    precision    recall  f1-score   support

            benign       0.92      1.00      0.96        67
brute_force_attack       1.00      0.62      0.77         8
    jamming_attack       1.00      0.67      0.80         9
     replay_attack       1.00      1.00      1.00        16

          accuracy                           0.94       100
         macro avg       0.98      0.82      0.88       100
      weighted avg       0.94      0.94      0.93       100

```
