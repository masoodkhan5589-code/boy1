from src.common.logger import logger
from src.domain.dtos.table_widget_payload_data import TableWidgetPayloadData


class BaseProcess:

    def __init__(self, q_process_response_signal: callable):
        self.q_process_response_signal = q_process_response_signal
        self._table_data = TableWidgetPayloadData

    def update_proxy_status(self, id_source: str, **kwargs) -> None:
        update_dict = {"id_source": id_source}
        update_dict.update(kwargs)

        self.response_to_table_widget(self._table_data(**update_dict))

    def response_to_table_widget(self, data: TableWidgetPayloadData) -> None:
        if self.q_process_response_signal:
            self.q_process_response_signal.emit(data)
        else:
            logger.info(data.status)
