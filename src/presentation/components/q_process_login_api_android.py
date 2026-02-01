from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.common.status_constants import StatusConstants
from src.domain.dtos.fb_katana_login_payload import FbKatanaLoginPayload
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.infrastructure.clients.fb_checker import FbChecker
from src.workers.method_worker_main import MethodWorkerMain


class QProcessLoginApiAndroid(QThread):
    q_process_response_signal = pyqtSignal(object)

    def __init__(self, select_rows):
        super().__init__()
        self.select_rows = select_rows
        self.max_workers = 50

    def login_api_android(self, id_source: str, fb_user_name: str, fb_password: str, fb_two_factor: str):
        # Emit "checking" state
        self.q_process_response_signal.emit(TableWidgetPayloadData(
            id_source=id_source,
            account_status=StatusConstants.ACCOUNT_STATUS_CHECKING
        ))

        main_worker = MethodWorkerMain(

        )

        status = (
            StatusConstants.ACCOUNT_LIVE if account_status is True else
            StatusConstants.ACCOUNT_DISABLED if account_status is False else
            StatusConstants.EXCEPTION_ERROR
        )

        # Emit final status
        self.q_process_response_signal.emit(TableWidgetPayloadData(
            id_source=id_source,
            account_status=status
        ))

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for item in self.select_rows:
                item_part = str(item).split('|')
                id_source, fb_user_name, fb_password, fb_two_factor = item_part[0], item_part[1], item_part[2], item_part[3]
                future = executor.submit(self.login_api_android, id_source, fb_user_name, fb_password, fb_two_factor)
                futures.append(future)

            for future in as_completed(futures):
                # We don't need the result, but this ensures exceptions inside threads are raised
                try:
                    future.result()
                except Exception as e:
                    print(f"[CheckLiveAccount] Error: {e}")
