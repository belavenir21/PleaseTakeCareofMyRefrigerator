import cv2
import numpy as np
import os
from PIL import Image

def split_sprites(image_path, output_dir):
    # 폴더 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 이미지 로드 (Alpha 채널 포함)
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("Image not found")
        return

    # Alpha 채널 추출
    alpha = img[:, :, 3]

    # 투명하지 않은 영역 찾기
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 각 컨투어의 바운딩 박스를 찾아 정렬 (y 우선, 그 다음 x 순)
    # 그리드 형태로 정렬하기 위함
    bboxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 5 and h > 5:  # 너무 작은 노이즈 제거
            bboxes.append((x, y, w, h))

    # 행 단위로 정렬하기 위한 로직
    # y좌표가 비슷한 것끼리 묶어서 x좌표로 정렬
    bboxes.sort(key=lambda b: (b[1] // 40, b[0])) # 40px 단위로 행 구분 (이미지 높이가 558이므로 적절)

    print(f"Detected {len(bboxes)} icons.")

    for i, (x, y, w, h) in enumerate(bboxes):
        # 약간의 여백 추가 (Padding)
        p = 2
        x1 = max(0, x - p)
        y1 = max(0, y - p)
        x2 = min(img.shape[1], x + w + p)
        y2 = min(img.shape[0], y + h + p)

        sprite = img[y1:y2, x1:x2]
        
        # 저장
        file_path = os.path.join(output_dir, f"icon_{i:03d}.png")
        cv2.imwrite(file_path, sprite)

    print(f"Saved all icons to {output_dir}")

if __name__ == "__main__":
    img_path = r'C:/Users/SSAFY/.gemini/antigravity/brain/49d9dcfd-19a8-4d5a-be33-ccb365a2ba90/uploaded_image_1766382388783.png'
    out_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    split_sprites(img_path, out_dir)
