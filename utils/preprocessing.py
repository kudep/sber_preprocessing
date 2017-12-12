import pandas as pd
from os import path
import re
import progressbar
import datetime
import numpy as np
import random


def get_chats_list(df, column_name):
    '''
    # Get chats list df => [df0,df1,..]
    column_name = 'CHAT_ID'
    chats = get_chats_list(tokinazed_dataset, column_name)
    '''
    bar = progressbar.ProgressBar()
    chat_id_serial = df[column_name].value_counts()[df[column_name].value_counts()>1]
    chats = list()
    for ind in bar(chat_id_serial.index):
        chats.append(df[df[column_name]==ind].copy().reset_index(drop=True))
    return chats


def pauses_insert_in_begin(chats, tag=" <PAUSE> "):
    '''
    # Insert a special tag in dialogue begining  [df0,df1,..] => [df0,df1,..]
    chats = preprocessing.pauses_insert_in_begin(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    for chat in bar(chats):
        select_speaker = 'MANAGER'
        one_df =  chat
        one_row = pd.DataFrame(data=[[None, None, "CORPORATE", tag, None]], columns=one_df.columns.values)
        if one_df['SPEAKER'][0] == select_speaker:
            one_df = pd.concat([one_row, one_df.loc[0:,:]])
        res_chats.append(one_df.reset_index(drop=True))
    return res_chats


def insert_pauses(chats, tag="<PAUSE>"):
    '''
    # Insert a special tag between the replies of the same author [df0,df1,..] => [df0,df1,..]
    chats = preprocessing.insert_pauses(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    for chat in bar(chats):
        select_speaker = 'MANAGER'
        one_df =  chat
        one_row = pd.DataFrame(data=[[None, None, "CORPORATE", tag, None]], columns=one_df.columns.values)
        for ind in one_df.index.values.tolist()[:-1]:
            cur_row =one_df.loc[ind,:]
            next_row =one_df.loc[ind+1,:]
            if (cur_row["SPEAKER"]==select_speaker) and (next_row["SPEAKER"]==select_speaker):
                one_df = pd.concat([one_df.loc[:ind,:], one_row, one_df.loc[ind+1:,:]])
        res_chats.append(one_df.reset_index(drop=True))
    return res_chats

def delete_dublicates(chats,repeate_trash_hold = 5):
    '''
    # Delete a replica dublicates [df0,df1,..] => [df0,df1,..]
    chats = preprocessing.delete_dublicates(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    bad_chats= list()
    for chat in bar(chats):
        setect_speaker = 'MANAGER'
        one_df =  chat
        repeate_count = 0
        for ind in one_df.index.values.tolist()[0:-1]:
            cur_row =one_df.loc[ind,:]
            next_row =one_df.loc[ind+1,:]
            if (cur_row["SPEAKER"]==next_row["SPEAKER"]) and (cur_row["TEXT"]==next_row["TEXT"]):
                repeate_count+=1
                if ind == 0:
                    one_df = pd.concat([one_df.loc[ind+1:,:]])
                else:
                    one_df = pd.concat([one_df.loc[:ind-1,:], one_df.loc[ind+1:,:]])
        if repeate_count < repeate_trash_hold:
            res_chats.append(one_df.reset_index(drop=True))
        else:
            bad_chats.append(one_df.reset_index(drop=True))
    return res_chats


# Concatenate near dialogs by one author

def sentence_concatenate(chats):
    '''
    # Concatenate near dialogs by one author [df0,df1,..] => [df0,df1,..]
    chats = preprocessing.sentence_concatenate(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    for chat in bar(chats):
        prev_speak = ''
        remove_list = list()
        for index, row in chat.iterrows():
            if prev_speak == row['SPEAKER']:
                chat.loc[index,'TEXT'] = chat.loc[index-1,'TEXT'] + ' ' + chat.loc[index,'TEXT']
                remove_list.append(index-1)
            prev_speak = row['SPEAKER']
        chat=chat.drop(chat.index[remove_list]).reset_index(drop=True)
        res_chats.append(chat.reset_index(drop=True))
    return res_chats


# If end dialog is sended by corporate then delete it


def delete_corp_endings(chats):
    '''
    # If end dialog is sended by corporate then delete it [df0,df1,..] => [df0,df1,..]
    chats = preprocessing.delete_corp_endings(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    for chat in bar(chats):
        setect_speaker = 'CORPORATE'
        one_df =  chat
        if one_df['SPEAKER'].values[-1] == setect_speaker:
            one_df = one_df.iloc[:-1,:]
        res_chats.append(one_df)
    return res_chats

def delete_small_chat(chats, count_trashhold=0):
    '''
    # Delete chats with replica numbel less count_trashhold [df0,df1,..] => [df0,df1,..]
    count_trashhold=5
    chats = preprocessing.delete_small_chat(chats, count_trashhold)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    for chat in bar(chats):
        if len(chat)>count_trashhold:
            res_chats.append(chat)
    return res_chats


def add_service_tag(chats):
    '''
    # Add service tag in chats [df0,df1,..] => [df0,df1,..]
    context_chats = preprocessing.add_service_tag(chats)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_chats= list()
    man_start_tag = " <MAN_START> "
    cor_start_tag = " <COR_START> "
    cor_speaker = 'CORPORATE'

    cor_row = pd.DataFrame(data=[[None, None, "CORPORATE", cor_start_tag, None]], columns=chats[0].columns.values)
    man_row = pd.DataFrame(data=[[None, None, "MANAGER", man_start_tag, None]], columns=chats[0].columns.values)
    for chat in bar(chats):
        one_df =  chat
        for ind in one_df.index.values.tolist():
            if (one_df["SPEAKER"][ind]==cor_speaker):
                one_df = pd.concat([one_df.loc[:ind-1,:], cor_row,one_df.loc[ind:,:]])
            else:
                one_df = pd.concat([ one_df.loc[:ind-1,:],man_row, one_df.loc[ind:,:]])
        res_chats.append(one_df.reset_index(drop=True))
    return res_chats




def add_indexing(context_chats,answer_chats,context_len = 140,man_replic_max = 10, drop_begin_man_replic = 0):
    '''
    # Add indexes [df0,df1,..],[df0,df1,..] => [df0,df1,..]
    context_len = 140
    man_replic_max = 2
    chats = preprocessing.add_indexing(context_chats,chats,context_len,man_replic_max)
    '''
    bar = progressbar.ProgressBar()
    bar.init()
    res_answer_chats = list()
    for context_chat, answer_chat in bar(zip(context_chats,answer_chats)):
        context_dial, answer_dial = context_chat,answer_chat[answer_chat['SPEAKER']=='MANAGER']
        lens = context_dial['TEXT'].map(lambda x: len([item for item in x.split() if item])).tolist()
        context_ids = dict()

        for answer_ind, row in answer_dial.iterrows():
            current_context_len = 0
            context_ids[answer_ind]=list()
            drop_begin_man_replic_count = drop_begin_man_replic
            man_replic_count = man_replic_max
            for context_ind in range(answer_ind-1,-1,-1):
                if (context_dial['SPEAKER'][context_ind]=="MANAGER"):
                    if drop_begin_man_replic_count > 0:
                        drop_begin_man_replic_count-=1
                        continue
                    if man_replic_count > 0:
                        man_replic_count-=1
                    else:
                        continue
                prev_len = current_context_len
                current_context_len+=lens[context_ind]
                if (current_context_len <= context_len):
                    context_ids[answer_ind].append(context_ind)
                else:
                    break
        answer_dial = answer_dial.join(pd.DataFrame([0 for i in range(answer_dial.index[-1]+1)],columns =['PADS']))
        answer_dial = answer_dial.join(pd.DataFrame([context_ids.get(i) for i in range(answer_dial.index[-1]+1)],columns =['CONTEXT_IDS']))
        res_answer_chats.append(answer_dial)
    return res_answer_chats

def zipper(context_chats, ans_chats):
    '''
    # Zip chats [df0,df1,..],[df0,df1,..] => [(df0,df0),(df1,df1),..]
    context_chats = context_chats
    ans_chats = man_chats
    chats = preprocessing.zipper(context_chats, ans_chats)
    '''
    return [(con,ans) for con,ans in zip(context_chats,ans_chats)]

def dataset_make(zip_chats, train_file, label_file, pad_enable = True, label_line_len = 140):
    bar = progressbar.ProgressBar()
    bar.init()
    pad_tonken = '<PAD> '
    with open(train_file, 'wt') as train:
        with open(label_file, 'wt') as label:
            for context_chat, answer_chat in bar(zip_chats):
                for _, row in answer_chat.iterrows():
                    text = re.sub(r'\n', ' ', row['TEXT'])
                    text = re.sub(r' +', ' ', text)
                    label_line = ' '.join(text.strip().split()[:label_line_len])
                    train_line = ''
                    if pad_enable:
                        train_line+= pad_tonken*int(row['PADS'])
                    row['CONTEXT_IDS'].sort()
                    for index in row['CONTEXT_IDS']:
                        train_line+= context_chat['TEXT'][index]
                    train_line = re.sub(' +', ' ', train_line)
                    if not len(train_line) or not len(label_line):
                        # print('''
                        # Catch empty line:
                        # train_line: {}
                        # label_line: {}
                        # '''.format(train_line,label_line))
                        continue
                    label.write(label_line + '\n')
                    train.write(train_line + '\n')


def rand_split_list(source, first_portion):
    source_len=len(source)
    targ1_list=list()
    targ2_list=list()
    rand_indexs = random.sample(range(source_len), int(source_len*first_portion))
    for ind,item in enumerate(source):
        if ind in rand_indexs:
            targ1_list.append(item)
        else:
            targ2_list.append(item)
    return targ1_list, targ2_list




def mkvocab(inputfile):
    bar = progressbar.ProgressBar()
    bar.init()
    words = list()
    with open(inputfile) as f:
        for line in bar(f):
            words.extend(line.split())
    return set(words)


def save_vocab(vocab, filename):
    with open(filename, 'wt') as f:
        bar = progressbar.ProgressBar()
        bar.init()
        f.write("<unk>\n")
        f.write("<s>\n")
        f.write("</s>\n")
        for item in bar(vocab):
            f.write("%s\n" % item)

def save_column_text(df, column_name, filename):
    '''
    # Save text of column df => text_file
    column_name = 'TEXT'
    save_column_text(rawdataset, column_name,output_file)
    '''
    with open(filename, 'wt') as f:
        bar = progressbar.ProgressBar()
        bar.init()
        for line in bar(df[column_name]):
            f.write("%s\n" % line)
