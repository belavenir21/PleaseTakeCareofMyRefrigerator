-- 숙주의 image_url을 콩나물.png로 업데이트
UPDATE ingredient_master 
SET image_url = '/media/ingredient_icons/콩나물.png',
    icon = '🌱'
WHERE name IN ('숙주', '숙주나물');

-- 확인
SELECT name, icon, image_url FROM ingredient_master WHERE name IN ('숙주', '숙주나물');
