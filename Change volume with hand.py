import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# تنظیمات pycaw برای کنترل صدای ویندوز
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# مقداردهی اولیه mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# دسترسی به وب کم
cap = cv2.VideoCapture(0)

def change_volume(fingers):
    # گرفتن مقدار فعلی صدا
    current_volume = volume.GetMasterVolumeLevel()
    
    # تغییر صدا بر اساس تعداد انگشتان باز
    if fingers == 2:
        new_volume = min(current_volume + 2.0, 0.0)  # افزایش صدا
    elif fingers == 0:
        new_volume = max(current_volume - 2.0, -65.25)  # کاهش صدا
    else:
        return
    
    volume.SetMasterVolumeLevel(new_volume, None)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # چک کردن وضعیت انگشتان
            finger_tips = [hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP], 
                           hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]]
            finger_mcp = [hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP], 
                          hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]]
            
            fingers_open = [tip.y < mcp.y for tip, mcp in zip(finger_tips, finger_mcp)]
            fingers_count = sum(fingers_open)
            
            change_volume(fingers_count)
    
    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
