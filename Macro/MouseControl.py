import win32api, win32con
import time

state_left = win32api.GetKeyState(0x01)  # Left button down = 0 or 1. Button up = -127 or -128
state_right = win32api.GetKeyState(0x02)  # Right button down = 0 or 1. Button up = -127 or -128

print("1. 위치를 저장합니다.")
print("   '마우스 이동 + 왼쪽 버튼 클릭'하면 위치가 저장됩니다.")
print("   오른쪽 버튼을 클릭하면 위치 저장이 완료됩니다.")

pos_x = []
pos_y = []

cnt=1
while True:
    left_btn = win32api.GetKeyState(0x01)
    right_btn = win32api.GetKeyState(0x02)

    if left_btn != state_left:  # Button state changed
        state_left = left_btn

        if left_btn < 0:
            mouse_p1 = win32api.GetCursorPos()
            pos_x.append(mouse_p1[0])
            pos_y.append(mouse_p1[1])
            print('좌표', cnt, ":", mouse_p1[0], mouse_p1[1])
            cnt+=1
    if right_btn != state_right:  # Button state changed
        state_right = right_btn

        if right_btn < 0:
            break

    time.sleep(0.001)

print("좌표 저장 완료\n")

times = int(input(("2. 반복 횟수 설정 : ")))

interval = int(input(("3. 각 클릭 동작 사이 인터벌(sec) 설정 : ")))

print("Start!")
for num in range(times):
    for x, y in zip(pos_x, pos_y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(interval)

print("완료")

