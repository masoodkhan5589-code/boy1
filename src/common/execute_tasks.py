from typing import List, Tuple, Callable, Optional, Union


def execute_tasks(
        instance,
        tasks: List[Tuple[Callable[[], bool], Optional[str]]],
        retry_message_to_match: Optional[Union[str, List[str]]] = None,
        max_retries: int = 2
) -> bool:
    i = 0
    retry_count = 0

    # Ensure retry_message_to_match is a list internally
    if retry_message_to_match is not None:
        if isinstance(retry_message_to_match, str):
            retry_messages = [retry_message_to_match]
        else:
            retry_messages = retry_message_to_match
    else:
        retry_messages = []

    while i < len(tasks):
        task, message = tasks[i]

        if message and hasattr(instance, 'update_status'):
            instance.update_status(status=message)

        result = task()

        if not result:
            return False

        # Retry logic
        if getattr(instance, 'try_again', False) and retry_messages and message in retry_messages:
            instance.try_again = False  # Reset flag to avoid infinite loop

            if retry_count < max_retries:
                retry_count += 1

                # Jump back to first matching message
                i = next(
                    (index for index, (_, msg) in enumerate(tasks)
                     if msg in retry_messages),
                    i
                )
                continue
            else:
                return False

        i += 1

    return True
