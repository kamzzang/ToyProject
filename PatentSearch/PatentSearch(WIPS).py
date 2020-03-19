import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from pandas import Series, DataFrame
from io import BytesIO
from urllib.request import urlopen
import xlsxwriter
import logging

mylogger = logging.getLogger("로깅")
mylogger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s | %(name)s:%(lineno)s]%(asctime)s >> %(message)s')

stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
mylogger.addHandler(stream_hander)

file_handler = logging.FileHandler('WIPS.log')
file_handler.setFormatter(formatter)
mylogger.addHandler(file_handler)

mylogger.info("특허 검색 시작!!!")

# 엑셀 저장
# 엑셀 저장용 별도 함수로 실행
# 엑셀 이름, Data 넘김
def data_to_excel(file_name, Data):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet()

    # worksheet setting
    format = workbook.add_format({'border': 1,
                                  'text_wrap': True,
                                  'valign': 'vcenter',
                                  'align': 'center'})

    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 25)
    worksheet.set_column('F:F', 19)
    worksheet.set_column('G:G', 78)
    worksheet.write(0, 1, '상태', format)
    worksheet.write(0, 2, '출원일', format)
    worksheet.write(0, 3, '출원인', format)
    worksheet.write(0, 4, '대표도면', format)
    worksheet.write(0, 5, '특허 번호', format)
    worksheet.write(0, 6, '특허 제목', format)

    for i in range(0, len(Data)):
        # 순서 저장
        worksheet.write(i + 1, 0, i + 1, format)
        worksheet.write(i + 1, 4, '', format)  # 대표 도면에 이미지 넣고 테두리 포맷 적용이 안되므로 미리 테두리 설정함

        # 특허 상태 저장
        status = Data['Status'][i]
        worksheet.write(i + 1, 1, status, format)

        # 출원일 저장
        date = Data['Date'][i]
        worksheet.write(i + 1, 2, date, format)

        # 출원인 저장
        name = Data['Name'][i]
        worksheet.write(i + 1, 3, name, format)

        # 이미지 저장
        worksheet.set_row(i + 1, 141)
        url = Data['Img_URL'][i]
        if 'https://' in url:  # 특정 대표도면에 주소 오류 에러방지
            image_data = BytesIO(urlopen(url).read())
            worksheet.insert_image('E' + str(i + 2), url,
                                   {'image_data': image_data, 'positioning': 1, 'x_offset': 10, 'y_offset': 10,
                                    'object_position': 1})

        # 특허 번호 저장
        num = Data['Patent_No'][i]
        worksheet.write(i + 1, 5, num, format)

        # 특허 제목 저장
        name = Data['Patent_Title'][i]
        worksheet.write(i + 1, 6, name, format)

    print('엑셀 저장 완료')
    mylogger.info("엑셀 저장 완료")

    workbook.close()


try:
    driver = webdriver.Chrome("chromedriver.exe")
    driver.get("https://www.wipson.com/service/mai/main.wips")

    # WIPS.csv Format : 윕스 아이디, 비번, 검색어, 출원인, 국가로 데이터 정리
    # 윕스 아이디, 비번 설정(WIPS.csv에 저장해놓은 정보 읽음)
    input_data = pd.read_csv('WIPS.csv', encoding="euc-kr")
    id = input_data.ID[0]  # wipson ID"
    pw = input_data.PW[0]  # wipson PW"

    keyword = input_data.WORD.tolist()      # 검색어 설정
    company = input_data.COMPANY.tolist()   # 출원인(회사명) 설정
    nation = input_data.NATION.tolist()     # 특허 국가 설정

    today = datetime.now()

    input_id = driver.find_element_by_id('username') # 로그인 - ID 입력
    input_id.send_keys(id)
    input_pw = driver.find_element_by_id('password') # 로그인 - 비밀번호 입력
    input_pw.send_keys(pw)
    input_pw.send_keys(Keys.RETURN)
    print("로그인 완료")
    mylogger.info("로그인 완료")

    # 이전 로그인 기록에 의해 알람 발생시 알람 처리
    try:
        alert = driver.switch_to_alert()
        alert.accept()  # 경고창 "OK" 버튼 누름 효과
    except Exception as ex:
        print("no alert to accept")

    # 팝업창 처리
    driver.execute_script("document.getElementById('devEventLayerPopup').style.display='none';")

    print("에러처리 완료")
    mylogger.info("에러처리 완료")
    time.sleep(1)

    # 기본 검색 클릭 class="m_detailsearch"
    driver.find_element_by_class_name('m_detailsearch').click()
    print("기본검색 선택 완료")
    mylogger.info("기본검색 선택 완료")

    # 여기서 부터 국가별로 검색
    # 1. nation 리스트에서 국가로 클릭
    # 2. keyword 리스트에서 동일 순서 검색어 입력
    # 3. company 리스트에서 동일 순서 회사면 입력
    # 4. 엑셀 저장 후 다시 1번
    for num in range(len(nation)):

        # 검색 국가 선택
        driver.find_element_by_link_text(nation[num]).click()
        time.sleep(1)

        # 검색 입력창 id="inputText"
        input_search = driver.find_element_by_id('inputText')
        input_search.send_keys(keyword[num])
        input_search = driver.find_element_by_id('AP')
        input_search.send_keys(company[num])
        input_search.send_keys(Keys.RETURN)
        print("검색어 입력 완료")
        mylogger.info("검색어 입력 완료")

        # 블럭형 열거 선택 id="devViewmodeBlockBtnTop"
        time.sleep(0.5)
        driver.find_element_by_id('devViewmodeBlockBtnTop').click()
        print("블럭형 선택 완료")

        time.sleep(1)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        lists = soup.select('li.blocktype')

        status = []
        img_url = []
        date = []
        name = []
        number = []
        title = []
        cnt = 1

        print('Data 저장 시작')
        for data in lists:
            # 상태 받기
            # temp = data.find_all('span', class_='case_type case_fld')
            # for i in temp:
            #     status.append(i.text)
            # if cnt == 1: print("상태", status)

            # 이미지 주소 받기
            img_url.append(data.find('img').get('src'))

            # 출원일 받기
            dates = data.find_all('li', class_='kindinfo_text')
            temp = []
            for i in dates:
                temp.append(i.text.replace('\n', '').replace('\t', ''))
            date.append(temp[1][-10:])
            name.append(temp[3][6:])
            # if cnt == 1: print("출원인", name)

            # 특허 번호 받기
            nums = data.find_all('span')
            temp = []
            for i in nums:
                temp.append(i.text)
                # if cnt == 1: print("특허번호", temp) # 리스트 번호가 매번 바뀌는 거 체크
            number.append(temp[5] + temp[6])
            status.append(temp[3])
            # if cnt == 1: print("특허번호", number)

            # 특허 제목 받기
            tis = data.find_all('a')
            ti = []
            for i in tis:
                ti.append(i.text)
                # if cnt == 1: print("title", ti) # 리스트 번호가 매번 바뀌는 거 체크
            title.append(ti[4])
            # if cnt == 1: print("title", title)
            cnt += 1

        Result = {'Status': status,
                  'Img_URL': img_url,
                  'Date': date,
                  'Name': name,
                  'Patent_No': number,
                  'Patent_Title': title
                  }

        frame = DataFrame(Result)
        print('Data 저장 완료')
        mylogger.info("Data 저장 완료")

        file_name = str(today.year) + '-' + str(today.month) + '-' + str(today.day) + '_' + nation[num] + '.xlsx'
        data_to_excel(file_name, frame)

        print("Finished")

        os.startfile(file_name) # 결과 저장 파일 열기

except Exception as ex:
   print('stop 에러:', ex)
   mylogger.debug(ex)

driver.quit()

mylogger.info("특허 검색 완료")
