from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.common.status_constants import StatusConstants
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData
from src.infrastructure.clients.fb_checker import FbChecker


class QProcessCheckLiveAccount(QThread):
    q_process_response_signal = pyqtSignal(object)

    def __init__(self, select_rows):
        super().__init__()
        self.select_rows = select_rows
        self.max_workers = 50

    def check_live_uid(self, id_source: str, c_user: str):
        # Emit "checking" state
        self.q_process_response_signal.emit(TableWidgetPayloadData(
            id_source=id_source,
            account_status=StatusConstants.ACCOUNT_STATUS_CHECKING
        ))

        # Check live
        account_status = FbChecker().check_uid(fb_uid=c_user)

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
                id_source, c_user = item_part[0], item_part[1]
                future = executor.submit(self.check_live_uid, id_source, c_user)
                futures.append(future)

            for future in as_completed(futures):
                # We don't need the result, but this ensures exceptions inside threads are raised
                try:
                    future.result()
                except Exception as e:
                    print(f"[CheckLiveAccount] Error: {e}")
