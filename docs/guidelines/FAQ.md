# Frequently Asked Questions

## Use whatever tooling you want

Office hours asked: use tools you didn’t write? Yes. You must understand what tool, why it fits problem, coherent reason to apply. Cite tool in report -- what work you leveraged vs what you contributed.

## Target instructors as your audience

Page limit is tight -- use space well. Audience = instructors. Don’t re-explain lecture material. Assume solid grasp of common language + neural models. Spend words on your contributions and how they differ from published work.

## Keep your report focused

1-2 models (+ baseline). Know them deeply; show it. Prefer algorithm detail + motivation over “which package.” Don’t pad with unmotivated algorithm lists -- references + empirical results on your data, or omit. Graders shouldn’t yell “Bingo\!” after a paragraph. They should see you know the data, where baseline fails, coherent fixes.

## Literature review is required

Work should connect to published literature. What shaped direction? Cite it. Claim “approach X doesn’t work” → substantiate with references. Citing “X fails” to skip solved problems is fine -- not cheating. References must:

* Related to project; published, peer-reviewed sources.  
* Not prior course project reports; not Stanford CS224N/CS224D reports.  
* Not GitHub or blog posts as “the literature.”  
* Not blog posts (repeat: not blog posts).  
* (For honesty: still cite reports, GitHub, blogs when used -- they don’t replace peer-reviewed motivation for approach/claims.)

## Analysis is critical

Explain errors through your model -- use the understanding you built. One model + strong error analysis beats many algorithms with no idea why things work or fail.

## Data selection

Like any ML project, data choice matters. You may use datasets you can access if sampling, volume, methodology fit goals. Instructors may need to inspect data without signing NDA -- no private proprietary data.

## Concrete example

(Not real sentences.) Say project = classification:

* Example (bad): “We stored our data in /foo/bar.csv. Next we processed the data with scikit\_learn.TFIDFVectorizer and perplexity is 38.02.”  
* Example (good): “Because Hinton \[1\] and Bengio \[2\] found bag-of-vectors works on our task, we used that baseline. Many errors looked like sentences heavy on stop words; we hypothesize they swamped average embedding. (e.g. …) We weighted terms by TF-IDF not plain TF -- hypothesis: better on those errors by down-weighting stopwords, up-weighting semantic terms. Accuracy 89%, +2 pp vs Hinton. Nearly all prior errors fixed; one left: \[The Who\] is a band but embedding looks like two stopwords’ mean. (… discuss casing, NER first, Word2Vec-style tricks …)”

Bad example problems:

* We don’t care where/format you store data -- care that you looked at data and it fits problem.  
* Sounds random tool use (TFIDFVectorizer) without motivation -- motivate choices.  
* Perplexity often wrong metric here -- skim field papers for standard metrics; if you insist on different metric, justify (OH OK).  
* Final number matters less than trust you understand + apply to real problems. Data scientist who skips looking at data is weak. (Look at data. Bonus: study wrong predictions + hypotheses why.)

Good example strengths:

* Claim + approach backed by peer-reviewed cites  
* Close to data (inspect losses)  
* Lit + observations drive method  
* Concrete plan (BoV, TF vs IDF, why averaging improves)  
* Empirical results  
