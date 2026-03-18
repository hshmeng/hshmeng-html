import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

def validate_image(file):
    """
    检查上传的文件是否是真实的图片
    """
    try:
        # 尝试打开并验证图片
        img = Image.open(file)
        img.verify()
        # 验证后需要重新 seek(0)，因为 verify 会移动文件指针
        file.seek(0)
        return True
    except (IOError, SyntaxError):
        return False

def save_avatar(file):
    if not validate_image(file):
        return None
    
    # 提取文件扩展名
    _, ext = os.path.splitext(file.filename)
    if not ext:
        return None # 不允许没有扩展名的文件

    # 创建一个唯一的、安全的文件名
    unique_filename = str(uuid.uuid4()) + ext.lower()
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
    return unique_filename

def save_post_images(files):
    """
    保存帖子图片，限制5张以内
    """
    saved_filenames = []
    for file in files[:5]:
        if file and file.filename != '':
            if validate_image(file):
                # 提取文件扩展名
                _, ext = os.path.splitext(file.filename)
                if not ext:
                    continue # 跳过没有扩展名的文件

                # 创建一个唯一的、安全的文件名
                unique_filename = str(uuid.uuid4()) + ext.lower()
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
                saved_filenames.append(unique_filename)
    return saved_filenames
