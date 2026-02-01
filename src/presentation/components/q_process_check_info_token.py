from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.common.logger import logger
from src.common.status_constants import StatusConstants
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.infrastructure.clients.fb_checker import FbChecker


class QProcesCheckInfoToken(QThread):
    q_process_response_signal = pyqtSignal(object)

    def __init__(self, select_rows):
        super().__init__()
        self.select_rows = select_rows
        self.max_workers = 50

    def check_info_token(self, id_source: str, fb_uid: str, fb_access_token: str):
        """Kiểm tra token Facebook và emit trạng thái tương ứng."""
        emit = self.q_process_response_signal.emit

        # Emit trạng thái "checking"
        emit(TableWidgetPayloadData(
            id_source=id_source,
            status=StatusConstants.ACCOUNT_STATUS_CHECKING
        ))

        # Kiểm tra token rỗng / không hợp lệ
        if not fb_access_token:
            emit(TableWidgetPayloadData(
                id_source=id_source,
                status=StatusConstants.REQUIRES_FB_KATANA_TOKEN,
                account_status=StatusConstants.UNKNOWN
            ))
            return

        # Gọi API check token
        checker = FbChecker()
        token_data = checker.check_token(fb_uid=fb_uid, fb_access_token=fb_access_token)

        # Nếu token lỗi → emit và return
        if not token_data.token_status:
            emit(TableWidgetPayloadData(
                id_source=id_source,
                account_status=StatusConstants.UNKNOWN,
                status=token_data.status
            ))
            return

        # Emit kết quả cuối cùng (token live)
        emit(TableWidgetPayloadData(
            id_source=id_source,
            fullname=token_data.fullname,
            is_verified=StatusConstants.VERIFIED if bool(token_data.fullname) else StatusConstants.UNKNOWN,
            account_status=token_data.account_status,
            status=StatusConstants.TASK_COMPLETED
        ))

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for item in self.select_rows:
                item_part = str(item).split('|')
                id_source, fb_uid, fb_access_token = item_part[0], item_part[1], item_part[5]
                future = executor.submit(self.check_info_token, id_source, fb_uid, fb_access_token)
                futures.append(future)

            for future in as_completed(futures):
                # We don't need the result, but this ensures exceptions inside threads are raised
                try:
                    future.result()
                except Exception as e:
                    logger.error(e)
