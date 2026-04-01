import os
import json
import random
random.seed(0)
from typing import Optional

import numpy as np
import pandas as pd

from corr_utils import my_pairwise_acc, my_acc_eq, my_tau_eq, my_tau_b


# unfortunately human eval and LLM judges used different ways to represent locales
# manually mapping them to each other, thanks to Google Translate for language identification
LOCALE_TO_ID_dict = {
    "ar_EG": 2,
    "bn_BD": 3,
    "cs_CZ": 1,
    "de_DE": 7, 
    "en_US": 0,
    "hi_IN": 9,
    "id_ID": 11,
    "ja_JP": 13,
    "ru_RU": 19,
    "zh_CN": 4,
}
ID_TO_LOCALE_dict = {v: k for k, v in LOCALE_TO_ID_dict.items()}


def parse_score_from_answer(answer: str) -> float:
    """
        Parse a score from the judge's answer string.
    """
    
    # only consider the first line in the response
    answer = answer.strip().split("\n")[0].strip()
    if answer == "FAILED":
        # hard rule, as "FAILED" is a result of force-setting. 
        # This may mean that the server failed or the output could not be parsed after several attempts.
        # We can assign an average score, a random score, or np.nan.
        score = random.randint(1, 7)  # we assign a random score if "FAILED" 
    # elif any(i.isdigit() for i in answer): 
    #     # this no longer happens for run 2.
    #     # if there is a digit, extract the first number as the score. It's guaranteed to find a match.
    #     score = np.float32(re.search(r"[-+]?\d*\.\d+|\d+", answer).group()) # pyright: ignore[reportOptionalMemberAccess]
    else:
        try:
            score = float(answer)
        except ValueError:
            raise ValueError(
                f"Failed to parse judge answer as a numeric score: {answer!r}"
            )

    # Cap the score between 1 and 7, inclusive, which is the allowed range in our rubric.
    score = max(min(score, 7.0), 1.0)
    return score


def gather_oeg_judge_submission_data(output_csv: Optional[str] = None) -> pd.DataFrame:
    """
        Gather all OEG LLM-as-a-judge track submissions into a single pandas dataframe.
        
        Write the dataframe to a csv file if output_csv is not None.
        Return the dataframe.
    """

    # human and LLM judges used different criterion names, so we need to standardise them (to use the human eval names)
    criterion_mapping = {
        "it": "instruction_following",
        "coherence": "coherence",
        "natural": "naturalness",
    }
    
    # list all OEG LLM-as-a-judge track submissions
    filenames = [f for f in os.listdir("../submissions_oeg_judge_run2") if f.endswith(".json")]

    # initialize an empty dict to hold all records
    data = {
        "judge_model_name": [],
        "criterion": [],
        "submission_system_name": [],
        "original_instance_id": [],
        "locale": [],
        "score": [],
    }

    # loop through each file and extract the relevant information to populate the data dict
    for filename in filenames:
        with open(f"../submissions_oeg_judge_run2/{filename}", "r") as f:
            judge_data = json.load(f)
            judge_model_name = filename.split(".json")[0]
            for d in judge_data:
                # e.g. judge_it_#_open_ended_generation_34ff7b0c7d176187b5f56965bc072870_0_#_Gemma-3-27B
                criterion, full_task_id, submission_system_name = d["taskid"].split("_#_")
                criterion = criterion_mapping[criterion.replace("judge_", "")]  # e.g. "judge_it"

                # split the full_task_id to get the original instance id and the locale. note this id format may be different for other tracks
                # e.g. "open_ended_generation_34ff7b0c7d176187b5f56965bc072870_0"
                _, _, _, original_instance_id, language_id = full_task_id.split("_")
                
                locale_id = int(language_id) // 100
                locale = ID_TO_LOCALE_dict[locale_id]
                
                score = parse_score_from_answer(d["answer"])

                # append the extracted information to the data dict using a for loop, since now dict keys are ordered
                for key, value in zip(data.keys(), [judge_model_name, criterion, submission_system_name, original_instance_id, locale, score]):
                    data[key].append(value)

    # convert the data dict to a pandas dataframe
    df_judge_submission = pd.DataFrame(data)

    # save to a csv file 
    if output_csv is not None:
        df_judge_submission.to_csv(output_csv, index=False)

    return df_judge_submission


def gather_oeg_human_eval_data(output_csv: Optional[str] = None) -> pd.DataFrame:
    """
        Gather all OEG human eval data into a single pandas dataframe.
        
        Write the dataframe to a csv file if output_csv is not None.
        Return the dataframe.
    """

    # list all OEG human eval data files
    filenames = [f for f in os.listdir("./oeg_human_eval_raw_data/") if f.endswith(".csv")]

    # initialize an empty dict to hold all records
    data = {
        "judge_model_name": [],
        "criterion": [],
        "submission_system_name": [],
        "original_instance_id": [],
        "locale": [],
        "score": [],
    }

    # loop through each file and extract the relevant information to populate the data dict
    for filename in filenames:
        # sanity check: filename format
        assert filename.startswith("data_"), f"Unexpected filename format: {filename}"
        judge_model_name = "human"  # all files are from human judges
        locale = filename.replace("data_", "").replace(".csv", "")  # e.g. data_ar_EG.csv
        
        # load the csv file into pandas dataframe
        df = pd.read_csv(f"./oeg_human_eval_raw_data/{filename}")
        for _, row in df.iterrows():
            submission_system_name = row["system"]
            original_instance_id = row["doc_id"]
            for criterion in ["coherence", "naturalness", "instruction_following"]:
                score = row[criterion]

                # append the extracted information to the data dict using a for loop, since now dict keys are ordered
                for key, value in zip(data.keys(), [judge_model_name, criterion, submission_system_name, original_instance_id, locale, score]):
                    data[key].append(value)

    # convert the data dict to a pandas dataframe
    df_human_eval = pd.DataFrame(data)

    # save to a csv file 
    if output_csv is not None:
        df_human_eval.to_csv(output_csv, index=False)

    return df_human_eval


def perform_EDA(df_judge_submission: pd.DataFrame, df_human_eval: pd.DataFrame, verbose=True) -> None:
    if verbose:
        import builtins
        print = builtins.print
    else:
        print = lambda *args, **kwargs: None # disable printing, will only run sanity checks
    
    # sanity check: total number of instances in the judge dataframe should be
    # 13 judges * 3 criteria * 10 locales * 46 instances * 16 submission systems = 287040
    assert len(df_judge_submission) == 287040, f"Unexpected number of instances in judge submission data: {len(df_judge_submission)}"
    # sanity check: total number of instances in the human eval dataframe should be
    # 1 judge * 3 criteria * 10 locales * 46 instances * 16 submission systems = 22080
    assert len(df_human_eval) == 22080, f"Unexpected number of instances in human eval data: {len(df_human_eval)}"
    
    # sanity check: number of unique values in each column
    assert df_judge_submission["judge_model_name"].nunique() == 13    
    assert df_human_eval["judge_model_name"].nunique() == 1
    assert df_human_eval["criterion"].nunique() == df_judge_submission["criterion"].nunique() == 3
    assert df_human_eval["submission_system_name"].nunique() == df_judge_submission["submission_system_name"].nunique() == 16
    assert df_human_eval["original_instance_id"].nunique() == df_judge_submission["original_instance_id"].nunique() == 46
    assert df_human_eval["locale"].nunique() == df_judge_submission["locale"].nunique() == 10
        
    print("number of unique judge_model_name:", df_judge_submission["judge_model_name"].nunique())
    print("number of unique criterion:", df_judge_submission["criterion"].nunique())
    print("number of unique submission_system_name:", df_judge_submission["submission_system_name"].nunique())
    print("number of unique original_instance_id:", df_judge_submission["original_instance_id"].nunique())
    print("number of unique locale:", df_judge_submission["locale"].nunique())

    print("score distribution, sorted by mean for most:\n\n", df_judge_submission["score"].describe())
    print("score distribution by judge_model_name:\n", df_judge_submission.groupby("judge_model_name")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by criterion:\n", df_judge_submission.groupby("criterion")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by submission_system_name:\n", df_judge_submission.groupby("submission_system_name")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by original_instance_id:\n", df_judge_submission.groupby("original_instance_id")["score"].describe())
    print("score distribution by locale:\n", df_judge_submission.groupby("locale")["score"].describe().sort_values(by="mean", ascending=False))

    print("number of unique judge_model_name:", df_human_eval["judge_model_name"].nunique())
    print("number of unique criterion:", df_human_eval["criterion"].nunique())
    print("number of unique submission_system_name:", df_human_eval["submission_system_name"].nunique())
    print("number of unique original_instance_id:", df_human_eval["original_instance_id"].nunique())
    print("number of unique locale:", df_human_eval["locale"].nunique())
    
    print("score distribution, sorted by mean for most:\n\n", df_human_eval["score"].describe())
    print("score distribution by judge_model_name:\n", df_human_eval.groupby("judge_model_name")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by criterion:\n", df_human_eval.groupby("criterion")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by submission_system_name:\n", df_human_eval.groupby("submission_system_name")["score"].describe().sort_values(by="mean", ascending=False))
    print("score distribution by original_instance_id:\n", df_human_eval.groupby("original_instance_id")["score"].describe())
    print("score distribution by locale:\n", df_human_eval.groupby("locale")["score"].describe().sort_values(by="mean", ascending=False))


def get_system_level_score(df_human_eval: pd.DataFrame, df_judge_submission: pd.DataFrame, metric_fn) -> dict:
    """
        For each judge_model_name, compute a system-level score between its ranking of submission_system_name
        and the human ranking of submission_system_name, based on their average scores across all instances.
        
        The system-level score is calculated by the `metric_fn` argument.
        
        Return a dict of each judge_model_name to its score.
    """

    # get human ranking of submission_system_name by their average scores, using rank() with the "min" method to account for possible ties
    system_rank_by_human = df_human_eval.groupby("submission_system_name")["score"].mean().rank(method="min", ascending=False)
    system_names_human = system_rank_by_human.index
    rank_human = system_rank_by_human.values
    
    # for each judge_model_name, rank systems in the same way, then compute the `metric_fn` score with human rankings
    judge_model_to_score = {}
    for judge_model_name in df_judge_submission["judge_model_name"].unique():
        df_subset_by_judge = df_judge_submission[(df_judge_submission["judge_model_name"] == judge_model_name)]
        system_rank_by_judge = df_subset_by_judge.groupby("submission_system_name")["score"].mean().rank(method="min", ascending=False)
        system_names_judge = system_rank_by_judge.index
        rank_judge = system_rank_by_judge.values
        
        # sanity check: the system names match between human and judge rankings        
        assert [n1 == n2 for n1, n2 in zip(system_names_judge, system_names_human)] and len(system_names_judge) == len(system_names_human)

        score = metric_fn(rank_human, rank_judge)
        judge_model_to_score[judge_model_name] = score

    return judge_model_to_score


def get_score_by_criterion(df_human_eval: pd.DataFrame, df_judge_submission: pd.DataFrame, metric_fn) -> dict:
    """
        For each criterion, compute the instance-level score between each judge_model_name and human, using the group-by-item method.

        The instance-level score is calculated by the `metric_fn` argument.

        Return a dict of criterion to another dict of judge_model_name to score.
    """
    criterion_to_judge_model_to_score = {}
    for criterion in df_judge_submission["criterion"].unique():
        # get the subset of data for this criterion
        df_judge_criterion = df_judge_submission[df_judge_submission["criterion"] == criterion]
        df_human_criterion = df_human_eval[df_human_eval["criterion"] == criterion]
        
        # determine the unique instances from human eval data using original_instance_id_with_locale
        unique_instances = set(df_judge_criterion["original_instance_id_with_locale"])
        # sanity check: the unique instances should match between judge and human data after filtering
        assert unique_instances == set(df_human_criterion["original_instance_id_with_locale"]), "The unique instances between judge and human data do not match after filtering."

        # for each judge_model_name, compute the average pairwise accuracy with ties across all unique instances
        judge_model_to_score = {}
        for judge_model_name in df_judge_criterion["judge_model_name"].unique():
            instance_scores = []
            for instance in unique_instances:
                # get the same set of instances from all submission systems for both judge and human rankings
                df_judge_instance = df_judge_criterion[(df_judge_criterion["judge_model_name"] == judge_model_name) & (df_judge_criterion["original_instance_id_with_locale"] == instance)]
                df_human_instance = df_human_criterion[df_human_criterion["original_instance_id_with_locale"] == instance]
                
                # sanity check: the two dataframes should have the same submission_system_name values
                systems_judge = set(df_judge_instance["submission_system_name"].unique())
                systems_human = set(df_human_instance["submission_system_name"].unique())
                assert systems_judge == systems_human, f"Different systems between judge and human for instance {instance} and judge_model_name {judge_model_name}"
                
                # sort by system name to ensure the system order is the same, so later the scores are aligned
                df_judge_instance = df_judge_instance.sort_values(by="submission_system_name")
                df_human_instance = df_human_instance.sort_values(by="submission_system_name")

                # get submission systems' scores by judge and human
                scores_judge = df_judge_instance["score"].values
                scores_human = df_human_instance["score"].values
                
                # compute the instance-level score using the provided `metric_fn` argument
                # ;) actually, using scores, negative scores, or ranks are all equivalent for computing pariwise accuracy or tau (with ties)
                score = metric_fn(scores_human, scores_judge)
                instance_scores.append(score)

            # average scores across all instances for this judge_model_name and criterion
            avg_score = np.mean(instance_scores)
            judge_model_to_score[judge_model_name] = avg_score

        criterion_to_judge_model_to_score[criterion] = judge_model_to_score

    return criterion_to_judge_model_to_score


def get_criterion_grouped_scores(
    df_human_eval: pd.DataFrame,
    df_judge_submission: pd.DataFrame,
    include_additional_metrics: bool = False,
) -> dict:
    """
        Compute criterion-grouped judge-human correlations for multiple metrics.

        Return a dict with metric names as keys and criterion->judge_model_name->score
        as values.
    """
    metric_name_to_fn = {
        "acc_eq": my_acc_eq,
    }
    if include_additional_metrics:
        metric_name_to_fn.update(
            {
                "tau_eq": my_tau_eq,
                "tau_b": my_tau_b,
            }
        )

    grouped_scores = {}
    for metric_name, metric_fn in metric_name_to_fn.items():
        grouped_scores[metric_name] = get_score_by_criterion(
            df_human_eval=df_human_eval,
            df_judge_submission=df_judge_submission,
            metric_fn=metric_fn,
        )

    return grouped_scores


if __name__ == "__main__":

    # get the judge submission data
    judge_submission_csv = "oeg_judge_run2_submission_data.csv"
    if os.path.exists(judge_submission_csv):
        print(f"{judge_submission_csv} exists. Loading data directly...")
        df_judge_submission = pd.read_csv(judge_submission_csv)
    else:
        print(f"{judge_submission_csv} does not exist. Processing data from scratch...")
        df_judge_submission = gather_oeg_judge_submission_data(output_csv=judge_submission_csv)

    # get the human eval data
    human_eval_csv = "oeg_human_eval_data.csv"
    if os.path.exists(human_eval_csv):
        print(f"{human_eval_csv} exists. Loading data directly...")
        df_human_eval = pd.read_csv(human_eval_csv)
    else:
        print(f"{human_eval_csv} does not exist. Processing data from scratch...")
        df_human_eval = gather_oeg_human_eval_data(output_csv=human_eval_csv)

    ### 0. important step: filter the two dataframes to have the same (sub)set of instances ###
    # make a new column that combines original_instance_id and locale to define a unique instance
    df_judge_submission["original_instance_id_with_locale"] = df_judge_submission["original_instance_id"] + "_with_" + df_judge_submission["locale"]
    df_human_eval["original_instance_id_with_locale"] = df_human_eval["original_instance_id"] + "_with_" + df_human_eval["locale"]

    # remove extra (non-overlapping) instances by submission_system_name, criterion, or original_instance_id_with_locale in either dataframe
    # this ensures that all correlations are computed on the same set of instances
    for filter_key in ["submission_system_name", "criterion", "original_instance_id_with_locale"]:
        judge_keys = set(df_judge_submission[filter_key].unique())
        human_keys = set(df_human_eval[filter_key].unique())
        df_judge_submission = df_judge_submission[df_judge_submission[filter_key].isin(human_keys)]
        df_human_eval = df_human_eval[df_human_eval[filter_key].isin(judge_keys)]

    # perform some EDA on the filtered dataframes
    perform_EDA(df_judge_submission, df_human_eval, verbose=False)
    print()

    ### 1. pairwise accuracy excluding ties, between each judge_model_name and human rankings ###
    judge_model_to_pairwise_acc = get_system_level_score(df_human_eval, df_judge_submission, metric_fn=my_pairwise_acc)
    print("Pairwise ranking accuracy between each judge_model_name and human rankings:")
    for judge_model_name, acc in sorted(judge_model_to_pairwise_acc.items(), key=lambda x: x[1], reverse=True):
        print(f"{judge_model_name}: {acc:.4f}")
    print()


    ### 2. for each criterion, compute criterion-grouped correlations (OEG criteria after mapping) ###
    criterion_grouped_scores = get_criterion_grouped_scores(
        df_human_eval,
        df_judge_submission,
        include_additional_metrics=False,
    )
    criterion_to_judge_model_to_acc_eq = criterion_grouped_scores["acc_eq"]
    print("Average pairwise accuracy with ties between each judge_model_name and human rankings:")
    for criterion, judge_model_to_acc_eq in criterion_to_judge_model_to_acc_eq.items():
        print(f"Criterion - {criterion}")
        for judge_model_name, acc_eq in sorted(judge_model_to_acc_eq.items(), key=lambda x: x[1], reverse=True):
            print(f"{judge_model_name}: {acc_eq:.4f}")
        print()


    ## 3. save the results to a json file ###
    results = {"ranking_accuracy": judge_model_to_pairwise_acc}
    
    acc_eq_overall = {}
    for criterion, judge_model_to_acc_eq in criterion_to_judge_model_to_acc_eq.items():
        results[f"acc_eq_by_{criterion}"] = judge_model_to_acc_eq

        for judge_model_name, acc_eq in judge_model_to_acc_eq.items():
            if judge_model_name not in acc_eq_overall:
                acc_eq_overall[judge_model_name] = []
            acc_eq_overall[judge_model_name].append(acc_eq)
    average_acc_eq_overall = {judge_model_name: np.mean(acc_eq_list) for judge_model_name, acc_eq_list in acc_eq_overall.items()}

    results["acc_eq_average"] = average_acc_eq_overall
    results["criterion_grouped_scores"] = criterion_grouped_scores

    with open("./oeg_judge_human_agreement_results.json", "w") as f:
        json.dump(results, f, indent=4)

    with open("./oeg_judge_human_agreement_by_criterion.json", "w") as f:
        json.dump({"criterion_grouped_scores": criterion_grouped_scores}, f, indent=4)
