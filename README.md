# ToyProject
My Toy Projects for Work Efficiency (Design, Test, Analysis, etc.)

## PowerSupplyController
### VuPOWER 사의 programmable power supply인 K1205D을 이용한 솔레노이드 코일 시험용 프로그램

#### 1. 주요 기능
* 파워서플라이와 USB를 이용한 RS232 통신
* P1, P2 독립 제어 및 연동 제어
* CV, CC Mode 별도 지정
* 연속 작동, On/Off 반복 작동, 패턴(별도 CSV 파일) 작동
* 시험 중 전압, 전류 디스플레이
* 시험 완료 후 결과 파일 저장

#### 2. 파이썬 패키지
pip install serial

#### 3. 사전 설치 드라이버
* [RS232_USB드라이버](http://www.vupower.com/sub.php?page=demo.php)

#### 4. 메뉴얼
* [K1205D 메뉴얼](http://www.vupower.com/download/K_USB_Manual_Korea_Ver3.2.pdf)

#### 5. 패턴 csv 형식
* MODE  
|MODE|내용|VALUE|
|---|---|---|
|1|정전압(CV)|전압(V)|
|2|정전류(CC)|전류(A)|
* OUTPUT  
|OUTPUT|내용|
|---|---|
|1|ON|
|2|OFF|
* EXAMPLE
|TIME|MODE|VALUE|PUTPUT|
|---|---|---|---|
|1|1|8|1|
|2|1|8|0|
|3|1|8|0|
|4|1|8|1|
|5|1|8|1|

#### 6. 실행화면
![image.png](attachment:image.png)
