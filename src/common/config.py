import os
import sys


def get_project_root(current_file_path: str, levels_up: int) -> str:
    """
    Xác định thư mục gốc của dự án, có tính đến việc đóng gói bằng PyInstaller.

    Args:
        current_file_path: Đường dẫn tuyệt đối của tệp hiện tại (sử dụng __file__).
        levels_up: Số cấp thư mục cần quay lên từ vị trí tệp hiện tại để đạt đến thư mục gốc.

    Returns:
        Đường dẫn tuyệt đối đến thư mục gốc của dự án.
    """
    if getattr(sys, 'frozen', False):
        # 1. Nếu đang chạy EXE (đã đóng gói bằng PyInstaller):
        #    Thư mục gốc là thư mục chứa tệp EXE.
        return os.path.dirname(sys.executable)
    else:
        # 2. Nếu đang chạy trong môi trường phát triển (Dev):
        #    Tính toán thư mục gốc dựa trên vị trí tệp hiện tại.

        # Lấy thư mục chứa tệp hiện tại
        current_dir = os.path.dirname(os.path.abspath(current_file_path))

        # Quay lên theo số cấp đã cho
        path_components = [".."] * levels_up

        return os.path.abspath(os.path.join(current_dir, *path_components))


development_mode = True

PROJECT_ROOT = get_project_root(__file__, 2)
data_dir = os.path.join(PROJECT_ROOT, 'data')
language_dir = os.path.join(data_dir, 'languages')
log_dir = os.path.join(PROJECT_ROOT, 'data', 'logs')
icon_dir = os.path.join(PROJECT_ROOT, 'data', '.icons')
cache_dir = os.path.join(data_dir, 'cache')
contact_list_dir = os.path.join(PROJECT_ROOT, 'contact_list.txt')
max_country_scores_file = os.path.join(log_dir, 'max_country_scores.json')
