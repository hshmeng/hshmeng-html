import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def save_avatar(file):
    filename = secure_filename(file.filename)
    # 使用 UUID 防止文件名冲突
    unique_filename = str(uuid.uuid4()) + "_" + filename
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
    return unique_filename
