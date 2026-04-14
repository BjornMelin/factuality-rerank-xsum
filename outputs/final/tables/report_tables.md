# Report-ready tables

## Main metrics

| split | system | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| val_full | baseline_best_likelihood | 8 | zscore | 0.4466 | 0.2168 | 0.3719 | 0.3719 | 0.1917 | 0.3175 | 0.6424 | 0.3839 | 23.9219 |
| val_full | best_balanced | 16 | zscore | 0.4426 | 0.219 | 0.3632 | 0.3632 | 0.2891 | 0.485 | 0.6856 | 0.4866 | 22.7891 |
| val_full | best_factuality | 16 | zscore | 0.4426 | 0.219 | 0.3632 | 0.3632 | 0.2891 | 0.485 | 0.6856 | 0.4866 | 22.7891 |
| val_full | best_simple | 16 | zscore | 0.4431 | 0.2132 | 0.3611 | 0.3611 | 0.2004 | 0.4968 | 0.6812 | 0.4595 | 23.3203 |
| test_final | baseline_best_likelihood | 8 | zscore | 0.4414 | 0.2087 | 0.3592 | 0.3592 | 0.1452 | 0.2376 | 0.6102 | 0.331 | 24.8906 |
| test_final | best_balanced | 16 | zscore | 0.4253 | 0.1942 | 0.3393 | 0.3393 | 0.2567 | 0.403 | 0.6413 | 0.4337 | 24.1797 |
| test_final | best_factuality | 16 | zscore | 0.4253 | 0.1942 | 0.3393 | 0.3393 | 0.2567 | 0.403 | 0.6413 | 0.4337 | 24.1797 |
| test_final | best_simple | 16 | zscore | 0.4343 | 0.2042 | 0.3529 | 0.3529 | 0.1518 | 0.4267 | 0.6352 | 0.4046 | 24.4219 |

## Ablation metrics

| system | split | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logprob_only_beam_4 | test_final | 4 | zscore | 0.4345 | 0.2026 | 0.3512 | 0.3512 | 0.1522 | 0.2159 | 0.5974 | 0.3218 | 25.0703 |
| logprob_only_beam_8 | test_final | 8 | zscore | 0.4414 | 0.2087 | 0.3592 | 0.3592 | 0.1452 | 0.2376 | 0.6102 | 0.331 | 24.8906 |
| logprob_only_beam_16 | test_final | 16 | zscore | 0.4401 | 0.2069 | 0.3571 | 0.3571 | 0.1318 | 0.2251 | 0.6068 | 0.3212 | 24.5469 |
| summac_only | test_final | 8 | zscore | 0.4318 | 0.1987 | 0.348 | 0.348 | 0.2476 | 0.2741 | 0.6297 | 0.3838 | 24.6328 |
| factcc_only | test_final | 8 | zscore | 0.4278 | 0.1971 | 0.3504 | 0.3504 | 0.1619 | 0.3925 | 0.6407 | 0.3984 | 24.9297 |
| logprob_plus_summac | test_final | 8 | zscore | 0.4309 | 0.1994 | 0.3494 | 0.3494 | 0.2369 | 0.2561 | 0.6227 | 0.3719 | 24.7344 |
| logprob_plus_factcc | test_final | 8 | zscore | 0.4347 | 0.2056 | 0.3562 | 0.3562 | 0.1626 | 0.375 | 0.6215 | 0.3863 | 24.8359 |
| summac_plus_factcc | test_final | 8 | zscore | 0.4303 | 0.1962 | 0.3492 | 0.3492 | 0.2318 | 0.3781 | 0.6358 | 0.4152 | 24.8516 |
| logprob_plus_summac_plus_factcc | test_final | 8 | zscore | 0.4316 | 0.2 | 0.3513 | 0.3513 | 0.2278 | 0.3576 | 0.6265 | 0.404 | 24.5859 |
| logprob_plus_summac_plus_factcc_plus_entity_support | test_final | 8 | zscore | 0.4303 | 0.1989 | 0.3496 | 0.3496 | 0.2217 | 0.3691 | 0.6419 | 0.4109 | 24.7031 |

## Audit taxonomy

| primary_error_type | count |
| --- | --- |
| Entity swap / wrong named entity / unsupported named entity | 13 |
| Negation / polarity / stance reversal | 5 |
| Number or date distortion | 5 |
| No clear factual issue | 1 |