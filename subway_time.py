# -*- conding: utf-8 -*-
#작성 : 김민찬
from bs4 import BeautifulSoup# 패키지 설치
from urllib import parse, request

k_time = "%H%M%S"
k_day = "%a"
h_day = "%m/%d"

u_key_decode = '비공개' #디코딩 해둔 키값

server_issue = '' #메시지에 공지사항 편하게 첨부할라구


def simpletext(send_text):
    send_texts = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": send_text
                            }
                        }
                    ]
                }
            }
    return send_texts

def user_data_processing(u_data):
#사용자가 전달한 메시지를 분석해 역 이름과 노선 이름을 나눔
#/의 유무에 따라 역검색과 시간표 검색을 판단
    sub_line_list = ['서울', '대구', '부산', '광주', '대전', '인천']
    sub_name = ''
    sub_line = ''
    sub_line_tmp = ''
    bar_falg = 0 # '/'가 없으면 역검색, 있으면 시간표 검색
    for i in range(len(u_data)): # 정자역/분당선 의 경우 정자역과 분당선으로 나누기 위해
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
    try :
        if sub_name[-1] == '역':#맨뒤에 역을 입력한경우 역 삭제 ex) 정자역 -> 정자
            sub_name_len = len(sub_name)
            sub_name = sub_name[0:sub_name_len - 1]
    except :
        return '##', '##'
    if bar_falg == 0:#역 이름 검색
        return sub_name , ''
    elif sub_line[0:2] in sub_line_list:#지역별 노선 구분을 위해 사용 ex. 서울 2호선
        sub_line_tmp = sub_line[0:2] + ' ' + sub_line[2:]
        return sub_name, sub_line_tmp
    else :#해당사항 없으면 반환.
        return sub_name, sub_line
    
def timetable_msg(s_name, s_line, KST):
   #어느 국가에 위치한 서버든지 상관없이 한국 표준시로 사용하도록.

    if s_line != '' :
        u_text = search_time_table(s_name, s_line, KST)

        if u_text[:3] == '이미지':
            print(u_text[3:])
            img_u = 'http://13.124.194.183:50852/static/image/migeum_'
            if u_text[3:] == '01':
                img_u+="d.JPG"
                day_t='평일'
            else :
                img_u+="h.JPG"
                day_t='주말 및 공휴일'
            u_dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleImage": {
                                "imageUrl":img_u,
                                "altText": '서버 오류 발생\n죄송합니다.'
                            }
                        },
                        {
                            "simpleText": {
                                "text": '출처:https://www.shinbundang.co.kr/index.jsp?open_main=1&open_sub1=4&open_sub2=1&pageID=%2Fdxline%2Fdxline3_1.jsp&st_cd=SB007'
                            }
                        },
                        {
                            "simpleText": {
                                "text": day_t+'시간표입니다.'+server_issue
                            }
                        }
                    ]
                }
            }

        else:
            u_dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": u_text+server_issue
                            }
                        }
                    ]
                }
            }

    elif s_line == '':

        u_notice, u_text = search_line_name(s_name, s_line, KST)
        if u_notice == '시간표':
            u_dataSend = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": u_text+server_issue
                            }
                        }
                    ]
                }
            }

        else :
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

def day_t(KST):
    # print(KST.strftime(h_day),type(KST.strftime(h_day)))
    h_list = ['09/30', '10/01', '10/02', '10/03', '10/09']
    # print(KST.strftime(h_day)+' '+KST.strftime(k_day)+' '+KST.strftime(k_time))
    if KST.strftime(h_day) in h_list:
        return '03'
    elif KST.strftime(k_day) == 'Sun':
        return '03'
    elif KST.strftime(k_day) == 'Sat':
        return '02'
    else :
        return '01'
    
def sub_name_search(u_key, user_sub_name):#비슷한 역 이름 검색기능 ex) 강남역 서울 2호선 출력(리스트로해서 비슷한거 다뽑아줌)
    search_list = []
    #print(user_sub_name)
    try : 
        url = 'http://openapi.tago.go.kr/openapi/service/SubwayInfoService/getKwrdFndSubwaySttnList'
        queryParams = '?' + parse.urlencode({ parse.quote_plus('ServiceKey') : u_key, parse.quote_plus('subwayStationName') : user_sub_name })
        requ = (url + queryParams)
        response_body = request.urlopen(requ).read()
        soup = (BeautifulSoup(response_body, 'html.parser'))#URL과 파라메터 합쳐서 전달후 정보 읽어옴
        for item in soup.findAll('item'): #내가 필요한 정보 습득
            search_list.append([item.subwaystationname.string, item.subwayroutename.string])
            # print(search_list)
            
    except :
        # print('역이름 오류')
        return []
    #print(user_sub_name, search_list)
    
    return search_list

def sub_code(u_key, user_sub_name, user_line_name):
    short_line = ['경강선', '광주 1호선', '동해선', '대구 1호선']
    try : 
        url = 'http://openapi.tago.go.kr/openapi/service/SubwayInfoService/getKwrdFndSubwaySttnList'
        queryParams = '?' + parse.urlencode({ parse.quote_plus('ServiceKey') : u_key, parse.quote_plus('subwayStationName') : user_sub_name })
        requ = (url + queryParams)
        response_body = request.urlopen(requ).read()
        soup = (BeautifulSoup(response_body, 'html.parser'))#URL과 파라메터 합쳐서 전달후 정보 읽어옴
        for item in soup.findAll('item'): #내가 필요한 정보 습득
            # print(item)
            # print(user_line_name) #** x호선 설정 안한것 찾기 위해
            if item.subwayroutename.string == user_line_name: #사용자가 입력
                s_code = item.subwaystationid.string #역 코드
                s_name = item.subwaystationname.string #역 이름
                break
    except :
        s_code, s_name = sub_code(u_key, user_sub_name, user_line_name)
    if user_line_name in short_line:
        return 'T'+s_code, s_name
    else:
        return s_code, s_name


def sub_time(u_key, subway_code, upDTCode, KST): #지하철 시간표 검색 함수
    lim_t = 0
    day_time = day_t(KST)
    real_time = KST.strftime(k_time)#어느 국가에 위치한 서버든지 상관없이 한국 표준시로 사용하도록.
    time_list = []
    if day_time == '01' :
        if subway_code[0] == 'T' :
            subway_code = subway_code[1:]
            if int(real_time) > 200000 :
                pageNumber = 5
                try_n = 10
        elif int(real_time) > 200000 :
            pageNumber = 14
            try_n = 10
        elif int(real_time) > 150000 :
            pageNumber = 8
            try_n = 13
        else :
            pageNumber = 1
            try_n = 30
    else :
        if subway_code[0] == 'T' :
            subway_code = subway_code[1:]
            if int(real_time) > 200000 :
                pageNumber = 2
                try_n = 10
        elif int(real_time) > 200000 :
            pageNumber = 7
            try_n = 10
        elif int(real_time) > 150000 :
            pageNumber = 5
            try_n = 10
        else :
            pageNumber = 1
            try_n = 30
    
    #23시 59분 이후 시간은 24시로 표기 -> 다음 날짜 걱정 필요 X

    url = 'http://openapi.tago.go.kr/openapi/service/SubwayInfoService/getSubwaySttnAcctoSchdulList'
    
    if upDTCode == 'D':
        time_list.append('하행')
    elif upDTCode == 'U':
        time_list.append('상행')
    
    time_stack = 0
    while time_stack != 5:
        if lim_t > try_n:
            if len(time_list) == 1:
                time_list.append('금일 운행이 모두 종료되었습니다.')
            return time_list
        lim_t += 1
        queryParams = '?' + parse.urlencode({ parse.quote_plus('ServiceKey') : u_key, parse.quote_plus('subwayStationId') : subway_code, parse.quote_plus('dailyTypeCode') : day_time, parse.quote_plus('upDownTypeCode') : upDTCode, parse.quote_plus('pageNo') : pageNumber })
        requ = (url + queryParams)
        response_body = request.urlopen(requ).read()
        soup = (BeautifulSoup(response_body, 'html.parser'))
        if str(soup) == '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><response><header><resultcode>00</resultcode><resultmsg>NORMAL SERVICE.</resultmsg></header><body><items></items><numofrows>10</numofrows><pageno>1</pageno><totalcount>0</totalcount></body></response>':
            return ['인증 코드 오류(UnD, SubCod)']

        for item in soup.findAll('item'):
            if int(item.deptime.string) > int(real_time):
                time_list.append(item.deptime.string[0:2]+'시 '+item.deptime.string[2:4]+'분 '+item.endsubwaystationnm.string+ '행')
                time_stack += 1
                if time_stack==5:
                    break
            if item.endsubwaystationnm.string == item.subwaystationnm.string:
                return [time_list[0], '출발역이 종점입니다.']
        if len(time_list) < 6:
            pageNumber += 1
    return time_list

def subway_timetable(time_l, sub_name):#사용자에게 전송할 타임 테이블, sub_time(...) 에서 구한 시간표를 사용자에게 제공하기 위해 정비
    if time_l[0] == '인증 코드 오류(UnD, SubCod)':
        return '인증 코드 오류(UnD, SubCod)'
    else :
        result_s = ''
        for i in range(len(time_l)):
            if i == len(time_l) - 1:
                result_s += ' '+time_l[i]
            elif time_l[i] == '인증 코드 오류(UnD, SubCod)':
                return '인증 코드 오류(UnD, SubCod)\n'
            elif time_l[i] == '금일 운행이 모두 종료되었습니다.':
                result_s += time_l[i]+'\n\n'
            elif time_l[i] == '상행' or time_l[i] == '하행':
                result_s += '   '+sub_name+'   '+time_l[i]+'\n'+'\n'
            elif time_l[i+1] == '하행':
                result_s += ' '+time_l[i]+'\n'+'\n'
            else:
                result_s += ' '+time_l[i]+'\n'
    
    return result_s

def search_line_name(start_sub_name, start_line_name, KST):
    #if start_line_name == '': #비슷한 역 이름 검색기능 ex) 강남역 서울 2호선 출력(리스트로해서 비슷한거 다뽑아줌)
    user_answer_l = []
    tmp_list = sub_name_search(u_key_decode, start_sub_name)#비슷한 역 이름 검색기능 ex) 강남역 서울 2호선 출력(리스트로해서 비슷한거 다뽑아줌)
    #print('search_line_name runing', tmp_list)
    if tmp_list != []:
        if tmp_list[0][0] == '미금':
            tmp_list.append(['미금','신분당선'])

    if tmp_list == []:
        notice_msg = "올바른 역 이름을 입력 하세요."
        user_answer_l = [{"messageText": "출처","action": "message","label": "출처 보기"},{"messageText": "명령어","action": "message","label": "명령어 보기"},{"messageText": "정자역","action": "message","label": "예시 1번"},{"messageText": "서울","action": "message","label": "예시 2번"},{"messageText": "판교역","action": "message","label": "예시 3번"}]

    elif len(tmp_list) == 1:
        notice_msg = '시간표'
        return notice_msg, search_time_table(tmp_list[0][0], tmp_list[0][1], KST)

    else :
        notice_msg = "지하철 목록입니다."
        for i in range(len(tmp_list)):
            tmp = {
                "messageText": tmp_list[i][0]+'/'+tmp_list[i][1],
                "action": "message",
                "label": tmp_list[i][0]+'/'+tmp_list[i][1]
                }
            #print(tmp)
            user_answer_l.append(tmp)
        
    return notice_msg, user_answer_l

def search_time_table(time_sub_name, time_line_name, KST):
    #print('search_time_table runing')

    user_answer = ''
    result_l = []
    seting_num = 0
    # print(time_sub_name, time_line_name)
    if time_sub_name == '미금' and time_line_name == '신분당선':
        notice_msg = '이미지'+day_t(KST)
        return notice_msg

    if time_line_name == '': #비슷한 역 이름 검색기능 ex) 강남역 서울 2호선 출력(리스트로해서 비슷한거 다뽑아줌)
        return '노선 정보가 누락되었습니다.'

    try:

        subway_code, subway_name = sub_code(u_key_decode, time_sub_name, time_line_name)#사용자가 원하는 지하철역의 코드
        result_l += sub_time(u_key_decode, subway_code, 'U', KST)#사용자가 원하는 지하철 상행 시간표
        result_l += sub_time(u_key_decode, subway_code, 'D', KST)#사용자가 원하는 지하철 하행 시간표

        user_answer = subway_timetable(result_l, subway_name)#사용자에게 전송할 지하철 시간표

    except UnboundLocalError :#역, 선 이름 오류
        return '올바른 역 이름과 선 이름을 입력 하세요.'

    return user_answer

def main_service(u_content, KST):

    u_sub_name, u_sub_line = user_data_processing(u_content)
    #print(u_sub_name+'lll', len(u_sub_name),type(u_sub_name))

    if u_sub_name == '명령어':
        help_text = simpletext("\"역이름\" 으로 검색\n예 : \"정자역\"\n\n\"역이름/노선이름\" 으로 검색\n예 : \"정자역/분당선\"\n\n출처 보기는 \"출처\"로 검색\n예 : \"출처\" ")
        dataSend = help_text
    elif u_sub_name == '출처':
        dataSend = simpletext('모든 정보는 공공데이터 포털의 오픈API인 지하철정보서비스를 사용하였습니다.\n정보 제공 기관 : 국토교통부\n출처 URL : https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15056904')
    else :
        dataSend = timetable_msg(u_sub_name, u_sub_line, KST)

    return dataSend
