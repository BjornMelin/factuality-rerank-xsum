# Report-ready tables

## Main metrics

| split | system | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| val_full | baseline_best_likelihood | 8 | zscore | 0.1483 | 0.0064 | 0.0886 | 0.0886 | 0.7786 | 0.808 | 0.8935 | 0.8267 | 15.875 |
| val_full | best_balanced | 16 | zscore | 0.1698 | 0.0188 | 0.1172 | 0.1172 | 0.9914 | 0.9905 | 0.9906 | 0.9908 | 22.375 |
| val_full | best_factuality | 16 | zscore | 0.1698 | 0.0188 | 0.1172 | 0.1172 | 0.9914 | 0.9905 | 0.9906 | 0.9908 | 22.375 |
| val_full | best_simple | 16 | zscore | 0.1698 | 0.0188 | 0.1172 | 0.1172 | 0.9914 | 0.9905 | 0.9906 | 0.9908 | 22.375 |
| test_final | baseline_best_likelihood | 8 | zscore | 0.1613 | 0.0189 | 0.1242 | 0.1242 | 0.7644 | 0.7841 | 0.9169 | 0.8218 | 16.25 |
| test_final | best_balanced | 16 | zscore | 0.2216 | 0.0262 | 0.1359 | 0.1314 | 0.9894 | 0.9668 | 0.992 | 0.9827 | 26.875 |
| test_final | best_factuality | 16 | zscore | 0.2216 | 0.0262 | 0.1359 | 0.1314 | 0.9894 | 0.9668 | 0.992 | 0.9827 | 26.875 |
| test_final | best_simple | 16 | zscore | 0.2216 | 0.0262 | 0.1359 | 0.1314 | 0.9894 | 0.9668 | 0.992 | 0.9827 | 26.875 |

## Ablation metrics

| system | split | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logprob_only_beam_4 | test_final | 4 | zscore | 0.1613 | 0.0189 | 0.1242 | 0.1242 | 0.7644 | 0.7841 | 0.9169 | 0.8218 | 16.25 |
| logprob_only_beam_8 | test_final | 8 | zscore | 0.1613 | 0.0189 | 0.1242 | 0.1242 | 0.7644 | 0.7841 | 0.9169 | 0.8218 | 16.25 |
| logprob_only_beam_16 | test_final | 16 | zscore | 0.1613 | 0.0189 | 0.1242 | 0.1242 | 0.7644 | 0.7841 | 0.9169 | 0.8218 | 16.25 |
| summac_only | test_final | 8 | zscore | 0.2061 | 0.0263 | 0.1236 | 0.1236 | 0.9786 | 0.9069 | 0.9862 | 0.9573 | 23.0 |
| factcc_only | test_final | 8 | zscore | 0.2061 | 0.0263 | 0.1236 | 0.1236 | 0.9764 | 0.9069 | 0.9862 | 0.9565 | 23.0 |
| logprob_plus_summac | test_final | 8 | zscore | 0.1845 | 0.0272 | 0.1233 | 0.1233 | 0.8531 | 0.8031 | 0.9474 | 0.8679 | 19.625 |
| logprob_plus_factcc | test_final | 8 | zscore | 0.1671 | 0.0189 | 0.1235 | 0.1235 | 0.8256 | 0.8399 | 0.9547 | 0.8734 | 16.75 |
| summac_plus_factcc | test_final | 8 | zscore | 0.2061 | 0.0263 | 0.1236 | 0.1236 | 0.9786 | 0.9069 | 0.9862 | 0.9573 | 23.0 |
| logprob_plus_summac_plus_factcc | test_final | 8 | zscore | 0.1704 | 0.0189 | 0.1211 | 0.1211 | 0.9 | 0.8798 | 0.9762 | 0.9187 | 19.0 |
| logprob_plus_summac_plus_factcc_plus_entity_support | test_final | 8 | zscore | 0.1908 | 0.0277 | 0.1228 | 0.1228 | 0.9199 | 0.8876 | 0.9809 | 0.9295 | 19.875 |

## Audit taxonomy

| primary_error_type | count |
| --- | --- |
| No clear factual issue | 6 |
| Entity swap / wrong named entity / unsupported named entity | 1 |
| Unsupported relation / unsupported event composition / unsupported causal link | 1 |