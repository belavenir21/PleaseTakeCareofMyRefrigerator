from PIL import Image
import os

def split_additional_icons(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    name_list = [
        # Row 1
        "당근", "토마토", "파프리카", "적양파", "청경채", "오이", "사과", "수박조각", "오렌지", "빨간사과", "노란사과", "귤", "키위", "포도",
        # Row 2
        "배추", "브로콜리", "양배추", "적양파", "수박", "가지", "호박", "햄덩어리", "새우", "새우", "새우", "꽃게", "빵", "빵",
        # Row 3
        "토마토", "당근", "귤", "청포도", "서양배", "산딸기", "감자", "우유", "우유", "우유", "우유", "우유", "우유", "오렌지주스",
        # Row 4
        "닭다리", "닭다리", "스테이크", "스테이크", "고기", "고기", "고기", "머스타드", "오렌지소스", "케첩", "바베큐소스", "칠리소스", "땅콩소스", "통조림",
        # Row 5
        "스테이크", "연어", "흰살생선", "치즈", "새우", "양송이버섯", "생선", "토마토통조림", "옥수수통조림", "감자통조림", "콩통조림", "호밀빵", "바게트", "빵",
        # Row 6
        "된장", "쌈장", "치즈", "마늘", "귤", "육쪽마늘", "단호박", "빵", "도넛", "빵", "파이", "파이", "라면", "라면"
    ]

    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    pix = img.load()

    # 4배 업스케일링 (일관성 유지)
    upscale_factor = 4
    img_large = img.resize((w * upscale_factor, h * upscale_factor), resample=Image.NEAREST)
    width, height = img_large.size

    visited = set()
    bboxes = []

    print("Detecting new icons...")
    for y in range(h):
        for x in range(w):
            if pix[x, y][3] > 0 and (x, y) not in visited:
                stack = [(x, y)]
                visited.add((x, y))
                min_x, min_y = x, y
                max_x, max_y = x, y
                while stack:
                    cx, cy = stack.pop()
                    min_x, min_y = min(min_x, cx), min(min_y, cy)
                    max_x, max_y = max(max_x, cx), max(max_y, cy)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if pix[nx, ny][3] > 0 and (nx, ny) not in visited:
                                    visited.add((nx, ny))
                                    stack.append((nx, ny))
                if (max_x - min_x) > 5 and (max_y - min_y) > 5:
                    bboxes.append((min_x, min_y, max_x, max_y))

    # 행/열 정렬 (Row height is approx 84px)
    bboxes.sort(key=lambda b: (round(b[1] / 80), b[0]))
    print(f"Found {len(bboxes)} new icons.")

    # 파일명 중복 처리 및 저장
    existing_files = [f for f in os.listdir(output_dir) if f.endswith('.png')]
    
    for i, bbox in enumerate(bboxes):
        if i >= len(name_list):
            base_name = f"unknown_{i}"
        else:
            base_name = name_list[i]

        # 중복 체크
        final_name = base_name
        suffix = 2
        while f"{final_name}.png" in existing_files:
            final_name = f"{base_name}{suffix}"
            suffix += 1
        
        # 실제 저장할 이름 확정 (리스트에 추가해서 이번 루프 내 중복도 방지)
        existing_files.append(f"{final_name}.png")

        lx, ly, rx, ry = [c * upscale_factor for c in bbox]
        p = 12
        crop_bbox = (max(0, lx-p), max(0, ly-p), min(width, rx+p), min(height, ry+p))
        sprite = img_large.crop(crop_bbox)
        sprite.save(os.path.join(output_dir, f"{final_name}.png"))
        print(f"Saved: {final_name}.png")

if __name__ == "__main__":
    img_path = r'C:/Users/SSAFY/.gemini/antigravity/brain/49d9dcfd-19a8-4d5a-be33-ccb365a2ba90/uploaded_image_1766389511460.png'
    out_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    split_additional_icons(img_path, out_dir)
