import pandas as pd
from os import path
import re
import progressbar
import datetime
import numpy as np
import random

class regex_patterns():
    std_tokinaze = [
                (r'[\s+]',r' '),
                (r'(\\n)',r' '),
                (r"([\w/'+$\s-]+|[^\w/'+$\s-]+)\s*",r" \1 "),
                (r"([\*\"\'\\\/\|\{\}\[\]\;\:\<\>\,\.\?\*\(\)])",r" \1 "),
                (' +',r' ')]

def tokinaze_column(df, column_name, patterns):
    '''
    # Tokinaze useless columns df => df
    column_name = 'TEXT'
    patterns = utils.regex_patterns.std_tokinaze
    tokinazed_dataset = utils.tokinaze_column(dataset, column_name,patterns)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    column = df[column_name]
    output_df = df.copy()

    for from_regex, to_regex in bar(patterns):
        column=column.apply(lambda x: re.sub(from_regex, to_regex, x))

    output_df[column_name] = column
    return output_df
