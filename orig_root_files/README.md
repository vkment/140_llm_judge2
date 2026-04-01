# llm-judge-wmt-mist-oeg

Starter repository for analyzing agreement between LLM judges and human ratings on the WMT MIST 2025 Open-Ended Generation (OEG) track.

## What this repo currently does

- Loads processed OEG judge data from `oeg_judge_run2_submission_data.csv`.
- Loads processed OEG human data from `oeg_human_eval_data.csv`.
- Aligns judge/human rows to overlapping systems, criteria, and instances.
- Computes:
	- System-level pairwise ranking accuracy (`my_pairwise_acc`).
	- Criterion-grouped correlations (`acc_eq`) using group-by-item scoring.
	- Optional extra criterion metrics (`tau_eq`, `tau_b`) if enabled in code.
- Saves outputs to JSON files.

## OEG criterion mapping

Judge submissions and human files use slightly different criterion naming. The script normalizes judge criteria to human-style names:

- `judge_it` -> `instruction_following`
- `judge_coherence` -> `coherence`
- `judge_natural` -> `naturalness`

## Files

- `judge_human_agreement.py`: main analysis script.
- `judge_utils.py`: contains all of the original prompts used for the judges.
- `corr_utils.py`: correlation and pairwise metrics.
- `oeg_human_eval_raw_data/`: raw human CSV files by locale.
- `oeg_human_eval_data.csv`: flattened processed human data.
- `oeg_judge_run2_submission_data.csv`: flattened processed judge data.

## Quick start

1. Install dependencies:

	 ```bash
	 pip install numpy pandas
	 ```

2. Run analysis from this directory:

	 ```bash
	 python judge_human_agreement.py
	 ```

## Outputs

- `oeg_judge_human_agreement_results.json`
	- Overall system-level ranking accuracy.
	- Criterion-level `acc_eq` slices.
	- Average `acc_eq` across criteria.
	- Criterion-grouped metrics bundle (`acc_eq` by default).

- `oeg_judge_human_agreement_by_criterion.json`
	- Criterion-grouped metrics only (`acc_eq` by default).

## References

- Deutsch et al. (EMNLP 2023): defines meta-evaluation metrics used here (including `acc_eq`, `tau_eq`, etc.).
	- https://aclanthology.org/2023.emnlp-main.798.pdf
- Kocmi et al. (WMT 2025): defines the WMT MIST 2025 data/task setup used for this project.
	- https://aclanthology.org/2025.wmt-1.23.pdf
