# ToyProject
* My Toy Projects for Work Efficiency (Design, Test, Analysis, etc.)  
------

## 1. PowerSupplyController
* VuPOWER 사의 programmable power supply인 K1205D을 이용한 솔레노이드 코일 시험용 프로그램  

#### A. 주요 기능
* 파워서플라이와 USB를 이용한 RS232 통신
* P1, P2 독립 제어 및 연동 제어
* CV, CC Mode 별도 지정
* 연속 작동, On/Off 반복 작동, 패턴(별도 CSV 파일) 작동
* 시험 중 전압, 전류 디스플레이
* 시험 완료 후 결과 파일 저장

#### B. 파이썬 패키지
pip install serial

#### C. 사전 설치 드라이버
* [RS232_USB드라이버](http://www.vupower.com/sub.php?page=demo.php)

#### D. 메뉴얼
* [K1205D 메뉴얼](http://www.vupower.com/download/K_USB_Manual_Korea_Ver3.2.pdf)

#### E. 실행화면
![image](./PowerSupplyController/PowerSupplyController.jpg)
------


## 2. PatentSearch
* 특허 검색 사이트(WIPS ON)에서 원하는 키워드를 이용한 특허 검색 자동 크롤러  
[WIPS ON](https://www.wipson.com/service/mai/main.wips)  
------


## 3. OAScheduler
* 업무효율화를 위한 윈도우 작업스케줄러 생성 프로그램으로, 1차 특허 검색 작업 스케줄러 적용  

#### A. 주요 기능
* WIPS ON 아이디 비번 저장
* 한국, 미국, 유럽, 일본 특허 검색 가능
* 스케줄러 설정 : 매주 (각 요일 설정), 매월(월초, 월말)
* 저장하면 아이디, 비번, 검색국가 및 검색어는 "WIPS.csv"에 저장
* 설정한 일정 단위로 작업 스케줄러 "특허 검색" 등록  
  (기존 스케줄러에 "특허 검색"은 삭제 후 신규 등록)
  
#### B. 실행화면
![image](./OAScheduler/OAScheduler_screenshot.jpg)
------
