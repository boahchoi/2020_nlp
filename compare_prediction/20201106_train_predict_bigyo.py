# -*- coding:utf-8 -*-

import os
import json
import sys

#sys.stdout = open('C:/Users/User/Desktop/1016_proto/proto.txt', 'a', encoding='utf-8')
path = 'C:/Users/User/Desktop/1119_poi'

filelist = os.listdir(path)
dev_json = path + '/' + filelist[0]
prediction = path + '/' + filelist[1]

def get_predict_dict(prediction):
    with open(prediction, encoding='utf-8') as f:
        txt = f.readlines()
        predict_dict = {}
        for t in txt:
            if t.find(':') == -1:
                continue
            else:
                txt_idx = t.split(':')[0].strip().replace('"','')
                txt_answer = t.split(':')[1].strip().replace('"','')
                if txt_answer.endswith(','):
                    txt_answer = txt_answer[:-1]
                predict_dict[txt_idx] = txt_answer
    return predict_dict

def get_dev_json_dict(dev_json):
    with open(dev_json, 'r', encoding='utf-8') as f:
        dev_json_dict = {}
        json_load = json.load(f)
        data = json_load['data']

        for data in data:
            paragraph = data['paragraphs']

            for prg in paragraph:
                qas = prg['qas']
#               context는 qas와 동일선상
                context = prg['context']

                for qs in qas:
                    id = qs['id']
                    ans = qs['answers'][0]['text']
                    question = qs['question']
                    filename = qs['filename']
                    dev_json_dict[id] = (ans, question, filename, context)
    return dev_json_dict

if __name__ == '__main__':
    sys.stdout = open('C:/Users/User/Desktop/1119_poi/1119_poi_predict.txt', 'a', encoding='utf-8')
    dev_json_dict = get_dev_json_dict(dev_json)
    predict_dict = get_predict_dict(prediction)
    
    predict_id_list = list(predict_dict.keys())
    dev_json_id_list = list(dev_json_dict.keys())
    
    count_wrong = 0
    count_pre_long = 0
    count_pre_short = 0
    count_right = 0
    for predict_id in predict_id_list:
        if predict_id in dev_json_id_list:
            predict_ans = predict_dict[predict_id]
            dev_ans, dev_question, filename, context = dev_json_dict[predict_id]
            # --- 20.10.12 수정
            #predict와 dev가 아예 다른 경우(부분점수 x)
            if predict_ans.find(dev_ans) == -1 and dev_ans.find(predict_ans)==-1:
                count_wrong += 1
                print('--- 3. pre != dev ---')
                print('predict값 : %s' % predict_ans)
                print('train값 : %s' % dev_ans)
                print('question : %s' % dev_question)
                #print('context : %s' % context)
                print('파일명 : %s' % filename)
                print('\n')                
                
            #predict가 dev보다 answer를 더 넓게 잡는 경우(부분점수o)
            elif len(predict_ans) > len(dev_ans):
                count_pre_long += 1
                print('--- 1. pre > dev ---')
                print('predict값 : %s' % predict_ans)
                print('train값 : %s' % dev_ans)
                print('question : %s' % dev_question)
                #print('context : %s' % context)
                print('파일명 : %s' % filename)
                print('\n')                 


            #predict가 dev보다 answer를 더 작게 잡는 경우(부분점수o)
            elif len(predict_ans) < len(dev_ans):
                count_pre_short += 1
                print('--- 2. pre < dev ---')
                print('predict값 : %s' % predict_ans)
                print('train값 : %s' % dev_ans)
                print('question : %s' % dev_question)
                #print('context : %s' % context)
                print('파일명 : %s' % filename)
                print('\n') 

            else:
                count_right += 1
                print('<<< pre = dev >>>')
                print('predict값 : %s' % predict_ans)
                print('train값 : %s' % dev_ans)
                print('question : %s' % dev_question)
                #print('context : %s' % context)
                print('파일명 : %s' % filename)
                print('\n')

    
    print('='*30)
    print('전체 개수 : %d' % (count_wrong+count_pre_long+count_pre_short+count_right))
    print('전혀 다른 predict값 개수 : %d' % count_wrong)
    print('더 긴 predict값 개수 : %d' % count_pre_long)
    print('짧은 predict값 개수 : %d' % count_pre_short)
    print('정확히 맞은 predict값 개수 : %d' % count_right)

sys.stdout = sys.__stdout__