# Detection Accuracy Validation Results
Generated: 2025-07-30 19:16:05

## Accuracy Metrics
Overall Accuracy: 87.00%
Average Confidence Score: 0.00

### Class Metrics
| Class | Precision | Recall | F1 Score | Support |
|-------|-----------|--------|----------|--------|
| brute_force_attack | 1.00 | 0.60 | 0.75 | 5 |
| benign | 0.83 | 1.00 | 0.91 | 62 |
| replay_attack | 1.00 | 1.00 | 1.00 | 15 |
| jamming_attack | 1.00 | 0.39 | 0.56 | 18 |

## Performance Metrics
Average Processing Time: 0.06 ms
Minimum Processing Time: 0.00 ms
Maximum Processing Time: 0.77 ms
95th Percentile Processing Time: 0.51 ms
99th Percentile Processing Time: 0.71 ms
Real-time Requirement Met: Yes

## Classification Report
```
                    precision    recall  f1-score   support

            benign       0.83      1.00      0.91        62
brute_force_attack       1.00      0.60      0.75         5
    jamming_attack       1.00      0.39      0.56        18
     replay_attack       1.00      1.00      1.00        15

          accuracy                           0.87       100
         macro avg       0.96      0.75      0.80       100
      weighted avg       0.89      0.87      0.85       100

```
