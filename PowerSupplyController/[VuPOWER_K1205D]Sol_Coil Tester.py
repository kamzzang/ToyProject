# VuPOWER K1205D
# DataSheet : http://www.vupower.com/site_file/1516356352K.pdf
# Manual : http://www.vupower.com/download/K_USB_Manual_Korea_Ver3.2.pdf
# Demo & USB Driver Download : http://www.vupower.com/sub.php?page=demo.php

# VuPOWER K1205D를 이용한 각종 시험용 컨트롤러로
# 기본적으로 솔레노이드 코일 작동 시험을 위한 모드로 구성함

import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import serial
from tkinter import filedialog, Tk
import pandas as pd
from pandas import DataFrame

# GUI 파일 로드
form_class = uic.loadUiType("MainWindow.ui")[0]

# 파일 컨트롤 시 Tkinter 창이 뜨는 현상 방지
root = Tk()
root.withdraw()

print("SOL_COIL TESTER")
print("Copyright 2019. KAMZZANG")

class MyWindow(QMainWindow, form_class):
    # Class 호출 시 초기화 함수
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("SOL COIL TESTER")  # 제목표시
        self.setFixedSize(554, 697)  # 메인윈도우 사이즈 고정

        # 버튼 등 시그널 발생에 따른 함수 연결
        self._set_signal_slots()

        # GUI 초기 셋팅을 위한 변수 초기화
        self.comport = "COM1"  # 시리얼 통신 포트 초기화
        self.main_power = False  # 메인 통신 개시 OFF
        self.p1check = False  # P1 채널 선택
        self.p2check = False  # P2 채널 선택
        self.p1p2check = False  # P1 / P2 동시제어 선택(P1 기준으로 동일 작동)
        self.p1vcheck = True  # P1 정전압제어 선택(초기 선택)
        self.p1ccheck = False  # P1 정전류제어 선택
        self.p1conticheck = True  # P1 연속작동 선택(초기 선택)
        self.p1onoffcheck = False  # P1 On Off 반복작동 선택
        self.p2vcheck = True  # P2 정전압제어 선택(초기 선택)
        self.p2ccheck = False  # P2 정전류제어 선택
        self.p2conticheck = True  # P2 연속작동 선택(초기 선택)
        self.p2onoffcheck = False  # P2 On Off 반복작동 선택
        self.p1save = True  # P1 저장 확인(초기에 두 채널 모두 저장이 되었다는 True를 해야 한 채널만 시험시도 자장 후 바로 시험 시작 가능)
        self.p2save = True  # P2 저장 확인
        self.p1_testtime = 0  # P1 시험 시간 초기화
        self.p2_testtime = 0  # P2 시험 시간 초기화
        self.p1_teststatus = False  # P1 시험 상태
        self.p2_teststatus = False  # P2 시험 상태

        # 타이머 셋팅
        self.p1_timer1 = QTimer(self)  # P1 연속작동 타이머
        self.p1_timer1.timeout.connect(self.p1_timeout_conti)  # P1 연속작동 타이머 함수 연결
        self.p1_timer2 = QTimer(self)  # P1 On Off 작동 타이머
        self.p1_timer2.timeout.connect(self.p1_timeout_onoff)  # P1 On Off 작동 타이머 함수 연결
        self.p1_timer3 = QTimer(self)  # P1 패턴 작동 타이머
        self.p1_timer3.timeout.connect(self.p1_timeout_file)  # P1 패턴 작동 타이머 함수 연결
        self.p2_timer1 = QTimer(self)  # P2 연속작동 타이머
        self.p2_timer1.timeout.connect(self.p2_timeout_conti)  # P2 연속작동 타이머 함수 연결
        self.p2_timer2 = QTimer(self)  # P2 On Off 타이머
        self.p2_timer2.timeout.connect(self.p2_timeout_onoff)  # P2 On Off 타이머 함수 연결
        self.p2_timer3 = QTimer(self)  # P2 패턴 작동 타이머
        self.p2_timer3.timeout.connect(self.p2_timeout_file)  # P2 패턴 작동 타이머 함수 연결

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # 시험 진행 경과 확인용 Progress Bar
        self.progressBar.setValue(0)

        # 각 채널 전압/전류 표시 라벨 0로 초기 셋팅
        self.lb_p1_volt.setText("0")  # P1 전압 라벨
        self.lb_p1_current.setText("0")  # P1 전류 라벨
        self.lb_p2_volt.setText("0")  # P2 전압 라벨
        self.lb_p2_current.setText("0")  # P2 전류 라벨

        # 초기 버튼 비활성화
        self.btn_p1_save.setEnabled(0)  # P1 Save 버튼
        self.btn_p2_save.setEnabled(0)  # P2 Save 버튼
        self.btn_start.setEnabled(0)  # Start 버튼
        self.btn_stop.setEnabled(0)  # Stop 버튼
        self.btn_resultsave.setEnabled(0)  # Result save 버튼

        # 초기 체크박스 비활성화
        self.cbox_p1.setEnabled(0)  # P1 선택 체크박스
        self.cbox_p2.setEnabled(0)  # P2 선택 체크박스
        self.cbox_p1p2.setEnabled(0)  # P1/P2 동시제어 선택 체크박스

        # 초기 시험 모드/패턴 입력 비활성화
        self.p1_input_activate(0)  # P1 입력 항목 전체 활성화 함수
        self.p2_input_activate(0)  # P2 입력 항목 전체 활성화 함수

    # GUI 아이템(버튼, 라디오 버튼, 체크박스) 시그널 연결 함수
    def _set_signal_slots(self):

        # 메인 버튼 연결
        self.btn_main_onoff.clicked.connect(self.mainpower)

        # 테스트 모드 저장 버튼 연결
        self.btn_p1_save.clicked.connect(self.p1modesave)
        self.btn_p2_save.clicked.connect(self.p2modesave)

        # 결과 저장 버튼 연결
        self.btn_resultsave.clicked.connect(self.resultsave)

        # 테스트 제어 버튼 연결
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)

        # 테스트 체널 선택 체크박스 연결
        self.cbox_p1.clicked.connect(self.p1selected)
        self.cbox_p2.clicked.connect(self.p2selected)
        self.cbox_p1p2.clicked.connect(self.p1p2selected)

        # 테스트 모드/패턴 선택 라디오버튼 연결
        self.rbtn_p1_volt.clicked.connect(self.p1vselected)
        self.rbtn_p1_current.clicked.connect(self.p1cselected)
        self.rbtn_p1_conti.clicked.connect(self.p1contiselected)
        self.rbtn_p1_onoff.clicked.connect(self.p1onoffselected)
        self.rbtn_p1_fileload.clicked.connect(self.p1fileloadselected)
        self.rbtn_p2_volt.clicked.connect(self.p2vselected)
        self.rbtn_p2_current.clicked.connect(self.p2cselected)
        self.rbtn_p2_conti.clicked.connect(self.p2contiselected)
        self.rbtn_p2_onoff.clicked.connect(self.p2onoffselected)
        self.rbtn_p2_fileload.clicked.connect(self.p2fileloadselected)

    # 메인 전원 역할 버튼 함수
    def mainpower(self):
        try:
            if self.main_power == False:  # 메인 파워 ON 시키는 조건(OFF상태에서 ON으로 전환되므로)
                # 메인 파워 변수 True로 변경
                self.main_power = True

                # 사용자가 체크박스에서 선택한 COM PORT읽음
                self.comport = self.cBox_comport.currentText()

                # 시리얼 포트 통신 연결
                self.comm = serial.Serial(
                    port=self.comport,
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1)

                # VUPOWER와 정상적인 연결이 되었는지 확인
                msg = "*IDN?\n"
                self.comm.write(msg.encode('utf-8'))
                ans = self.comm.readline().decode('utf-8').split(',')

                if ans[0] == "VUPOWER":  # VUPOWER인 조건
                    # 연결된 포트 디스플레이
                    comport = self.comm.portstr
                    self.lb_comm_status.setText("통신 연결\n" + comport)
                    # 상태표시창 : 준비 상태
                    self.statusBar.showMessage("Ready")

                    # 파워서플라이 상태 초기화(명령 및 출력)
                    msg = "*RST \n"
                    self.comm.write(msg.encode('utf-8'))

                    # 채널 선택 체크박스 활성화
                    self.cbox_p1.setEnabled(1)
                    self.cbox_p2.setEnabled(1)

                    # 컴포트 선택 박스 비활성화
                    self.cBox_comport.setEnabled(0)
                else:
                    # 경고 메세지 출력
                    QMessageBox.warning(self, "경고", "통신 포트 변경\n(다른 통신 연결임)")

                    # 메인 전원 버튼 OFF
                    self.btn_main_onoff.setChecked(0)
                    self.main_power = False

                    # 경고 메세지 출력에 따라 시스템 대기 상태
                    return
            else:  # 메인 파워 OFF 시키는 조건(ON상태에서 OFF로 전환되므로)
                # 메인 파워 변수 False로 변경
                self.main_power = False

                # 통신 포트 선택 가능하도록 활성화
                self.cBox_comport.setEnabled(1)

                # 채널 선택 False
                self.p1check = False
                self.p2check = False

                # 각 채널 저장 변수 초기화
                self.p1save = True
                self.p2save = True

                # 버튼 비활성화
                self.btn_p1_save.setEnabled(0)
                self.btn_p2_save.setEnabled(0)
                self.btn_start.setEnabled(0)
                self.btn_stop.setEnabled(0)
                self.btn_resultsave.setEnabled(0)

                # 채널 선택 체크박스 해제 및 비활성화
                self.cbox_p1.setChecked(0)
                self.cbox_p2.setChecked(0)
                self.cbox_p1p2.setChecked(0)
                self.cbox_p1.setEnabled(0)
                self.cbox_p2.setEnabled(0)
                self.cbox_p1p2.setEnabled(0)

                # 모드/패턴 입력 항목 비활성화
                self.p1_input_activate(0)
                self.p2_input_activate(0)

                # 통신 연결 해제
                self.comm.close()
                self.lb_comm_status.setText("통신 연결")
                self.statusBar.showMessage("시리얼통신 해제")

        except Exception as ex:
            # 메인 전원 함수 관련 에러 처리
            print('mainpower 에러:', ex)
            self.statusBar.showMessage("시리얼통신 Error")
            if self.main_power == True:
                QMessageBox.warning(self, "경고", "통신 포트 설정 재확인")  # 경고창 출력
                self.btn_main_onoff.setChecked(0)  # 메인 전원 버튼 OFF
                self.main_power = False  # 메인 파워 변수 False로 변경
            return  # 경고 메세지 출력에 따라 시스템 대기 상태

    # 제어 채널 선택 시 실행 함수 ************************************************
    # 1. P1 선택
    def p1selected(self):
        if self.p1check == False:  # 채널 선택 조건
            self.p1check = True  # 채널체크변수 True
            self.p1save = False  # 저장변수 False
            self.btn_p1_save.setEnabled(1)  # 저장 버튼 활성화
            self.cbox_p1p2.setEnabled(1)  # 동시제어 체크박스 활성화
            self.p1_input_activate(1)  # P1 시험 모드/패턴 입력 활성화
        else:  # 채널 선택 해제 조건
            self.p1check = False  # 채널체크변수 False
            self.p1save = True  # 저장변수 True
            self.btn_p1_save.setEnabled(0)  # 저장 버튼 비활성화
            self.cbox_p1p2.setEnabled(0)  # 동시제어 체크박스 비활성화
            self.p1_input_activate(0)  # P1 시험 모드/패턴 입력 비활성화

            # 채널 개별 시험 중 정지
            if self.cbox_p1p2.isChecked() == True:
                self.stop(0)  # 동시제어 상태에서는 모두 종료
                self.cbox_p2.setChecked(0)  # 동시제어 상태에서는 P2 체크해제
                self.cbox_p1p2.setChecked(0)  # 동시제어 상태에서는 동시제어 체크해제
                self.cbox_p1p2.setEnabled(0)  # 동시제어 상태에서는 동시제어 체크해제
                self.p1p2selected()
            else:
                self.stop(1)  # 동시제어가 아니면 P1만 종료
                self.total_testtime = self.p2_testtime  # 전체 시험 시간 재설정

    # 2. P2 선택
    def p2selected(self):
        if self.p2check == False:
            self.p2check = True
            self.p2save = False
            self.btn_p2_save.setEnabled(1)
            self.p2_input_activate(1)
        else:
            self.p2check = False
            self.p2save = True
            self.btn_p2_save.setEnabled(0)
            self.p2_input_activate(0)

            # 채널 개별 시험 중 정지
            self.stop(2)
            if self.cbox_p1p2.isChecked() == True:
                self.cbox_p2.setChecked(0)  # 동시제어 상태에서는 동시제어 체크해제
                self.p1p2selected()
            else:
                self.total_testtime = self.p1_testtime  # 동시제어가 아닌 상태에서는 전체 시험 시간 재설정

    # 3. P1/P2 동시제어 선택(P1 기준으로 동일 작동)
    def p1p2selected(self):
        if self.p1p2check == False:  # 채널 선택 조건
            self.p2check = True  # 동시 제어이므로 자동적으로 P2 채널체크 True
            self.p1p2check = True  # 동시제어체크변수 True
            self.cbox_p2.setChecked(1)  # 동시 제어이므로 자동적으로 P2 채널체크
            self.cbox_p2.setEnabled(0)  # 동시 제어이므로 자동적으로 P2 채널체크 후 비활성화
            self.btn_p2_save.setEnabled(0)  # P2 선택 이후 동시제어 체크가 될 경우를 감안해서 P2 저장 버튼 비활성화
            self.p2_input_activate(0)  # P2 시험 모드/패턴 입력 비활성화
        else:
            self.p2check = False  # 동시 제어이므로 자동적으로 P2 채널체크 False
            self.p1p2check = False  # 동시제어체크변수 False
            self.cbox_p2.setChecked(0)  # P2 선택 체크 해제
            self.cbox_p2.setEnabled(1)  # P2 선택이 가능하도록 체크박스 활성화

    # 제어 모드 선택 시 실행 함수 ************************************************
    # 1. 정전압 모드 선택
    def p1vselected(self):
        if self.p1vcheck == False:
            self.p1vcheck = True  # 정전압 모드 선택 변수 True
            self.p1ccheck = False  # 정전류 모드 선택 변수 False
            self.edit_p1_volt.setEnabled(1)  # 전압 입력창 활성화
            self.edit_p1_current.setEnabled(0)  # 전류 입력창 비활성화

    def p2vselected(self):
        if self.p2vcheck == False:
            self.p2vcheck = True
            self.p2ccheck = False
            self.edit_p2_volt.setEnabled(1)
            self.edit_p2_current.setEnabled(0)

    # 2. 정전류 모드 선택
    def p1cselected(self):
        if self.p1ccheck == False:
            self.p1ccheck = True  # 정전류 모드 선택 변수 True
            self.p1vcheck = False  # 정전압 모드 선택 변수 False
            self.edit_p1_volt.setEnabled(0)  # 전압 입력창 비활성화
            self.edit_p1_current.setEnabled(1)  # 전류 입력창 활성화

    def p2cselected(self):
        if self.p2ccheck == False:
            self.p2ccheck = True
            self.p2vcheck = False
            self.edit_p2_volt.setEnabled(0)
            self.edit_p2_current.setEnabled(1)

    # 제어 패턴 선택 시 실행 함수 ************************************************
    # 1. 연속작동패턴 선택
    def p1contiselected(self):
        if self.p1conticheck == False:
            self.p1conticheck = True  # 연속작동패턴 선택 변수 True
            self.p1onoffcheck = False  # On Off패턴 선택 변수 False
            self.edit_p1_contitime.setEnabled(1)  # 연속작동시간 입력창 활성화
            self.edit_p1_ontime.setEnabled(0)  # On OfF 작동 관련 시간 입력창 비활성화
            self.edit_p1_offtime.setEnabled(0)
            self.edit_p1_totaltime.setEnabled(0)

    def p2contiselected(self):
        if self.p2conticheck == False:
            self.p2conticheck = True
            self.p2onoffcheck = False
            self.edit_p2_contitime.setEnabled(1)
            self.edit_p2_ontime.setEnabled(0)
            self.edit_p2_offtime.setEnabled(0)
            self.edit_p2_totaltime.setEnabled(0)

    # 2. On Off패턴 선택
    def p1onoffselected(self):
        if self.p1onoffcheck == False:
            self.p1onoffcheck = True  # On Off패턴 선택 변수 True
            self.p1conticheck = False  # 연속작동패턴 선택 변수 False
            self.edit_p1_contitime.setEnabled(0)  # 연속작동시간 입력창 비활성화
            self.edit_p1_ontime.setEnabled(1)  # On OfF 작동 관련 시간 입력창 활성화
            self.edit_p1_offtime.setEnabled(1)
            self.edit_p1_totaltime.setEnabled(1)

    def p2onoffselected(self):
        if self.p2onoffcheck == False:
            self.p2onoffcheck = True
            self.p2conticheck = False
            self.edit_p2_contitime.setEnabled(0)
            self.edit_p2_ontime.setEnabled(1)
            self.edit_p2_offtime.setEnabled(1)
            self.edit_p2_totaltime.setEnabled(1)

    # 3. 패턴파일불러오기 선택
    def p1fileloadselected(self):
        if self.p1conticheck == True:  # 연속작동패턴 선택이 되어 있었을 조건
            self.edit_p1_contitime.setEnabled(0)  # 연속작동시간 입력창 비활성화
        elif self.p1onoffcheck == True:  # On Off패턴 선택이 되어 있었을 조건
            self.edit_p1_ontime.setEnabled(0)  # On OfF 작동 관련 시간 입력창 비활성화
            self.edit_p1_offtime.setEnabled(0)
            self.edit_p1_totaltime.setEnabled(0)

        try:
            # Tkinter Filedialog로 확장자 csv 파일 불러오기 실행
            fname_p1 = filedialog.askopenfilename(initialdir="/", title="패턴 CSV 파일 불러오기",
                                                  filetypes=(("csv", "*.csv"), ("all files", "*.*")))

            self.df_p1 = pd.read_csv(fname_p1, engine="python")  # 선택한 csv 파일을 pandas로 읽음
            self.df_p1 = self.df_p1.dropna(axis=1)  # 패턴 작성 설명란 등 빈칸이 있는 열은 삭제

        except Exception as e:
            # 패턴 파일 로드 에러 처리(파일 미선택, 데이터 이상 등)
            print("fileload1 에러 :", e)
            self.rbtn_p1_fileload.setChecked(0)  # 패턴파일 로드 선택 해제
            self.rbtn_p1_conti.setChecked(1)  # 연속작동패턴 선택
            self.edit_p1_contitime.setEnabled(1)  # 연속작동시간 입력창 활성화
            QMessageBox.warning(self, "경고", "패턴 파일 선택 오류")  # 경고창 출력
            return  # 경고 메세지 출력에 따라 시스템 대기 상태

    def p2fileloadselected(self):
        if self.p2conticheck == True:
            self.edit_p2_contitime.setEnabled(0)
        elif self.p2onoffcheck == True:
            self.edit_p2_ontime.setEnabled(0)
            self.edit_p2_offtime.setEnabled(0)
            self.edit_p2_totaltime.setEnabled(0)

        try:
            fname_p2 = filedialog.askopenfilename(initialdir="/", title="패턴 CSV 파일 불러오기",
                                                  filetypes=(("csv", "*.csv"), ("all files", "*.*")))

            self.df_p2 = pd.read_csv(fname_p2, engine="python")
            self.df_p2 = self.df_p2.dropna(axis=1)

        except Exception as e:
            print("fileload2 에러 :", e)
            self.rbtn_p2_fileload.setChecked(0)
            self.rbtn_p2_conti.setChecked(1)
            self.edit_p2_contitime.setEnabled(1)
            QMessageBox.warning(self, "경고", "패턴 파일 로드 오류")
            return

    # 제어 모드/패턴 입력 활성화 변수
    def p1_input_activate(self, status):
        # 넘어오는 인수(Status)가 1이면 활성화, 0이면 비활성화
        if status == 1:
            # 정전압 모드 활성화
            self.rbtn_p1_volt.setEnabled(status)
            # 정전압 모드 체크가 되어있으면 전압 입력창 활성화
            if self.rbtn_p1_volt.isChecked() == True: self.edit_p1_volt.setEnabled(status)

            # 정전류 모드 활성화
            self.rbtn_p1_current.setEnabled(status)
            # 정전류 모드 체크가 되어있으면 전류 입력창 활성화
            if self.rbtn_p1_current.isChecked() == True: self.edit_p1_current.setEnabled(status)

            # 연속작동패턴 활성화
            self.rbtn_p1_conti.setEnabled(status)
            # 연속작동패턴 체크가 되어있으면 연속작동시간 입력창 활성화
            if self.rbtn_p1_conti.isChecked()==True: self.edit_p1_contitime.setEnabled(status)

            # On Off패턴 활성화
            self.rbtn_p1_onoff.setEnabled(status)
            # On Off패턴 체크가 되어있으면 On Off 시간 입력창 활성화
            if self.rbtn_p1_onoff.isChecked() == True:
                self.edit_p1_ontime.setEnabled(status)
                self.edit_p1_offtime.setEnabled(status)
                self.edit_p1_totaltime.setEnabled(status)

            # 패턴파일불러오기 활성화
            self.rbtn_p1_fileload.setEnabled(status)

        else:
            self.rbtn_p1_volt.setEnabled(status)
            self.edit_p1_volt.setEnabled(status)
            self.rbtn_p1_current.setEnabled(status)
            self.edit_p1_current.setEnabled(status)
            self.rbtn_p1_conti.setEnabled(status)
            self.edit_p1_contitime.setEnabled(status)
            self.rbtn_p1_onoff.setEnabled(status)
            self.edit_p1_ontime.setEnabled(status)
            self.edit_p1_offtime.setEnabled(status)
            self.edit_p1_totaltime.setEnabled(status)
            self.rbtn_p1_fileload.setEnabled(status)
    def p2_input_activate(self, status):
        if status == 1:
            self.rbtn_p2_volt.setEnabled(status)
            if self.rbtn_p2_volt.isChecked() == True: self.edit_p2_volt.setEnabled(status)
            self.rbtn_p2_current.setEnabled(status)
            if self.rbtn_p2_current.isChecked() == True: self.edit_p2_current.setEnabled(status)
            self.rbtn_p2_conti.setEnabled(status)
            if self.rbtn_p2_conti.isChecked()==True: self.edit_p2_contitime.setEnabled(status)
            self.rbtn_p2_onoff.setEnabled(status)
            if self.rbtn_p2_onoff.isChecked() == True:
                self.edit_p2_ontime.setEnabled(status)
                self.edit_p2_offtime.setEnabled(status)
                self.edit_p2_totaltime.setEnabled(status)
            self.rbtn_p2_fileload.setEnabled(status)
        else:
            self.rbtn_p2_volt.setEnabled(status)
            self.edit_p2_volt.setEnabled(status)
            self.rbtn_p2_current.setEnabled(status)
            self.edit_p2_current.setEnabled(status)
            self.rbtn_p2_conti.setEnabled(status)
            self.edit_p2_contitime.setEnabled(status)
            self.rbtn_p2_onoff.setEnabled(status)
            self.edit_p2_ontime.setEnabled(status)
            self.edit_p2_offtime.setEnabled(status)
            self.edit_p2_totaltime.setEnabled(status)
            self.rbtn_p2_fileload.setEnabled(status)

    # 제어 명령 저장 함수(SAVE 버튼 클릭 시 실행)
    def p1modesave(self):
        # 출력 선택 체크박스 비활성화, START 시에 비활성화를 SAVE이후로 변경
        # 채널 개별 시험 중 정지를 위해서 활성화
        # self.cbox_p1.setEnabled(0)
        # self.cbox_p1p2.setEnabled(0)
        try:
            # 입력 체크가 되어있으나 0이면 경고 메세지 출력
            # 공란일 경우 에러 처리로 경고 메세지 출력
            # 패턴파일 불러오기를 선택할 경우는 전압/전류/시간 미입력 무시
            if self.rbtn_p1_fileload.isChecked() == False:
                if self.edit_p1_volt.isEnabled()==True and (self.edit_p1_volt.text() == "0"):
                    QMessageBox.warning(self, "경고", "전압 입력 재확인")
                    return
                elif self.edit_p1_current.isEnabled()==True and (self.edit_p1_current.text() == "0"):
                    QMessageBox.warning(self, "경고", "전류 입력 재확인")
                    return
                if self.edit_p1_contitime.isEnabled()==True and (self.edit_p1_contitime.text() == "0"):
                    QMessageBox.warning(self, "경고", "시험 시간 재확인")
                    return
                elif self.edit_p1_totaltime.isEnabled()==True and (self.edit_p1_totaltime.text() == "0"):
                    QMessageBox.warning(self, "경고", "시험 시간 재확인")
                    return

            # 동시제어 선택 시
            if self.cbox_p1p2.isChecked() == True:
                # 모드별로 P1 P2에 전압/전류 제한값 설정
                # 1. 정전압 모드
                # 전압은 입력받은 값으로 설정, 전류는 Max로 설정
                if self.rbtn_p1_volt.isChecked() == True:
                    self.rbtn_p2_volt.setChecked(1)
                    p1_volt = self.edit_p1_volt.text()
                    if type(float(p1_volt)) is not float: raise Exception         # 입력값 오류 시 강제 에러 호출
                    msg = "APPL P1, %s, MAX\n" % p1_volt
                    self.comm.write(msg.encode('utf-8'))
                    msg = "APPL P2, %s, MAX\n" % p1_volt
                    self.comm.write(msg.encode('utf-8'))
                # 2. 정전류 모드
                # 전압은 Max로 설정, 전류는 입력받은 값으로 설정
                elif self.rbtn_p1_current.isChecked() == True:
                    self.rbtn_p2_current.setChecked(1)
                    p1_current = self.edit_p1_current.text()
                    if type(float(p1_current)) is not float: raise Exception  # 입력값 오류 시 강제 에러 호출
                    msg = "APPL P1, MAX, %s\n" % p1_current
                    self.comm.write(msg.encode('utf-8'))
                    msg = "APPL P2, MAX, %s\n" % p1_current
                    self.comm.write(msg.encode('utf-8'))

                # 패턴 확인
                # 1. 연속작동
                if self.rbtn_p1_conti.isChecked() == True:
                    self.rbtn_p2_conti.setChecked(1)                            # P2도 동일하게 패턴 선택으로 표시
                    self.p1_testtime = int(self.edit_p1_contitime.text())       # 전체 시험 시간 변수 저장
                    self.p2_testtime = int(self.edit_p1_contitime.text())
                # 2. On Off 작동
                elif self.rbtn_p1_onoff.isChecked() == True:
                    self.rbtn_p2_onoff.setChecked(1)                            # P2도 동일하게 패턴 선택으로 표시
                    self.p1_onoff_ontime = int(self.edit_p1_ontime.text())      # On 시간 변수 저장
                    self.p1_onoff_offtime = int(self.edit_p1_offtime.text())    # Off 시간 변수 저장
                    self.p1_testtime = int(self.edit_p1_totaltime.text())       # 전체 시험 시간 변수 저장
                    self.p2_onoff_ontime = int(self.edit_p1_ontime.text())
                    self.p2_onoff_offtime = int(self.edit_p1_offtime.text())
                    self.p2_testtime = int(self.edit_p1_totaltime.text())
                # 3. 패턴파일 불러오기
                elif self.rbtn_p1_fileload.isChecked() == True:
                    self.rbtn_p2_fileload.setChecked(1)                         # P2도 동일하게 패턴 선택으로 표시
                    self.p1_file_testmode = []                                  # 모드 저장 리스트 초기화 (1:정전압, 2:정전류)
                    self.p1_file_testvalue = []                                 # 입력값 저장 리스트 초기화 (모드1:전압, 모드2:전류)
                    self.p1_file_testoutput = []                                # 출력상태 저장 리스트 초기화 (1:ON, 0:OFF)
                    for i in range(len(self.df_p1)):
                        self.p1_testtime = len(self.df_p1) - 1                  # 전체 시험시간 = csv에서 읽어와 저장한 DataFrame 길이 - 1
                        self.p1_file_testmode.append(self.df_p1['MODE'][i])     # 시간별 출력 모드 저장
                        self.p1_file_testvalue.append(self.df_p1['VALUE'][i])   # 시간별 입력값 저장
                        self.p1_file_testoutput.append(self.df_p1['OUTPUT'][i]) # 시간별 출력상태 저장
                    self.p2_testtime = self.p1_testtime                         # P2는 P1값과 동일하게 저장
                    self.p2_file_testmode = self.p1_file_testmode
                    self.p2_file_testvalue = self.p1_file_testvalue
                    self.p2_file_testoutput = self.p1_file_testoutput

                # P1 P2 저장 완료 메세지 출력
                QMessageBox.about(self, "message", "P1/P2 테스트 모드 저장 완료")

                # 저장버튼을 눌렀으므로 저장버튼은 비활성화
                self.btn_p1_save.setEnabled(0)
                self.btn_p2_save.setEnabled(0)

                # 입력저장함수 True
                self.p1save = True
                self.p2save = True
                # 입력 비활성화
                self.p1_input_activate(0)
                self.p2_input_activate(0)

            else:

                # 모드 확인
                if self.rbtn_p1_volt.isChecked() == True:
                    p1_volt = self.edit_p1_volt.text()
                    if type(float(p1_volt)) is not float: raise Exception  # 입력값 오류 시 강제 에러 호출
                    msg = "APPL P1, %s, MAX\n" % p1_volt
                    self.comm.write(msg.encode('utf-8'))
                elif self.rbtn_p1_current.isChecked() == True:
                    p1_current = self.edit_p1_current.text()
                    if type(float(p1_current)) is not float: raise Exception  # 입력값 오류 시 강제 에러 호출
                    msg = "APPL P1, MAX, %s\n" % p1_current
                    self.comm.write(msg.encode('utf-8'))

                # 패턴 확인
                if self.rbtn_p1_conti.isChecked() == True:
                    self.p1_testtime = int(self.edit_p1_contitime.text())
                elif self.rbtn_p1_onoff.isChecked() == True:
                    self.p1_onoff_ontime = int(self.edit_p1_ontime.text())
                    self.p1_onoff_offtime = int(self.edit_p1_offtime.text())
                    self.p1_testtime = int(self.edit_p1_totaltime.text())
                elif self.rbtn_p1_fileload.isChecked() == True:
                    self.p1_file_testmode = []
                    self.p1_file_testvalue = []
                    self.p1_file_testoutput = []
                    for i in range(len(self.df_p1)):
                        self.p1_testtime = len(self.df_p1) - 1
                        self.p1_file_testmode.append(self.df_p1['MODE'][i])
                        self.p1_file_testvalue.append(self.df_p1['VALUE'][i])
                        self.p1_file_testoutput.append(self.df_p1['OUTPUT'][i])

                QMessageBox.about(self, "message", "P1 테스트 모드 저장 완료")
                self.btn_p1_save.setEnabled(0)
                self.p1save = True
                self.p1_input_activate(0)

            # 저장완료변수가 모두 True면 시험 시작 버튼 활성화 / 결과 저장 버튼 비활성화
            if self.p1save == True and self.p2save == True:
                self.btn_start.setEnabled(1)
                self.btn_resultsave.setEnabled(0)

        except Exception as ex:
            # 모드/패턴 입력 에러 처리
            print('p1modesave 에러:', ex)
            QMessageBox.warning(self, "경고", "모드/패턴 입력 재확인")
            return
    def p2modesave(self):
        # 출력 선택 체크박스 비활성화, START 시에 비활성화를 SAVE이후로 변경
        # 채널 개별 시험 중 정지를 위해서 활성화
        # self.cbox_p2.setEnabled(0)
        try:
            if self.cbox_p2.isChecked() == True and self.rbtn_p2_fileload.isChecked() == False:
                if self.edit_p2_volt.isEnabled()==True and self.edit_p2_volt.text() == "0":
                    QMessageBox.warning(self, "경고", "전압 입력 재확인")
                    return
                elif self.edit_p2_current.isEnabled()==True and self.edit_p2_current.text() == "0":
                    QMessageBox.warning(self, "경고", "전류 입력 재확인")
                    return
                if self.edit_p2_contitime.isEnabled()==True and self.edit_p2_contitime.text() == "0":
                    QMessageBox.warning(self, "경고", "시험 시간 재확인")
                    return
                elif self.edit_p2_totaltime.isEnabled()==True and self.edit_p2_totaltime.text() == "0":
                    QMessageBox.warning(self, "경고", "시험 시간 재확인")
                    return

            # 모드 확인
            if self.rbtn_p2_volt.isChecked() == True:
                p2_volt = self.edit_p2_volt.text()
                if type(float(p2_volt)) is not float: raise Exception  # 입력값 오류 시 강제 에러 호출
                msg = "APPL P2, %s, MAX\n" % p2_volt
                self.comm.write(msg.encode('utf-8'))
            elif self.rbtn_p2_current.isChecked() == True:
                p2_current = self.edit_p2_current.text()
                if type(float(p2_current)) is not float: raise Exception  # 입력값 오류 시 강제 에러 호출
                msg = "APPL P2, MAX, %s\n" % p2_current
                self.comm.write(msg.encode('utf-8'))

            # 패턴 확인
            if self.rbtn_p2_conti.isChecked() == True:
                self.p2_testtime = int(self.edit_p2_contitime.text())
            elif self.rbtn_p2_onoff.isChecked() == True:
                self.p2_onoff_ontime = int(self.edit_p2_ontime.text())
                self.p2_onoff_offtime = int(self.edit_p2_offtime.text())
                self.p2_testtime = int(self.edit_p2_totaltime.text())
            elif self.rbtn_p2_fileload.isChecked() == True:
                self.p2_file_testmode = []
                self.p2_file_testvalue = []
                self.p2_file_testoutput = []
                for i in range(len(self.df_p2)):
                    self.p2_testtime = len(self.df_p2) - 1
                    self.p2_file_testmode.append(self.df_p2['MODE'][i])
                    self.p2_file_testvalue.append(self.df_p2['VALUE'][i])
                    self.p2_file_testoutput.append(self.df_p2['OUTPUT'][i])

            QMessageBox.about(self, "message", "P2 테스트 모드 저장 완료")
            self.btn_p2_save.setEnabled(0)
            self.p2save = True
            self.p2_input_activate(0)

            if self.p1save == True and self.p2save == True:
                self.btn_start.setEnabled(1)
                self.btn_resultsave.setEnabled(0)

        except Exception as ex:
            print('p2modesave 에러:', ex)

    # 시험 실행 변수(START 버튼 클릭 시 실행)
    def start(self):
        self.p1_test_cnt = 0
        self.p2_test_cnt = 0
        if self.cbox_p1.isChecked() == True or self.cbox_p2.isChecked() == True:
            self.statusBar.showMessage("TEST 시작")
            self.progressBar.setValue(0)    # progress bar 초기화
            print("테스트 Start")
            self.btn_start.setEnabled(0)    # 시작버튼 비활성화
            self.btn_stop.setEnabled(1)     # 정지버튼 활성화
            self.btn_p1_save.setEnabled(0)  # 저장버튼 비활성화
            self.btn_p2_save.setEnabled(0)

            # 전체 시험 현황 모니터링을 위한 타이머 설정
            # 현재 테스트시간 변수 초기화
            self.testtime = 0
            # 전체 시험 시간 설정(P1과 P2 시험 시간이 다른 경우 큰 값으로 설정)
            self.total_testtime = max(self.p1_testtime, self.p2_testtime)
            # 타이머 셋팅
            self.progress_timer = QTimer(self)
            self.progress_timer.start(1000)
            self.progress_timer.timeout.connect(self.progress_timeout)

            # 시험 시간/전압/전류 모니터링 값 저장 변수 초기화
            # Start 실행 시 초기 셋팅이 되지 않으면, 이전 시험값이 그대로 남아있는 오류 해결
            self.test_time1 = []
            self.test_v1 = []
            self.test_c1 = []
            self.test_time2 = []
            self.test_v2 = []
            self.test_c2 = []
        else:
            QMessageBox.warning(self, "경고", "시험 채널을 선택하세요.")
            return
        if self.cbox_p1p2.isChecked() == True: self.cbox_p1p2.setEnabled(0)
        if self.cbox_p1.isChecked() == True:
            # P1 시험 진행 카운트 초기화
            self.p1_test_cnt = 0

            # P1 시험 상태
            self.p1_teststatus = True
            self.cbox_p1.setEnabled(1)

            # 연속작동패턴 시험 시는 바로 저장한 값으로 출력 시작
            if self.rbtn_p1_conti.isChecked() == True:
                msg = "OUTP:STAT P1,ON\n"
                self.comm.write(msg.encode('utf-8'))
                # P1 연속작동 타이머 시작
                self.p1_timer1.start(1000)

            # On Off패턴 시험 시는 출력과 정지가 반복되므로
            # 출력 상태별 카운트 및 상태 변수 할당
            elif self.rbtn_p1_onoff.isChecked() == True:
                self.p1_on_cnt = 0          # On 카운트/Off 카운트 별개로 초기화
                self.p1_off_cnt = 0
                self.p1_status_on = True    # 시작을 ON으로 하는 출력 상태 변수 초기화(On:True, Off:False)
                self.p1_status_off = False
                self.p1_timer2.start(1000)  # P1 OnOff작동 타이머 시작

            # 패턴파일 시험 시는 타이머에서 각 리스트 값을 읽어서 시간별 출력함.
            # P1 패턴파일 작동 타이머 시작
            elif self.rbtn_p1_fileload.isChecked() == True:
                self.p1_timer3.start(1000)

        if self.cbox_p2.isChecked() == True:
            self.p2_test_cnt = 0
            self.p2_teststatus = True
            self.cbox_p2.setEnabled(1)
            if self.rbtn_p2_conti.isChecked() == True:
                msg = "OUTP:STAT P2,ON\n"
                self.comm.write(msg.encode('utf-8'))
                self.p2_timer1.start(1000)

            elif self.rbtn_p2_onoff.isChecked() == True:
                self.p2_on_cnt = 0
                self.p2_off_cnt = 0
                self.p2_status_on = True
                self.p2_status_off = False
                self.p2_timer2.start(1000)

            elif self.rbtn_p2_fileload.isChecked() == True:
                self.p2_timer3.start(1000)

    # 타이머 ************************************************
    # 1. 시험 진행 모니터링 타이머
    def progress_timeout(self):
        try:
            if self.testtime < self.total_testtime:         # 시험 진행 중
                # 시험 시간 변수 증가
                self.testtime += 1
                # Progress Bar 디스플레이(전체 시간 대비 비율)
                self.progressBar.setValue(self.testtime / self.total_testtime * 100)
                # 시험 시간 디스플레이
                self.statusBar.showMessage("TEST중... %s sec" % str(self.testtime))

            elif self.testtime >= self.total_testtime:      # 시험 종료
                self.statusBar.showMessage("TEST 완료")

                # 각 채널 시험 시간 초기화
                self.p1_testtime = 0
                self.p2_testtime = 0

                # 시험 상태 초기화
                self.p1_teststatus = False
                self.p2_teststatus = False

                # 작동 중인 타이머 정지
                if self.p1_timer1.isActive() == True: self.p1_timer1.stop()
                if self.p1_timer2.isActive() == True: self.p1_timer2.stop()
                if self.p2_timer1.isActive() == True: self.p2_timer1.stop()
                if self.p2_timer2.isActive() == True: self.p2_timer2.stop()
                if self.progress_timer.isActive() == True: self.progress_timer.stop()

                # 정지 버튼 비활성화
                self.btn_stop.setEnabled(0)

                # 시험 완료에 따라서 입력 관련 대기상태
                if self.cbox_p1.isChecked() == True:
                    self.p1save = False
                    self.p1_input_activate(1)
                    self.btn_p1_save.setEnabled(1)
                if self.cbox_p2.isChecked() == True and self.cbox_p1p2.isChecked() == False:
                    self.p2save = False
                    self.p2_input_activate(1)
                    self.btn_p2_save.setEnabled(1)

                # 시험 완료 후 입력 변경이 가능하도록 채널 선택 체크박스 활성화
                self.cbox_p1.setEnabled(1)
                self.cbox_p2.setEnabled(1)

        except Exception as ex:
            print('progress_timeout 에러:', ex)

    # 2. 연속작동 타이머
    def p1_timeout_conti(self):
        try:
            # 저장 이후 채널 선택 체크 해제가 될 수 있으므로
            # 불필요한 작동을 없애기 위해서 체크 상태 재확인
            if self.cbox_p1.isChecked() == True:
                # 전압/전류 모니터링
                volt, current = self.measure_p1()

                # 진행 시간별 전압/전류 저장 간격 설정
                # ~ 300sec : 5초 단위
                # 300 ~ 600sec : 10초 단위
                # 600 ~ 1800sec : 30초 단위
                # 1800 ~ : 1800초 단위

                # 매 1초마다 저장 시 아래 3개 활성화
                # self.test_time1.append(self.p1_test_cnt)
                # self.test_v1.append(float(volt))
                # self.test_c1.append(float(current))

                # 시험 진행 시간별 저장조건 변경 시 활성화
                if self.p1_test_cnt == 1:                       # 시험 초기 0초는 저장하지 않고 1초때 저장(0초 저장시는 불완전한 값 저장됨)
                    self.test_time1.append(0)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))
                elif self.p1_test_cnt <= 300 and self.p1_test_cnt % 5 == 0 and self.p1_test_cnt != 0:
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))
                elif self.p1_test_cnt > 300 and self.p1_test_cnt <= 600 and self.p1_test_cnt % 10 == 0:
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))
                elif self.p1_test_cnt > 600 and self.p1_test_cnt <= 1800 and self.p1_test_cnt % 30 == 0:
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))
                elif self.p1_test_cnt > 1800 and self.p1_test_cnt % 1800 == 0:
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))

                # P1 시험 진행 카운트 증가
                self.p1_test_cnt += 1

                # 시험 진행 카운트와 시험 시간이 동일한 조건 즉, 완료 시
                if self.p1_test_cnt == self.p1_testtime:
                    # 테스트 마지막 결과 저장 후 종료
                    volt, current = self.measure_p1()
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))

                    # P1 정지를 위한 STOP함수에 1 전달
                    self.stop(1)
            else:                           # 채널 개별 시험 중 정지
                if self.p1_timer1.isActive() == True: self.p1_timer1.stop()

        except Exception as ex:
            print('p1_timeout_conti 에러:', ex)
    def p2_timeout_conti(self):
        try:
            if self.cbox_p2.isChecked() == True:
                volt, current = self.measure_p2()

                # 매 1초마다 저장 시 아래 3개 활성화
                # self.test_time2.append(self.p2_test_cnt)
                # self.test_v2.append(float(volt))
                # self.test_c2.append(float(current))

                # 시험 진행 시간별 저장조건 변경 시 활성화
                if self.p2_test_cnt == 1:                       # 시험 초기 0초는 저장하지 않고 1초때 저장
                    self.test_time2.append(0)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))
                elif self.p2_test_cnt <= 300 and self.p2_test_cnt % 5 == 0 and self.p2_test_cnt != 0:
                    self.test_time2.append(self.p2_test_cnt)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))
                elif self.p2_test_cnt > 300 and self.p2_test_cnt <= 600 and self.p2_test_cnt % 10 == 0:
                    self.test_time2.append(self.p2_test_cnt)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))
                elif self.p2_test_cnt > 600 and self.p2_test_cnt <= 1800 and self.p2_test_cnt % 30 == 0:
                    self.test_time2.append(self.p2_test_cnt)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))
                elif self.p2_test_cnt > 1800 and self.p2_test_cnt % 1800 == 0:
                    self.test_time2.append(self.p2_test_cnt)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))

                self.p2_test_cnt += 1

                if self.p2_test_cnt == self.p2_testtime:
                    volt, current = self.measure_p2()
                    self.test_time2.append(self.p2_test_cnt)
                    self.test_v2.append(float(volt))
                    self.test_c2.append(float(current))

                    self.stop(2)
            else:                           # 채널 개별 시험 중 정지
                if self.p2_timer1.isActive() == True: self.p2_timer1.stop()

        except Exception as ex:
            print('p2_timeout_conti 에러:', ex)

    # 3. On Off 작동 타이머
    def p1_timeout_onoff(self):
        # 저장 이후 채널 선택 체크 해제가 될 수 있으므로
        # 불필요한 작동을 없애기 위해서 체크 상태 재확인
        try:
            if self.cbox_p1.isChecked() == True or self.cbox_p1p2.isChecked() == True:
                # 출력 상태를 True로 받아서 타이머가 작동되었으므로 바로 출력 ON시킴
                if self.p1_status_on == True:
                    msg = "OUTP:STAT P1,ON\n"
                    self.comm.write(msg.encode('utf-8'))
                    # On 카운트 증가
                    self.p1_on_cnt += 1

                    # 전압/전류 모니터링
                    volt, current = self.measure_p1()

                    # On Off 작동 시에는 ON 상태에서 결과 저장
                    self.test_time1.append(self.p1_test_cnt)
                    self.test_v1.append(float(volt))
                    self.test_c1.append(float(current))

                elif self.p1_status_off == True:
                    msg = "OUTP:STAT P1,OFF\n"
                    self.comm.write(msg.encode('utf-8'))
                    self.p1_off_cnt += 1

                # 출력 상태 카운트가 입력된 On Off 시간과 같으면 반대 작동으로 상태 전환 및 카운트 초기화
                # 다음 타이머 시에 상태에 맞게 출력
                if self.p1_on_cnt == self.p1_onoff_ontime:
                    self.p1_status_on = False
                    self.p1_status_off = True
                    self.p1_on_cnt = 0
                elif self.p1_off_cnt == self.p1_onoff_offtime:
                    self.p1_status_on = True
                    self.p1_status_off = False
                    self.p1_off_cnt = 0

            # 시험 진행 카운트를 증가시키고 시험 시간과 같아지면 정지
            self.p1_test_cnt += 1
            if self.p1_test_cnt == self.p1_testtime:
                volt, current = self.measure_p1()
                self.test_time1.append(self.p1_test_cnt)
                self.test_v1.append(float(volt))
                self.test_c1.append(float(current))

                self.stop(1)
        except Exception as ex:
            print('stop 에러:', ex)
    def p2_timeout_onoff(self):
        if self.cbox_p2.isChecked() == True or self.cbox_p1p2.isChecked() == True:
            if self.p2_status_on == True:
                msg = "OUTP:STAT P2,ON\n"
                self.comm.write(msg.encode('utf-8'))
                self.p2_on_cnt += 1

                volt, current = self.measure_p2()  # 측정 내용 반복에 따라 별도 함수화

                self.test_time2.append(self.p2_test_cnt)
                self.test_v2.append(float(volt))
                self.test_c2.append(float(current))

            elif self.p2_status_off == True:
                msg = "OUTP:STAT P2,OFF\n"
                self.comm.write(msg.encode('utf-8'))
                self.p2_off_cnt += 1

            if self.p2_on_cnt == self.p2_onoff_ontime:
                self.p2_status_on = False
                self.p2_status_off = True
                self.p2_on_cnt = 0
            elif self.p2_off_cnt == self.p2_onoff_offtime:
                self.p2_status_on = True
                self.p2_status_off = False
                self.p2_off_cnt = 0

        self.p2_test_cnt += 1
        if self.p2_test_cnt == self.p2_testtime:
            volt, current = self.measure_p2()
            self.test_time2.append(self.p2_test_cnt)
            self.test_v2.append(float(volt))
            self.test_c2.append(float(current))
            self.stop(2)

    # 4. 패턴파일 작동 타이머
    def p1_timeout_file(self):
        try:
            # 출력 모드 확인
            if self.p1_file_testmode[self.p1_test_cnt] == 1: # 정전압 모드
                p1_volt = self.p1_file_testvalue[self.p1_test_cnt]
                msg = "APPL P1, %s, MAX\n" % p1_volt
                self.comm.write(msg.encode('utf-8'))
            else:                                            # 정전류 모드
                p1_current = self.p1_file_testvalue[self.p1_test_cnt]
                msg = "APPL P1, MAX, %s\n" % p1_current
                self.comm.write(msg.encode('utf-8'))

            # 출력 패턴 확인
            if self.p1_file_testoutput[self.p1_test_cnt] == 1:  # 출력패턴 ON
                msg = "OUTP:STAT P1,ON\n"
                self.comm.write(msg.encode('utf-8'))

                volt, current = self.measure_p1()

                self.test_time1.append(self.p1_test_cnt)
                self.test_v1.append(float(volt))
                self.test_c1.append(float(current))
            else:                                               # 출력패턴 OFF
                msg = "OUTP:STAT P1,OFF\n"
                self.comm.write(msg.encode('utf-8'))

            self.p1_test_cnt += 1
            if self.p1_test_cnt == self.p1_testtime:
                volt, current = self.measure_p1()
                self.test_time1.append(self.p1_test_cnt)
                self.test_v1.append(float(volt))
                self.test_c1.append(float(current))
                self.stop(1)

        except Exception as ex:
            print('p1_timeout_file 에러:', ex)
    def p2_timeout_file(self):
        try:
            # 출력 모드 확인
            if self.p2_file_testmode[self.p2_test_cnt] == 1:  # 정전압 모드
                p2_volt = self.p2_file_testvalue[self.p2_test_cnt]
                msg = "APPL P2, %s, MAX\n" % p2_volt
                self.comm.write(msg.encode('utf-8'))
            else:  # 정전류 모드
                p2_current = self.p2_file_testvalue[self.p2_test_cnt]
                msg = "APPL P2, MAX, %s\n" % p2_current
                self.comm.write(msg.encode('utf-8'))

            # 출력 패턴 확인
            if self.p2_file_testoutput[self.p2_test_cnt] == 1:  # 출력패턴 ON
                msg = "OUTP:STAT P2,ON\n"
                self.comm.write(msg.encode('utf-8'))

                volt, current = self.measure_p1()  # 측정 내용 반복에 따라 별도 함수화

                self.test_time2.append(self.p2_test_cnt)
                self.test_v2.append(float(volt))
                self.test_c2.append(float(current))
            else:                                               # 출력패턴 OFF
                msg = "OUTP:STAT P2,OFF\n"
                self.comm.write(msg.encode('utf-8'))

            self.p2_test_cnt += 1
            if self.p2_test_cnt == self.p2_testtime:
                volt, current = self.measure_p2()
                self.test_time2.append(self.p2_test_cnt)
                self.test_v2.append(float(volt))
                self.test_c2.append(float(current))
                self.stop(2)

        except Exception as ex:
            print('p2_timeout_file 에러:', ex)

    # 전압/전류 모니터링/출력 변수
    def measure_p1(self):
        msg = "MEAS:VOLTA? P1\n"
        self.comm.write(msg.encode('utf-8'))
        volt = self.comm.readline().decode('utf-8').replace('\n', '')
        self.lb_p1_volt.setText(volt)

        msg = "MEAS:CURRA? P1\n"
        self.comm.write(msg.encode('utf-8'))
        current = self.comm.readline().decode('utf-8').replace('\n', '')
        self.lb_p1_current.setText(current)

        return(volt, current)
    def measure_p2(self):
        msg = "MEAS:VOLTA? P2\n"
        self.comm.write(msg.encode('utf-8'))
        volt = self.comm.readline().decode('utf-8').replace('\n', '')
        self.lb_p2_volt.setText(volt)

        msg = "MEAS:CURRA? P2\n"
        self.comm.write(msg.encode('utf-8'))
        current = self.comm.readline().decode('utf-8').replace('\n', '')
        self.lb_p2_current.setText(current)

        return (volt, current)

    # 시험 정지 변수(STOP버튼 클릭 시 실행)
    def stop(self, ch=3):
        # 전달되는 ch값에 따라 초기화 및 타이머 정지(1:P1, 2:P2, 0:P1/P2)
        try:

            if ch == 1:
                # 시험 상태
                self.p1_teststatus = False
                if self.p2_teststatus == False : self.stop(0)

                self.statusBar.showMessage("P1 TEST 정지")
                if self.testtime >= self.total_testtime:
                    self.btn_start.setEnabled(1)
                    self.btn_stop.setEnabled(0)
                    self.btn_p1_save.setEnabled(1)
                    self.btn_p2_save.setEnabled(1)

                msg = "OUTP:STAT P1,OFF\n"
                self.comm.write(msg.encode('utf-8'))

                if self.p1_timer1.isActive() == True: self.p1_timer1.stop()
                if self.p1_timer2.isActive() == True: self.p1_timer2.stop()
                if self.p1_timer3.isActive() == True: self.p1_timer3.stop() # 시험 파일 로드 추가에 따른 타이머 정지

                self.lb_p1_volt.setText(" ")
                self.lb_p1_current.setText(" ")

            elif ch == 2:
                # 시험 상태
                self.p2_teststatus = False
                if self.p1_teststatus == False: self.stop(0)

                self.statusBar.showMessage("P2 TEST 정지")
                if self.testtime >= self.total_testtime:
                    self.btn_start.setEnabled(1)
                    self.btn_stop.setEnabled(0)
                    self.btn_p1_save.setEnabled(1)
                    self.btn_p2_save.setEnabled(1)

                msg = "OUTP:STAT P2,OFF\n"
                self.comm.write(msg.encode('utf-8'))

                if self.p2_timer1.isActive() == True: self.p2_timer1.stop()
                if self.p2_timer2.isActive() == True: self.p2_timer2.stop()
                if self.p2_timer3.isActive() == True: self.p2_timer3.stop() # 시험 파일 로드 추가에 따른 타이머 정지

                self.lb_p2_volt.setText(" ")
                self.lb_p2_current.setText(" ")

            elif ch == 0:
                # 시험 상태
                self.p1_teststatus = False
                self.p2_teststatus = False

                self.statusBar.showMessage("TEST 정지")

                self.btn_start.setEnabled(1)
                self.btn_stop.setEnabled(0)

                # 시험 종료에 따라서 입력 관련 대기상태
                if self.cbox_p1.isChecked() == True:
                    self.p1save = False
                    self.p1_input_activate(1)
                    self.btn_p1_save.setEnabled(1)
                if self.cbox_p2.isChecked() == True and self.cbox_p1p2.isChecked() == False:
                    self.p2save = False
                    self.p2_input_activate(1)
                    self.btn_p2_save.setEnabled(1)

                msg = "OUTP:STAT P1,OFF\n"
                self.comm.write(msg.encode('utf-8'))
                msg = "OUTP:STAT P2,OFF\n"
                self.comm.write(msg.encode('utf-8'))

                # 강제 정지 버튼을 통한 전체 정지므로 전 타이머 정지시킴
                if self.p1_timer1.isActive() == True: self.p1_timer1.stop()
                if self.p1_timer2.isActive() == True: self.p1_timer2.stop()
                if self.p1_timer3.isActive() == True: self.p1_timer3.stop()
                if self.p2_timer1.isActive() == True: self.p2_timer1.stop()
                if self.p2_timer2.isActive() == True: self.p2_timer2.stop()
                if self.p2_timer3.isActive() == True: self.p2_timer3.stop()
                if self.progress_timer.isActive() == True: self.progress_timer.stop()

                self.lb_p1_volt.setText(" ")
                self.lb_p1_current.setText(" ")
                self.lb_p2_volt.setText(" ")
                self.lb_p2_current.setText(" ")


            # 정지 함수 호출 시 결과 저장 버튼 활성화
            self.btn_resultsave.setEnabled(1)

            self.progressBar.setValue(0)

        except Exception as ex:
            print('stop 에러:', ex)

    # 시험 결과 저장 변수(RESULT SAVE 버튼 클릭 시 실행)
    def resultsave(self):
        try:
            df_1 = DataFrame()
            df_2 = DataFrame()

            filename = filedialog.asksaveasfilename(initialdir="/", title="CSV 파일 저장",
                                                    filetypes=(("csv", "*.csv"), ("all files", "*.*")))

            # 취소나 결과 파일 미입력(미선택) 시 대기상태로 나감
            if filename == "":
                return

            if ".csv" not in filename: filename += ".csv"

            # 시험 중 체크박스 해제를 통한 정지 시 저장이 안되는 문제 개선
            # if self.cbox_p1.isChecked() == True:
            if self.p1_test_cnt > 0:
                df_1['P1_TIME'] = self.test_time1
                df_1['P1_VOLT'] = self.test_v1
                df_1['P1_CURRENT'] = self.test_c1

            # if self.cbox_p2.isChecked() == True:
            if self.p2_test_cnt > 0:
                df_2['P2_TIME'] = self.test_time2
                df_2['P2_VOLT'] = self.test_v2
                df_2['P2_CURRENT'] = self.test_c2

            # DataFrame 합치기
            df = pd.merge(df_1, df_2, how='outer', left_index=True, right_index=True)
            df.to_csv(filename, encoding='UTF-8', index=False)
            QMessageBox.about(self, "message", "결과 저장 완료")

            # 저장 파일 OPEN
            os.startfile(filename)

        except Exception as ex:
            print('resultsave 에러:', ex)
            QMessageBox.warning(self, "경고", "결과 저장 오류")
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()