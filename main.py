from PIL import Image
import numpy as np
import concurrent.futures

# Функция для нахождения ближайшего цвета в палитре
def find_nearest_color(color, palette):
    return min(palette, key=lambda x: np.linalg.norm(np.array(color) - np.array(x)))

# Функция для проверки цвета на соответствие условиям
def check_color_condition(color, base_color_id, threshold=220):
    base_color_id = base_color_id * 4 + 1
    return np.linalg.norm(np.array(color) - np.array(palette[base_color_id])) > threshold

# Функция для преобразования пикселя изображения
def process_pixel(x, y, pixels, palette, base_color_id, threshold=220):
    pixel_color = pixels[x, y]
    nearest_color = find_nearest_color(pixel_color, palette)
    pixels[x, y] = nearest_color
    if check_color_condition(nearest_color, base_color_id, threshold):
        return (0, 255, 0) # Затемненный цвет
    return nearest_color

# Загрузка палитры из файла
palette = []
with open('map_colors.txt', 'r') as f:
    for line in f:
        color = tuple(int(line[i:i+2], 16) for i in (0, 2, 4))
        palette.append(color)

# Загрузка изображения
image = Image.open('texture.png')
image = image.convert('RGB')

# Преобразование изображения с использованием многопоточности
width, height = image.size
pixels = image.load()
new_image = Image.new('RGB', (width, height)) # Создание нового изображения

base_color_id = 3 # Пример Base Color ID = 3
threshold = 220 # Затемненный цвет

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(process_pixel, x, y, pixels, palette, base_color_id, threshold): (x, y) for x in range(width) for y in range(height)}

    # Ожидание завершения всех потоков
    for future in concurrent.futures.as_completed(futures):
        x, y = futures[future]
        new_color = future.result()
        new_image.putpixel((x, y), new_color)

# Сохранение результата
image.save('converted_texture.png')
new_image.save('darkened_pixels.png')
