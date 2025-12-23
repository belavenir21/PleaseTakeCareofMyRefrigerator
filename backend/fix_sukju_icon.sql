-- 숙주의 image_url을 콩나물 이미지로 업데이트
UPDATE master_ingredientmaster
SET image_url = 'ingredient_icons/콩나물.png'
WHERE name = '숙주';
