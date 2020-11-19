# -*- coding:utf-8 -*-


import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split


count_prototype = 0
count_wrong = 0
path = 'C:/Users/User/Desktop/1103_total'


def count_datarows(train_data_list):
    data_list = []
    qas_list = []
# train data 생성
    for train_data in train_data_list:
        try:
            paragraphs = train_data['paragraphs']
        except Exception as e:
            continue
        
        for paragraph in paragraphs:
            qas = paragraph['qas']
            for qa in qas:
                qas_list.append(qa)
                data_list.append(len(qa['answers'][0]['text']))
    return data_list


def check_to_json(par_num, file_name):
    start_word = 0
    global count_prototype
    global path
    global count_wrong
    try:
        contract_df = pd.read_excel(file_name, keep_default_na=False, index_col=None, header=None, skiprows=2)
        if len(contract_df.columns) > 6:
            contract_df = contract_df.rename(columns={0:'필수조항',1:'체크리스트',2:'idx',3:'question',4:'answer',5:'relationship',6:'context',7:'reference'})
        else:
            count_prototype += 1
            with open(path + '/' + '1103_total.txt','a', encoding = 'utf-8') as f:
                f.write(str(count_prototype) + '\t' + file_name + '\n')
            return False

    except Exception as e :
        return False


    file = file_name.split('/')
    title = file[len(file)-1].replace('.xlsx', '')

    paragraphs_list = []
    qas_list = []
    pre_context = ''
    isfirstrow = True
    context_cnt = 0
    question_cnt = 0

    for index, rows in contract_df.iterrows():
        text = str(rows['answer'])
        # [200901 배수미] context와의 비교를 위해 answer text에도 개행 제거 로직 추가
        text = str(rows['answer']).replace('\n',' ').replace('\r',' ')
        context = rows['context']
        context = context.replace('\n',' ').replace('\r',' ')
        start_word = context.find(text)

        if start_word != -1:
            answer = [{'text':text, 'answer_start':start_word}]
# 오탈자 넘기기
        else:
            with open(path + '/' + '11wrong_answer_list.txt','a', encoding='utf-8') as f:
                count_wrong += 1
                namesplit = file_name.split('/')
                f.write(str(count_wrong) + '\t' + namesplit[len(namesplit)-1] + '\t' + str(rows['idx']) + '\t' + rows['question'] + '\t' + str(rows['answer']) + '\n')
            continue
        
        if isfirstrow:
            pre_context = context
            id_list = [str(par_num), str(context_cnt), str(question_cnt)]
            id = '-'.join(id_list)
            qas = {'id':id, 'question':rows['question'], 'class':rows['체크리스트'], 'answers':answer, 'filename':title}
            qas_list.append(qas)
            if index == len(contract_df)-1:
                paragraphs_list.append({'qas':qas_list, 'context':context})
            isfirstrow = False
            
        else:
            if pre_context != context:
                paragraphs_list.append({'qas':qas_list, 'context':pre_context})
                pre_context = context
                qas_list = []
                context_cnt +=1
                question_cnt = 0
                id_list = [str(par_num), str(context_cnt), str(question_cnt)]
                id = '-'.join(id_list)
                qas = {'id':id,'question':rows['question'], 'class':rows['체크리스트'],'answers':answer, 'filename':title}
                qas_list.append(qas)
            else:
                pre_context = context
                question_cnt += 1
                id_list = [str(par_num), str(context_cnt), str(question_cnt)]
                id = '-'.join(id_list)
                qas = {'id':id,'question':rows['question'], 'class':rows['체크리스트'],'answers':answer, 'filename':title}
                qas_list.append(qas)
                if index == len(contract_df)-1:
                    paragraphs_list.append({'qas':qas_list, 'context':context})


    data = {'paragraphs':paragraphs_list, 'title':title}
    return data


def excel_to_dataset():
    train_data_list = []
    dev_data_list = []
    global path
    file_list = os.listdir(path)


# 데이터 분리
    X_train, X_test = train_test_split(file_list, test_size=0.2,shuffle=True)
    print(len(X_train))
    print(len(X_test))
    data_id_list = []

    for par_num, file in enumerate(X_train+X_test):
        file = file.replace('\\','/')
        data = check_to_json(par_num, path + '/' +file)
        data_id_list.append((par_num, file))

        if par_num < len(X_train):
            train_data_list.append(data)
        else:
            print(par_num)
            dev_data_list.append(data)

    
# [20201018 qa학습데이터 세트 개수 세기]
    data_list = count_datarows(train_data_list)
    print('전체 data개수 : %s개' % len(data_list))
    
    train_set = {'data':train_data_list, 'version':'KorQuAD_v1.0_train'}
    dev_set = {'data':dev_data_list, 'version':'KorQuAD_v1.0_dev'}

    with open(path+'/'+'1104_train.json', 'w', encoding='utf-8') as output_file :
        json.dump(train_set, output_file,ensure_ascii=False)

    with open(path + '/' + '1104_dev.json', 'w', encoding='utf-8') as output_file :
        json.dump(dev_set, output_file,ensure_ascii=False)

    print('success')


if __name__ == "__main__":
    excel_to_dataset()