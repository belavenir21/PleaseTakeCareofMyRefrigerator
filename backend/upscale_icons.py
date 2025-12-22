from PIL import Image, ImageDraw
import os

def upscale_and_split_perfect(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    name_list = [
        "소고기", "삼겹살", "생닭", "생선", "두부", "청경채", "배추", "깻잎", "시금치", "부추", "얼갈이배추", "비타민", "공심채", "미나리", "쑥갓", "고구마순", "자색고구마",
        "무", "당근", "양파", "마늘", "감자", "고구마", "양송이버섯", "팽이버섯", "새송이버섯", "애호박", "오이", "가지", "고추", "피망", "숙주", "브로콜리", "양배추",
        "방울토마토", "단호박", "대파", "생강", "레몬", "사과", "서양배", "바나나", "오렌지", "귤", "체리", "도토리", "밤", "대추", "땅콩", "호두", "피칸",
        "아몬드", "베이컨", "참치캔", "만두", "천등", "거봉", "딸기", "포도", "수박", "멜론", "키위", "군밤", "대추야자", "생땅콩", "호두알", "껍질호두", "피넛",
        "슬라이스아몬드", "통아몬드", "캐슈넛", "들깨", "흑임자", "참깨", "검은콩", "말린나물", "은행", "연근", "우엉", "도라지", "더덕", "인삼", "고사리", "말린미역", "다시마",
        "건다시마", "파래", "상추", "전", "연어", "단무지", "샐러드무", "간장", "된장", "고추장", "쌈장", "명란젓", "액젓", "미림", "가쓰오부시", "올리브유", "식용유",
        "참기름", "설탕", "소금", "후추", "고춧가루", "케첩", "머스타드", "고추장봉지", "카레가루", "밀가루", "전분가루", "튀김가루", "부침가루", "빵가루", "소면", "당면", "파스타면",
        "라면", "컵라면", "떡볶이떡", "만두피", "비엔나소시지", "스팸", "베이컨줄", "참치캔2", "런천미트", "치즈", "버터", "우유", "요거트", "플레인요거트", "메추리알", "계란후라이", "계란",
        "오리알", "꽃게", "새우", "꼴뚜기", "문어", "조개", "홍합", "굴", "가리비", "전복", "꼬막", "멍게", "해삼", "미더덕", "말린새우", "맛살", "멸치",
        "뱅어포", "황태", "오징어채", "육포", "해파리", "문어다리", "게살", "연어알", "조개관자", "전복껍질", "고둥", "소라", "해초"
    ]

    # 1. 원본 로드
    img_orig = Image.open(image_path).convert("RGBA")
    w_orig, h_orig = img_orig.size
    pix_orig = img_orig.load()

    # 2. 고화질 보존 업스케일링
    upscale_factor = 4
    img_large = img_orig.resize((w_orig * upscale_factor, h_orig * upscale_factor), resample=Image.NEAREST)
    width, height = img_large.size
    
    # 3. 아주 예민한 아이콘 감지 (작은 점도 절대 놓치지 않음)
    visited = set()
    bboxes = []

    print("Step 1: Hyper-sensitive icon detection...")
    for y in range(h_orig):
        for x in range(w_orig):
            # 투명도가 1이라도 있으면 무조건 아이콘 후보
            if pix_orig[x, y][3] > 0 and (x, y) not in visited:
                stack = [(x, y)]
                visited.add((x, y))
                min_x, min_y = x, y
                max_x, max_y = x, y
                
                while stack:
                    cx, cy = stack.pop()
                    min_x, min_y = min(min_x, cx), min(min_y, cy)
                    max_x, max_y = max(max_x, cx), max(max_y, cy)
                    
                    # 8방향 탐색으로 더 꼼꼼하게 (대각선 포함)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w_orig and 0 <= ny < h_orig:
                                if pix_orig[nx, ny][3] > 0 and (nx, ny) not in visited:
                                    visited.add((nx, ny))
                                    stack.append((nx, ny))
                
                # 최소 크기 제한을 거의 없앰 (먼지만 수준이 아니면 다 잡음)
                if (max_x - min_x) >= 2 or (max_y - min_y) >= 2:
                    bboxes.append((min_x, min_y, max_x, max_y))

    # 4. 뭉쳐 있는 박스들 분리 시도 (너무 큰 박스는 재검토)
    # 이미지 특성상 한 칸이 약 60x55 정도임
    refined_bboxes = []
    avg_w = 60
    avg_h = 55
    for b in bboxes:
        bw = b[2] - b[0]
        bh = b[3] - b[1]
        # 만약 박스가 너무 넓다면 두 개의 아이콘이 붙은 것임 (예: 90px 이상)
        if bw > 85:
            mid = b[0] + bw // 2
            refined_bboxes.append((b[0], b[1], mid, b[3]))
            refined_bboxes.append((mid + 1, b[1], b[2], b[3]))
            print(f"Splitting wide icon at {b[0]}, {b[1]}")
        else:
            refined_bboxes.append(b)

    # 행 단위 정렬 (버킷 정렬 방식 사용 - Y좌표 오차 허용)
    refined_bboxes.sort(key=lambda b: (round(b[1] / 50), b[0]))
    
    print(f"Step 2: Found {len(refined_bboxes)} icons after refining. Saving...")

    # 출력 폴더 정리
    for f in os.listdir(output_dir):
        if f.endswith(".png"):
            os.remove(os.path.join(output_dir, f))

    # 5. 저장
    for i, bbox in enumerate(refined_bboxes):
        if i >= len(name_list):
            label = f"unknown_{i:03d}"
        else:
            label = name_list[i]
            
        lx, ly, rx, ry = [c * upscale_factor for c in bbox]
        p = 12 # 여백 넉넉히
        crop_bbox = (max(0, lx-p), max(0, ly-p), min(width, rx+p), min(height, ry+p))
        sprite = img_large.crop(crop_bbox)
        sprite.save(os.path.join(output_dir, f"{label}.png"))

    print(f"Final Count: {len(refined_bboxes)} icons saved to {output_dir}")

if __name__ == "__main__":
    img_path = r'C:/Users/SSAFY/.gemini/antigravity/brain/49d9dcfd-19a8-4d5a-be33-ccb365a2ba90/uploaded_image_1766385808485.png'
    out_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    upscale_and_split_perfect(img_path, out_dir)
