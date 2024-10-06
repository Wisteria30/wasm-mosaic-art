import random

def ten_print(width=179, height=56):
    characters = ["/", "\\"]
    for _ in range(height):
        print(''.join(random.choice(characters) for _ in range(width)))

# 実行
ten_print()
