import base64
import io

import numpy as np
from PIL import Image


def create_mosaic(image_data, tile_size=20, max_size=800):
    # base64エンコードされた画像データをデコード
    image_data = base64.b64decode(image_data.split(",")[1])

    # 画像をPIL Imageオブジェクトとして開く
    img = Image.open(io.BytesIO(image_data))

    # 画像のリサイズ
    img.thumbnail((max_size, max_size))

    # 画像をNumPy配列に変換
    img_array = np.array(img)

    height, width, _ = img_array.shape

    # タイルサイズで画像を分割
    for y in range(0, height, tile_size):
        for x in range(0, width, tile_size):
            tile = img_array[y : y + tile_size, x : x + tile_size]

            # タイルの平均色を計算
            avg_color = np.mean(tile, axis=(0, 1))

            # タイルを平均色で塗りつぶす
            img_array[y : y + tile_size, x : x + tile_size] = avg_color

    # NumPy配列をPIL Imageオブジェクトに変換
    mosaic_img = Image.fromarray(img_array.astype("uint8"))

    # 画像をbase64エンコードされた文字列に変換
    buffered = io.BytesIO()
    mosaic_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
