import random

import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi


def generate_voronoi_diagram(width, height, num_points):
    # 画像内にランダムな点を生成
    points = np.array(
        [
            (random.randint(0, width), random.randint(0, height))
            for _ in range(num_points)
        ]
    )

    # ボロノイ図を生成
    vor = Voronoi(points)
    return vor


def create_torn_paper_effect(image_path, num_segments: int, edge_roughness: int):
    try:
        # 画像を読み込む
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            width, height = img.size

        # ボロノイ図を生成
        vor = generate_voronoi_diagram(width, height, num_segments)

        # 各領域を分割して処理
        segments = []
        for region in vor.regions:
            if len(region) > 0:  # 空の領域をスキップ
                polygon = []
                for index in region:
                    if index == -1:
                        # 無限遠点を画像の境界に投影
                        far_point = vor.vertices[region[region.index(index) - 1]]
                        if far_point[0] < 0:
                            polygon.append((0, far_point[1]))
                        elif far_point[0] > width:
                            polygon.append((width, far_point[1]))
                        elif far_point[1] < 0:
                            polygon.append((far_point[0], 0))
                        elif far_point[1] > height:
                            polygon.append((far_point[0], height))
                    else:
                        polygon.append(vor.vertices[index])

                # 座標を整数に変換し、画像サイズ内に収める
                polygon = [
                    (max(0, min(int(x), width - 1)), max(0, min(int(y), height - 1)))
                    for x, y in polygon
                ]

                if len(polygon) > 2:  # 少なくとも3点必要
                    # 多角形のマスクを作成
                    mask = Image.new("L", (width, height), 0)
                    ImageDraw.Draw(mask).polygon(polygon, outline=255, fill=255)

                    # マスクを使って画像を切り抜く
                    segment = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    segment.paste(img, (0, 0), mask)

                    # エッジ効果を適用
                    draw = ImageDraw.Draw(segment)
                    for j in range(len(polygon)):
                        p1 = polygon[j]
                        p2 = polygon[(j + 1) % len(polygon)]
                        for _ in range(edge_roughness):
                            x = int(p1[0] + random.random() * (p2[0] - p1[0]))
                            y = int(p1[1] + random.random() * (p2[1] - p1[1]))
                            r = random.randint(1, 3)
                            draw.ellipse(
                                (x - r, y - r, x + r, y + r), fill=(0, 0, 0, 0)
                            )

                    segments.append(segment)

        # 全てのセグメントを合成
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for segment in segments:
            result = Image.alpha_composite(result, segment)

        return result

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()
        return None


# 使用例
input_image_path = "chatdev.png"
output_image = create_torn_paper_effect(
    input_image_path, num_segments=30, edge_roughness=5
)
if output_image:
    output_image.save("split.png")
    print("画像の処理が完了し、'split.png'として保存されました。")
else:
    print("画像の処理に失敗しました。")
