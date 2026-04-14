# **Factuality-Aware Summarization With NLI Reranking**

## **Assignment:** Final Project Proposal

**Course:** DATASCI 266: Natural Language Processing with Deep Learning (Spring 2026\)  
**Author:** Bjorn Melin  
**Date:** 2/15/2026

We will study factual hallucinations in abstractive summarization and test whether simple decoding-time reranking can reduce factual errors without sacrificing standard overlap metrics. Using XSum as the primary dataset, we will fine-tune a BART summarizer and generate multiple candidate summaries per article via beam search. We will then rerank candidates using factuality signals from (i) a learned factual-consistency classifier (FactCC-style) and (ii) an entailment-based consistency score (SummaC/NLI-style), combining these with the model log-likelihood. Evaluation will report ROUGE-1/2/L and at least one factuality metric (FactCC and/or QAGS), with a trade-off analysis across reranking weights and beam sizes.

The core contribution is analysis: we will build an error taxonomy for hallucinations (entity, number, negation, unsupported relation) and annotate a stratified sample to validate whether metric changes correspond to real factual improvements. Based on the most frequent remaining failures, we will implement one iterative refinement, such as sentence-level entailment aggregation, length normalization, or a simple entity-preservation constraint. The final report will include a Pareto curve (ROUGE vs factuality), ablations on candidate pool size and scoring functions, and qualitative examples highlighting when reranking helps and when it fails.

## **References**

1) Abigail See et al. (dataset context); XSum: Narayan, Cohen, Lapata. 2018\. Don’t Give Me the Details, Just the Summary\! Topic-Aware Convolutional Neural Networks for Extreme Summarization. EMNLP. URL: [https://aclanthology.org/D18-1206/](https://aclanthology.org/D18-1206/)  
2) Lewis et al. 2020\. BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension. ACL. URL: [https://aclanthology.org/2020.acl-main.703/](https://aclanthology.org/2020.acl-main.703/)  
3) Kryscinski et al. 2020\. Evaluating the Factual Consistency of Abstractive Text Summarization. EMNLP. URL: [https://aclanthology.org/2020.emnlp-main.750/](https://aclanthology.org/2020.emnlp-main.750/)  
4) Wang et al. 2020\. Asking and Answering Questions to Evaluate the Factual Consistency of Summaries. ACL. URL: [https://aclanthology.org/2020.acl-main.450/](https://aclanthology.org/2020.acl-main.450/)  
5) Laban et al. 2022\. SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization. TACL. URL: [https://aclanthology.org/2022.tacl-1.10/](https://aclanthology.org/2022.tacl-1.10/)
