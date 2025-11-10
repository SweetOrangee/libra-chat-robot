import os
from pathlib import Path
from PIL import Image

def generate_reversed_tarot_images(img_dir: str) -> None:
    """
    批量生成塔罗牌逆位图片（旋转180度）
    :param img_dir: 塔罗牌原图目录路径
    """
    # 检查目录是否存在
    img_path = Path(img_dir)
    if not img_path.exists():
        print(f"错误：目录不存在 → {img_dir}")
        return

    # 获取目录下所有图片文件（支持常见格式）
    img_extensions = (".jpg", ".jpeg", ".png", ".gif")
    img_files = [f for f in os.listdir(img_dir) if f.lower().endswith(img_extensions)]

    if not img_files:
        print(f"警告：目录下未找到图片文件 → {img_dir}")
        return

    # 批量处理图片
    for idx, filename in enumerate(img_files, 1):
        # 原图路径
        original_path = img_path / filename
        # 逆位图片路径（前缀加 'r'）
        reversed_filename = f"r{filename}"
        reversed_path = img_path / reversed_filename

        try:
            # 打开图片并旋转180度
            with Image.open(original_path) as img:
                # 旋转180度，保持图片尺寸和EXIF信息
                reversed_img = img.rotate(180, expand=False)
                # 保存逆位图片（覆盖已存在的文件）
                reversed_img.save(reversed_path)
            print(f"✅ 处理成功 [{idx}/{len(img_files)}]：{filename} → {reversed_filename}")
        except Exception as e:
            print(f"❌ 处理失败 [{idx}/{len(img_files)}]：{filename} → 错误：{str(e)}")

if __name__ == "__main__":
    # -------------------------- 配置参数 --------------------------
    # 替换为你的塔罗牌图片目录路径（绝对路径或相对路径）
    TAROT_IMG_DIR = "/home/admin/libra_robot/tarot/tarot-json-master/cards"
    # ----------------------------------------------------------------

    # 执行逆位图片生成
    print(f"开始生成逆位塔罗牌图片，目录：{TAROT_IMG_DIR}\n")
    generate_reversed_tarot_images(TAROT_IMG_DIR)
    print("\n✅ 所有图片处理完成！")