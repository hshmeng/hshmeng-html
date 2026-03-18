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
    
    filename = secure_filename(file.filename)
    # 使用 UUID 防止文件名冲突
    unique_filename = str(uuid.uuid4()) + "_" + filename
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
    return unique_filename
