# Report-ready tables

## Main metrics

| split | system | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| val_full | baseline_best_likelihood | 8 | zscore | 0.4421 | 0.2126 | 0.3692 | 0.3692 | 0.1968 | 0.3071 | 0.6396 | 0.3812 | 23.8516 |
| val_full | best_balanced | 16 | zscore | 0.4399 | 0.2165 | 0.361 | 0.361 | 0.2928 | 0.4845 | 0.6864 | 0.4879 | 22.9688 |
| val_full | best_factuality | 16 | zscore | 0.4399 | 0.2165 | 0.361 | 0.361 | 0.2928 | 0.4845 | 0.6864 | 0.4879 | 22.9688 |
| val_full | best_simple | 16 | zscore | 0.4382 | 0.2104 | 0.3574 | 0.3574 | 0.1948 | 0.5011 | 0.6866 | 0.4608 | 23.4062 |
| test_final | baseline_best_likelihood | 8 | zscore | 0.4401 | 0.2065 | 0.3569 | 0.3569 | 0.1464 | 0.2438 | 0.6069 | 0.3324 | 24.9688 |
| test_final | best_balanced | 16 | zscore | 0.4263 | 0.1963 | 0.3398 | 0.3398 | 0.2613 | 0.4255 | 0.6391 | 0.442 | 24.1641 |
| test_final | best_factuality | 16 | zscore | 0.4263 | 0.1963 | 0.3398 | 0.3398 | 0.2613 | 0.4255 | 0.6391 | 0.442 | 24.1641 |
| test_final | best_simple | 16 | zscore | 0.4358 | 0.2038 | 0.3523 | 0.3523 | 0.1569 | 0.4488 | 0.6295 | 0.4118 | 24.4219 |

## Ablation metrics

| system | split | beam_size | normalization | rouge1 | rouge2 | rougeL | rougeLsum | summac_style_score | factcc_style_score | entity_support_score | factuality_composite | summary_len_tokens |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| logprob_only_beam_4 | test_final | 4 | zscore | 0.4338 | 0.2031 | 0.3524 | 0.3524 | 0.1474 | 0.2305 | 0.5985 | 0.3255 | 25.1406 |
| logprob_only_beam_8 | test_final | 8 | zscore | 0.4401 | 0.2065 | 0.3569 | 0.3569 | 0.1464 | 0.2438 | 0.6069 | 0.3324 | 24.9688 |
| logprob_only_beam_16 | test_final | 16 | zscore | 0.4414 | 0.2082 | 0.3557 | 0.3557 | 0.1346 | 0.2508 | 0.6041 | 0.3298 | 24.7188 |
| summac_only | test_final | 8 | zscore | 0.4311 | 0.1994 | 0.3478 | 0.3478 | 0.2504 | 0.2791 | 0.6274 | 0.3856 | 24.7578 |
| factcc_only | test_final | 8 | zscore | 0.4292 | 0.194 | 0.3496 | 0.3496 | 0.1597 | 0.3896 | 0.637 | 0.3954 | 24.7578 |
| logprob_plus_summac | test_final | 8 | zscore | 0.4289 | 0.1984 | 0.3464 | 0.3464 | 0.2368 | 0.2597 | 0.6201 | 0.3722 | 24.7031 |
| logprob_plus_factcc | test_final | 8 | zscore | 0.4337 | 0.2031 | 0.3555 | 0.3555 | 0.1617 | 0.3749 | 0.6169 | 0.3845 | 24.7578 |
| summac_plus_factcc | test_final | 8 | zscore | 0.4325 | 0.195 | 0.3486 | 0.3486 | 0.2394 | 0.3753 | 0.6314 | 0.4154 | 24.625 |
| logprob_plus_summac_plus_factcc | test_final | 8 | zscore | 0.4295 | 0.1947 | 0.3488 | 0.3488 | 0.2297 | 0.3635 | 0.6251 | 0.4061 | 24.5 |
| logprob_plus_summac_plus_factcc_plus_entity_support | test_final | 8 | zscore | 0.4304 | 0.1953 | 0.3478 | 0.3478 | 0.2266 | 0.3665 | 0.6387 | 0.4106 | 24.5625 |

## Audit taxonomy

| primary_error_type | count |
| --- | --- |
| Entity swap / wrong named entity / unsupported named entity | 12 |
| Negation / polarity / stance reversal | 6 |
| Number or date distortion | 5 |
| No clear factual issue | 1 |