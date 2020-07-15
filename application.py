# -*- conding: utf-8 -*-
#작성 : 김민찬
from flask import Flask, request, jsonify
import subway_time
app = Flask(__name__)

def user_data_processing(u_data):
    sub_line_list = ['서울', '대구', '부산', '광주', '대전']
    sub_name = ''
    sub_line = ''
    sub_line_tmp = ''
    bar_falg = 0 # '/' 가 없으면 역이름 검색 있으면 시간표 검색
    for i in range(len(u_data)): # 정자역/분당선의 경우 정자역과 분당선을 분리하기위해
        if u_data[i] == '/':
            bar_falg = 1
        elif bar_falg == 0:
            sub_name += u_data[i]
        elif bar_falg == 1:
            sub_line += u_data[i]
        elif i == len(u_data)-1:
            pass
    sub_name = ''.join(sub_name.split())
    sub_line = ''.join(sub_line.split())
    if sub_name[-1] == '역':#맨뒤에 역을 입력한경우 역 삭제 ex) 정자역 -> 정자
        sub_name_len = len(sub_name)
        sub_name = sub_name[0:sub_name_len - 1]
    
    if bar_falg == 0:
        return sub_name , ''
    elif sub_line[0:2] in sub_line_list:
        sub_line_tmp = sub_line[0:2] + ' ' + sub_line[2:]
        return sub_name, sub_line_tmp
    else :
        return sub_name, sub_line
    
def timetable_msg(s_name, s_line):
    
    if s_line != '' :
        if s_line == '명령어':
            u_text = s_name
        else :
            u_text = (subway_time.search_time_table(s_name, s_line))
        u_dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": u_text
                        }
                    }
                ]
            }
        }
    
    elif s_line == '' :
        
        u_notice, u_text = (subway_time.search_line_name(s_name, s_line))
        u_dataSend = {
            "version": "2.0",
            "template": {
                "outputs": [
                  {
                    "simpleText": {
                        "text" : u_notice
                    }
                  }
                ],
                  "quickReplies" : u_text
              }
        }

    return u_dataSend


@app.route('/keyboard')
def keyboard(): #필요없음
    return jsonify({
        'type' : 'buttons',
        'buttons' : '수도권'
       })

@app.route('/message', methods=['POST'])
def Message():
    
    content = request.get_json()
    content = content['userRequest'] #필요한 부분 잘라냄
    content = content['utterance'] #역이름 얻음
    u_sub_name, u_sub_line = user_data_processing(content)
    #print(u_sub_name+'lll', len(u_sub_name),type(u_sub_name))
    if u_sub_name == '명령어':
        help_text = "\"역이름\" 으로 검색\n예 : \"정자역\"\n\"역이름/노선이름\" 으로 검색\n예 : \"정자역/분당선\" "
        dataSend = timetable_msg(help_text, '명령어')
    else :
        dataSend = timetable_msg(u_sub_name, u_sub_line)
    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
    
    
