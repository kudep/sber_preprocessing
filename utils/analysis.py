# coding: utf-8
import pandas as pd
from os import path
import matplotlib.pyplot as plt
import random
from utils.pandas_utils_for_sber_chitchat import tokinazing_column
from utils.pandas_utils_for_sber_chitchat import *
from utils.pipeline_tools import *
# get_ipython().magic('matplotlib inline')
plt.figure()

# #### Statistic


def speaker_set(df,speaker = None):
    if speaker:
        return df[df['SPEAKER']==speaker]
    return df


def get_replies_distibution(df,speaker = None):
    '''
    # Get replies distibution df => series
    speaker = None # CORPORATE, MANAGER
    replies_numbers_chats = analysis.get_replies_distibution(tokinazed_dataset, speaker)
    replies_numbers = pd.Series(replies_numbers_chats.index)

    speaker = 'CORPORATE'
    cor_replies_numbers_chats = analysis.get_replies_distibution(tokinazed_dataset, speaker)
    cor_replies_numbers = pd.Series(cor_replies_numbers_chats.index)

    speaker = 'MANAGER'
    man_replies_numbers_chats = analysis.get_replies_distibution(tokinazed_dataset, speaker)
    man_replies_numbers = pd.Series(man_replies_numbers_chats.index)
    plt.plot(replies_numbers, replies_numbers_chats, 'r',
            cor_replies_numbers, cor_replies_numbers_chats, 'b',
            man_replies_numbers, man_replies_numbers_chats, 'g'
            )
    '''
    chat_column_name = "CHAT_ID"
    df = speaker_set(df,speaker)
    replies_numbers = df[chat_column_name].value_counts().value_counts().sort_index()
    return replies_numbers
