# -*- coding: utf-8 -*-

MAPPING_TITLES = {"default": "Default",
                  "non_digits": "Ignoring digits",
                  "lowercase": "Ignoring case",
                  "remove_punctuation": "Ignoring punctuation",
                  "remove_diacritics": "Ignoring diacritics",
                  "all_transforms": "Combining all options"}

MAPPING_SCORES_INDEX = {"cer": "Char. Error Rate (CER in %)",
                        "wer": "Word Error Rate (WER in %)",
                        "levensthein_distance_char": "Levensthein Distance (Char.)",
                        "levensthein_distance_words": "Levensthein Distance (Words)",
                        "hamming_distance": "Hamming Distance",
                        "wacc": "Word Accuracy (Wacc in %)",
                        "mer": "Match Error Rate (MER in %)",
                        "cil": "Char. Information Lost (CIL in %)",
                        "cip": "Char. Information Preserved (CIP in %)",
                        "hits": "Hits",
                        "substitutions": "Substitutions",
                        "deletions": "Deletions",
                        "insertions": "Insertions"}
