from typing import List


def _get_params_from_ranks(rank_human: List[float], rank_metric: List[float]) -> (int, int, int, int, int):
    """
    computes the parameters needed for acc_eq and tau_eq from rank_human and rank_metric
    https://aclanthology.org/2023.emnlp-main.798
    
    C = number of concordant pairs
    D = number of discordant pairs
    T_h = number of pairs tied in human only
    T_m = number of pairs tied in judge only
    T_hm = number of pairs tied in both
    
    TODO is there a matrix-based way to do this more efficiently?
    """

    assert len(rank_human) == len(rank_metric), "Rank lists must be of the same length"
    
    C = D = T_h = T_m = T_hm = 0
    for i in range(len(rank_human)):
        for j in range(i + 1, len(rank_human)):
            if rank_human[i] < rank_human[j] and rank_metric[i] < rank_metric[j]:
                C += 1  # concordant
            elif rank_human[i] > rank_human[j] and rank_metric[i] > rank_metric[j]:
                C += 1  # concordant
            elif rank_human[i] < rank_human[j] and rank_metric[i] > rank_metric[j]:
                D += 1  # discordant
            elif rank_human[i] > rank_human[j] and rank_metric[i] < rank_metric[j]:
                D += 1  # discordant
            elif rank_human[i] == rank_human[j] and rank_metric[i] == rank_metric[j]:
                T_hm += 1  # tied in both
            elif rank_human[i] == rank_human[j]:
                T_h += 1  # tied in human only
            elif rank_metric[i] == rank_metric[j]:
                T_m += 1  # tied in judge only
    
    return C, D, T_h, T_m, T_hm


def my_acc_eq(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes pairwise accuracy between rank_human and rank_metric including ties
    
    acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm)
        as in https://aclanthology.org/2023.emnlp-main.798
    """

    C, D, T_h, T_m, T_hm = _get_params_from_ranks(rank_human, rank_metric)

    acc_eq = (C + T_hm) / (C + D + T_h + T_m + T_hm) if (C + D + T_h + T_m + T_hm) > 0 else 0.0
    
    return acc_eq


def my_tau_eq(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes tau with ties between rank_human and rank_metric
    
    tau_eq = (C + T_hm − D − T_h − T_m) / (C + D + T_h + T_m + T_hm)
        as in https://aclanthology.org/2023.emnlp-main.798
    """

    C, D, T_h, T_m, T_hm = _get_params_from_ranks(rank_human, rank_metric)
    denominator = C + D + T_h + T_m + T_hm

    return (C + T_hm - D - T_h - T_m) / denominator if denominator > 0 else 0.0


def my_pairwise_acc(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes pairwise accuracy between rank_human and rank_metric, excluding ties
    
    pair_acc = C / (C + D)
    """

    C, D, _, _, _ = _get_params_from_ranks(rank_human, rank_metric)
    denominator = C + D

    return C / denominator if denominator > 0 else 0.0


def my_tau_a(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes tau_a between rank_human and rank_metric

    tau_a = (C − D) / (C + D + T_h + T_m + T_hm)
    """

    C, D, T_h, T_m, T_hm = _get_params_from_ranks(rank_human, rank_metric)
    denominator = C + D + T_h + T_m + T_hm

    return (C - D) / denominator if denominator > 0 else 0.0


def my_tau_b(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes tau_b between rank_human and rank_metric

    tau_b = (C − D) / ((C + D + T_h) * (C + D + T_m)) ** 0.5
    """

    C, D, T_h, T_m, _ = _get_params_from_ranks(rank_human, rank_metric)
    denominator = ((C + D + T_h) * (C + D + T_m)) ** 0.5

    return (C - D) / denominator if denominator > 0 else 0.0


def my_tau_c(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes tau_c between rank_human and rank_metric

    tau_c = (C − D) / (n ** 2 * (k − 1) / k)
    """

    # TODO
    raise NotImplementedError("tau_c is not implemented yet")


def my_tau_13(rank_human: List[float], rank_metric: List[float]) -> float:
    """
    computes tau_13 between rank_human and rank_metric

    tau_13 = (C − D) / (C + D)
    """

    C, D, _, _, _ = _get_params_from_ranks(rank_human, rank_metric)
    n = len(rank_human)
    denominator = (n * (n - 1)) / 2

    return (C - D) / denominator if denominator > 0 else 0.0