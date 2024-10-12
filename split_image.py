import random

import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import Voronoi


def generate_voronoi_diagram(width, height, num_points):
    points = np.array(
        [
            (random.randint(0, width), random.randint(0, height))
            for _ in range(num_points)
        ]
    )
    vor = Voronoi(points)
    return vor


def create_jagged_line(start, end, jaggedness=10, num_points=50):
    x1, y1 = start
    x2, y2 = end

    # 直線に沿って均等に点を配置
    t = np.linspace(0, 1, num_points)
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)

    # ランダムな変位を追加
    x += np.random.normal(0, jaggedness, num_points)
    y += np.random.normal(0, jaggedness, num_points)

    return list(zip(x, y))


def create_torn_paper_effect(
    image_path, num_segments=20, edge_roughness=10, jaggedness=5
):
    # 画像を読み込む
    img = Image.open(image_path)
    width, height = img.size

    # ボロノイ図を生成
    vor = generate_voronoi_diagram(width, height, num_segments)

    # 各領域を分割して処理
    segments = []
    for region in vor.regions:
        if not -1 in region and len(region) > 0:
            polygon = [vor.vertices[i] for i in region]

            # ジャギーな輪郭を作成
            jagged_polygon = []
            for i in range(len(polygon)):
                start = polygon[i]
                end = polygon[(i + 1) % len(polygon)]
                jagged_line = create_jagged_line(start, end, jaggedness)
                jagged_polygon.extend(jagged_line)

            # 多角形のマスクを作成
            mask = Image.new("L", (width, height), 0)
            ImageDraw.Draw(mask).polygon(jagged_polygon, outline=1, fill=1)

            # マスクを使って画像を切り抜く
            segment = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            segment.paste(img, (0, 0), mask)

            # エッジ効果を適用
            draw = ImageDraw.Draw(segment)
            for x, y in jagged_polygon:
                if random.random() < 0.3:  # 30%の確率でエッジ効果を適用
                    r = random.randint(1, edge_roughness)
                    color = (0, 0, 0, random.randint(0, 100))  # 半透明の黒
                    draw.ellipse(
                        (x - r, y - r, x + r, y + r), fill=color, outline=color
                    )

            segments.append(segment)

    # 全てのセグメントを合成
    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for segment in segments:
        result = Image.alpha_composite(result, segment)

    return result


# 使用例
input_image_path = "chatdev.png"
output_image = create_torn_paper_effect(
    input_image_path, num_segments=30, edge_roughness=8, jaggedness=7
)
output_image.save("split.png")
