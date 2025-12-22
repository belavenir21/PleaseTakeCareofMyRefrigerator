from PIL import Image
import os

# 이미지 경로 (사용자 업로드 경로)
img_path = r'C:/Users/SSAFY/.gemini/antigravity/brain/49d9dcfd-19a8-4d5a-be33-ccb365a2ba90/uploaded_image_1766382184553.jpg'

try:
    with Image.open(img_path) as img:
        width, height = img.size
        print(f"Image Dimensions: {width}x{height}")
        # 전체 그리드 파악을 위해 썸네일 정보 출력
        # 육안상 가로 약 22개, 세로 10개
        # 1024 / 22 ~= 46.5
        # 512 / 10 ~= 51.2
        # 정확한 그리드 계산을 위해 AI에게 좌표를 물어보는 것이 좋음
except Exception as e:
    print(f"Error: {e}")
