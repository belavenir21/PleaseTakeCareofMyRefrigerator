from PIL import Image
import os

def split_icons_pillow(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    pix = img.load()

    visited = set()
    icons = []

    print(f"Analyzing image {width}x{height}...")

    # 투명하지 않은 픽셀들을 찾아 그룹화 (간단한 BFS)
    for y in range(height):
        for x in range(width):
            if pix[x, y][3] > 0 and (x, y) not in visited:
                # 새로운 아이콘 발견
                stack = [(x, y)]
                visited.add((x, y))
                
                min_x, min_y = x, y
                max_x, max_y = x, y
                
                while stack:
                    cx, cy = stack.pop()
                    min_x, min_y = min(min_x, cx), min(min_y, cy)
                    max_x, max_y = max(max_x, cx), max(max_y, cy)
                    
                    # 주변 8방향 탐색
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if pix[nx, ny][3] > 0 and (nx, ny) not in visited:
                                    visited.add((nx, ny))
                                    stack.append((nx, ny))
                
                # 너무 작지 않은 경우만 저장 (노이즈 방지)
                if (max_x - min_x) > 5 and (max_y - min_y) > 5:
                    icons.append((min_x, min_y, max_x, max_y))

    # 좌표 순서대로 정렬 (y 먼저, 그 다음 x)
    icons.sort(key=lambda b: (b[1] // 50, b[0]))

    print(f"Detected {len(icons)} icons. Saving...")

    for i, bbox in enumerate(icons):
        # 여백 포함 크롭
        p = 2
        crop_bbox = (max(0, bbox[0]-p), max(0, bbox[1]-p), min(width, bbox[2]+p), min(height, bbox[3]+p))
        sprite = img.crop(crop_bbox)
        sprite.save(os.path.join(output_dir, f"icon_{i:03d}.png"))

    print(f"Successfully saved {len(icons)} icons to {output_dir}")

if __name__ == "__main__":
    img_path = r'C:/Users/SSAFY/.gemini/antigravity/brain/49d9dcfd-19a8-4d5a-be33-ccb365a2ba90/uploaded_image_1766382388783.png'
    out_dir = r'c:/Users/SSAFY/Desktop/PleaseTakeCareofMyRefrigerator/backend/media/ingredient_icons'
    split_icons_pillow(img_path, out_dir)
