# -*- coding: utf-8 -*-

# from datetime import datetime
from collections import defaultdict

from numba import njit, jit
# import pandas as pd
import numpy as np

from .constants import MAPPING_TITLES, MAPPING_SCORES_INDEX


@njit(fastmath=True)
def compute_distance(reference, prediction, distance):
    for char_pred in range(1, len(prediction) + 1):
        for char_ref in range(1, len(reference) + 1):
            delt = 1 if prediction[char_pred - 1] != reference[char_ref - 1] else 0
            distance[char_pred, char_ref] = min(distance[char_pred - 1, char_ref - 1] + delt,
                                                distance[char_pred - 1, char_ref] + 1,
                                                distance[char_pred, char_ref - 1] + 1)

    return distance


@jit(nopython=True, nogil=True)
def check_back_direction(direction, char_ref, char_pred):
    char_pred = char_pred - 1 if direction == "<-" or direction == "\\" else char_pred
    char_ref = char_ref - 1 if direction == "^" or direction == "\\" else char_ref
    return char_ref, char_pred


def show_diff_color_html(reference: str, prediction: str) -> dict:
    """Display source and prediction in HTML format and color-code insertions (blue),
    deletions (red), and exact words (green). based on Levensthein algorithm.

    Example
    --------
    >>> show_diff_color_html("Chat", "Chien")
    ["<span style='color:#3CB371'>C</span>", "<span style='color:#3CB371'>h</span>",
    "<span style='color:#4169E1'>i</span>", "<span style='color:#4169E1'>e</span>",
    "<span style='color:#D2122E'>a</span>", "<span style='color:#4169E1'>n</span>",
    "<span style='color:#D2122E'>t</span>"]

    Args:
        reference (str): reference sequence
        prediction (str): prediction sequence

    Returns:
        list: list of HTML tag with color code
    """
    result = []
    res_r = []
    res_p = []

    distance = np.zeros((len(prediction) + 1, len(reference) + 1), dtype=int)
    distance[0, 1:] = range(1, len(reference) + 1)
    distance[1:, 0] = range(1, len(prediction) + 1)

    distance = compute_distance(reference, prediction, distance)
    # sequences alignment
    # iterate the matrix's values from back to forward
    char_pred = len(prediction)
    char_ref = len(reference)
    counter = 0
    while char_pred > 0 and char_ref > 0:
        counter +=1
        diagonal = distance[char_pred - 1, char_ref - 1]
        upper = distance[char_pred, char_ref - 1]
        left = distance[char_pred - 1, char_ref]

        # check back direction
        direction = "\\" if diagonal <= upper and \
                            diagonal <= left else "<-" \
            if left < diagonal and \
               left <= upper else "^"
        #char_pred = char_pred - 1 if direction == "<-" or direction == "\\" else char_pred
        #char_ref = char_ref - 1 if direction == "^" or direction == "\\" else char_ref
        char_ref, char_pred = check_back_direction(direction, char_ref, char_pred)

        # Colorize characters with HTML tags
        if (direction == "\\"):
            if distance[char_pred + 1, char_ref + 1] == diagonal:
                # exact match
                result.append(f"<span data-id='em-{counter}' class='exact-match line'>{prediction[char_pred]}</span>")
                res_r.append(f"<span id='em-{counter}'>{reference[char_ref]}</span>")
                res_p.append(f"<span id='em-{counter}'>{prediction[char_pred]}</span>")
            elif distance[char_pred + 1, char_ref + 1] > diagonal:
                result.append(f"<span data-id='ref-{counter}' class='delSubts line'>{reference[char_ref]}</span>")
                result.append(f"<span data-id='pred-{counter}' class='insertion line'>{prediction[char_pred]}</span>")
                res_r.append(f"<span id='ref-{counter}'>{reference[char_ref]}</span>")
                res_p.append(f"<span id='pred-{counter}'>{prediction[char_pred]}</span>")
            else:
                result.append(f"<span data-id='pred-{counter}' class='insertion line'>{prediction[char_pred]}</span>")
                result.append(f"<span data-id='ref-{counter}' class='delSubts line'>{reference[char_ref]}</span>")
                res_r.append(f"<span id='ref-{counter}'>{reference[char_ref]}</span>")
                res_p.append(f"<span id='pred-{counter}'>{prediction[char_pred]}</span>")
        elif (direction == "<-"):
            result.append(f"<span data-id='pred-{counter}' class='insertion line'>{prediction[char_pred]}</span>")
            res_p.append(f"<span id='pred-{counter}'>{prediction[char_pred]}</span>")
        elif (direction == "^"):
            result.append(f"<span data-id='ref-{counter}' class='delSubts line'>{reference[char_ref]}</span>")
            res_r.append(f"<span id='ref-{counter}'>{reference[char_ref]}</span>")

    # reverse the list of result
    return {"comparaison": result[::-1], "reference": res_r[::-1], "prediction": res_p[::-1]}


def serialize_scores(board: dict) -> dict:
    """Serialize Kami board in correct format to display in HTML table

    Args:
        board (dict): Kami dict that contains transcription metrics and preprocessing keys

    Returns:
        dict : dict that contain scores and columns
    """
    # set empty value in columns list to represent score legend title in final table
    columns = [""]
    # case with text preprocessing actions
    if "default" in board.keys():
        scores = defaultdict(list)
        for type_preprocess, results in board.items():
            if isinstance(results, dict):
                # convert (from mapping) and add correct preprocessing
                # titles display in final table
                columns.append(MAPPING_TITLES[type_preprocess])
                # convert and add correct metrics titles
                # display in final table
                for type_metric, score in results.items():
                    if type_metric != "wer_hunt":
                        scores[MAPPING_SCORES_INDEX[type_metric]].append(score)
        # final score list eg.
        # [["Levensthein Distance (Char.)", 4, 4, 4, 4], ["Word Error Rate (WER)", 14, 35.54, 46.6, 20], ...]
        scores = [[type_metric]+scores for type_metric, scores in dict(scores).items() if type_metric != "wer_hunt"]
    else:
        columns.append(MAPPING_TITLES["default"])
        scores = [[MAPPING_SCORES_INDEX[type_metric], score] for type_metric, score in board.items() if type_metric != "wer_hunt"]
    return {
        "scores": scores,
        "columns": columns
    }


"""
LEGACY 
def make_dataframe(score_board, reference):
    metadata_keys = ['levensthein_distance_char', 'levensthein_distance_words', 'hamming_distance', 'wer', 'cer',
                     'wacc', 'mer', 'cil', 'cip', 'hits', 'substitutions', 'deletions', 'insertions']
    now = datetime.now()
    metadatas = {}
    metrics = {}
    metadatas["DATETIME"] = now.strftime("%d_%m_%Y_%H:%M:%S")
    metadatas["IMAGE"] = None  # TODO changer quand implémenté
    metadatas["REFERENCE"] = reference
    metadatas["MODEL"] = None  # TODO changer quand implémenté

    for key, value in score_board.items():
        if type(value) != dict and key not in metadata_keys:
            metadatas[key] = value
        else:
            metrics[key] = value
    try:
        df_metrics = pd.DataFrame.from_dict(metrics)
    except:
        df_metrics = pd.DataFrame.from_dict(metrics, orient='index')

    displayable_titles = {0: "Default",
                          "0": "Default",
                          "default": "Default",
                          "non_digits": "Ignoring digits",
                          "lowercase": "Ignoring case",
                          "remove_punctuation": "Ignoring punctuation",
                          "remove_diacritics": "Ignoring diacritics",
                          "all_transforms": "Combining all options"}
    displayable_index = {"cer": "Char. Error Rate (CER)", "wer": "Word Error Rate (WER)",
                         "levensthein_distance_char": "Levensthein Distance (Char.)",
                         "levensthein_distance_words": "Levensthein Distance (Words)",
                         "hamming_distance": "Hamming Distance",
                         "wacc": "Word Accuracy (Wacc)",
                         "mer": "Match Error Rate (MER)",
                         "cil": "Char. Information Lost (CIL)",
                         "cip": "Char. Information Preserved (CIP)",
                         "hits": "Hits",
                         "substitutions": "Substitutions",
                         "deletions": "Deletions",
                         "insertions": "Insertions"}

    df_metrics.rename(columns=displayable_titles, index=displayable_index, inplace=True)

    tables = [df_metrics.to_html(classes=["data", "table", "table-hover", "table-bordered", "table-result-metrics"],
                                 justify='center')]
    titles = [df_metrics.columns.values]
    return tables, titles, metrics
"""
