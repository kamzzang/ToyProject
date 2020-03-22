import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from PyQt5.QtGui import *  # QPixmap 사용

import pandas as pd

# GUI 파일 로드
form_class = uic.loadUiType("mainwindow_scheduler.ui")[0]

cnt = 0

class MainWindow(QMainWindow, form_class):
    # Class 호출 시 초기화 함수
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("OA Scheduler")  # GUI 제목에 버젼표시(동일 UI 파일 사용하기 위함)
        self.setFixedSize(396, 441)  # 메인윈도우 사이즈 고정

        # 버튼 등 시그널 발생에 따른 함수 연결
        self._set_signal_slots()

        # GUI 초기 셋팅을 위한 변수 초기화
        self.weekcheck = True
        self.monthcheck = False

        self.groupBox_weekly.show()  # 매주 설정 그룹 보이게 설정
        self.groupBox_monthly.hide()  # 매월 설정 그풉은 초기에 안보이게 설정

        self.ledit_id.setText("WIPS ID 입력")
        self.ledit_pw.setText("WIPS PW 입력")
        self.cbox_kor.setChecked(True)
        self.ledit_kor.setText("검색어 입력")
        self.cbox_usa.setChecked(True)
        self.ledit_usa.setText("검색어 입력")

        # self.cbox_usa.setEnabled(0)  # 미국 특허 검색 비활성화
        # self.ledit_usa.setEnabled(0)
        self.cbox_eu.setEnabled(0)  # 유럽 특허 검색 비활성화
        self.ledit_eu.setEnabled(0)
        self.cbox_jpn.setEnabled(0)  # 일본 특허 검색 비활성화
        self.ledit_jpn.setEnabled(0)

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    # GUI 아이템(버튼, 라디오 버튼, 체크박스) 시그널 연결 함수
    def _set_signal_slots(self):
        # 버튼 연결
        self.btn_save.clicked.connect(self.save)
        self.rbtn_weekly.clicked.connect(self.weeklyselected)
        self.rbtn_monthly.clicked.connect(self.monthlyselected)

    def save(self):

        if self.tabWidget.currentIndex() == 0:  # 특허검색
            id = self.ledit_id.text()
            pw = self.ledit_pw.text()
            # input = self.ledit_kor.text()
            # print(id, pw, input)

            nation_list = []
            word_list = []
            com_list = []

            if self.cbox_kor.isChecked() == True :
                if self.ledit_kor.text() == "":
                    QMessageBox.warning(self, "경고", "한국 특허 검색어 입력")
                    return
                else:
                    nation_list.append("한국")
                    temp = self.ledit_kor.text().split(',')
                    word_list.append(temp[0])
                    com_list.append(temp[1].replace(' ',''))
            if self.cbox_usa.isChecked() == True:
                if self.ledit_usa.text() == "":
                    QMessageBox.warning(self, "경고", "미국 특허 검색어 입력")
                    return
                else:
                    nation_list.append("미국")
                    temp = self.ledit_usa.text().split(',')
                    word_list.append(temp[0])
                    com_list.append(temp[1].replace(' ',''))
            if self.cbox_eu.isChecked() == True:
                if self.ledit_eu.text() == "":
                    QMessageBox.warning(self, "경고", "유럽 특허 검색어 입력")
                    return
                else:
                    nation_list.append("유럽")
                    temp = self.ledit_eu.text().split(',')
                    word_list.append(temp[0])
                    com_list.append(temp[1].replace(' ',''))
            if self.cbox_jpn.isChecked() == True:
                if self.ledit_jpn.text() == "":
                    QMessageBox.warning(self, "경고", "일본 특허 검색어 입력")
                    return
                else:
                    nation_list.append("일본")
                    temp = self.ledit_jpn.text().split(',')
                    word_list.append(temp[0])
                    com_list.append(temp[1].replace(' ',''))

            data = {'ID' : id,
                    'PW' : pw,
                    'NATION' : nation_list,
                    'WORD' : word_list,
                    'COMPANY' : com_list
                    }
            df_wipsinput = pd.DataFrame(data)
            print(df_wipsinput)
            df_wipsinput.to_csv("WIPS.csv", encoding="euc-kr", index = False)
            # os.startfile("WIPS.csv")

            output = 'schtasks /create /tn "특허검색" /tr "C:\Anaconda3\python.exe D:\Github\ToyProject\PatentSearch\WIPSSearch.py" /sc '
            if self.rbtn_weekly.isChecked() == True:
                output = output + 'weekly /d '
                if self.rbtn_mon.isChecked() == True:
                    output = output + 'MON '
                elif self.rbtn_tue.isChecked() == True:
                    output = output + 'TUE '
                elif self.rbtn_wed.isChecked() == True:
                    output = output + 'WED '
                elif self.rbtn_thu.isChecked() == True:
                    output = output + 'THU '
                elif self.rbtn_fri.isChecked() == True:
                    output = output + 'FRI '

            elif self.rbtn_monthly.isChecked() == True:
                output = output + 'monthly /mo '
                if self.rbtn_first.isChecked() == True:
                    output = output + 'FIRST /d MON '
                elif self.rbtn_last.isChecked() == True:
                    output = output + 'LASTDAY /m * '

            output = output + '/st 09:00:00'  # SYSTEM 계정으로 실행 시 엑서스 에러발생

            print(output)
            os.system('schtasks /delete /tn "특허검색" /f')  # 기존 저장되어 있을 수 있는 스케줄러 삭제(/f는 삭제여부 재확인 없는 설정)
            os.system(output)  # 특허검색 스케줄러 신규 생성

    def weeklyselected(self):
        if self.weekcheck == True:
            self.weekcheck = False
            self.groupBox_weekly.hide()
        else:
            self.weekcheck = True
            self.monthcheck = False
            self.groupBox_weekly.show()
            self.groupBox_monthly.hide()

    def monthlyselected(self):
        if self.monthcheck == True:
            self.monthcheck = False
            self.groupBox_monthly.hide()
        else:
            self.weekcheck = False
            self.monthcheck = True
            self.groupBox_weekly.hide()
            self.groupBox_monthly.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.show()
    app.exec_()