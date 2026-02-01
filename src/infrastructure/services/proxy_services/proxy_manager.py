import os
import uuid
import random
import threading
import time
import atexit
from collections import defaultdict
from typing import Dict, Tuple, Optional

from src.common import config
from src.common.logger import logger
from src.application.interfaces.i_proxy_manager import IProxyManager


class ProxyManager(IProxyManager):
    def __init__(self, save_interval: int = 5, release_cooldown: int = 30):
        self.lock = threading.Lock()
        self.proxies: Dict[str, str] = {}          # uid -> proxy string
        self.in_use: set[str] = set()              # uid đang được dùng
        self.country_score = defaultdict(int)      # country -> score
        self.cooldowns: Dict[str, float] = {}      # uid -> timestamp có thể dùng lại

        self.score_file = config.max_country_scores_file
        self.save_interval = save_interval
        self.release_cooldown = release_cooldown
        self.stop_event = threading.Event()

        proxy_file = os.path.join(config.data_dir, 'proxies.txt')
        self._load_proxies(proxy_file)
        self._load_scores()

        # Thread tự động save định kỳ
        self.save_thread = threading.Thread(target=self._auto_save_loop, daemon=True)
        self.save_thread.start()

        # Đảm bảo flush khi process dừng
        atexit.register(self._save_scores)

    def _load_proxies(self, proxy_file: str):
        if not os.path.exists(proxy_file):
            raise FileNotFoundError(f"Proxy file {proxy_file} not found")

        with open(proxy_file, "r", encoding="utf-8") as f:
            for line in f:
                proxy = line.strip()
                if proxy:
                    uid = str(uuid.uuid4())
                    self.proxies[uid] = proxy

    def _load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "|" in line:
                            country, score = line.strip().split("|", 1)
                            self.country_score[country] = int(score)
            except Exception as e:
                logger.warning(f"[ProxyManager] Failed to load scores: {e}")

    def _save_scores(self):
        """Lưu điểm ra file, sort giảm dần"""
        try:
            with self.lock:
                sorted_scores = sorted(
                    self.country_score.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                with open(self.score_file, "w", encoding="utf-8") as f:
                    for country, score in sorted_scores:
                        f.write(f"{country}|{score}\n")
        except Exception as e:
            logger.error(f"[ProxyManager] Failed to save scores: {e}")

    def _auto_save_loop(self):
        while not self.stop_event.is_set():
            time.sleep(self.save_interval)
            self._save_scores()

    def stop(self):
        """Dừng manager, flush dữ liệu ra file"""
        self.stop_event.set()
        self._save_scores()

    def get_proxy(self, uid: Optional[str] = None) -> Optional[Tuple[str, str]]:
        """
        Lấy proxy ngẫu nhiên hoặc theo uid.
        - Nếu uid được truyền vào: trả về proxy đó ngay lập tức (bỏ qua cooldown).
        - Nếu không: trả về proxy ngẫu nhiên khả dụng.
        """
        with self.lock:
            if uid:
                if uid not in self.proxies:
                    logger.warning(f"Proxy UID {uid} not found")
                    return None

                if uid not in self.in_use:
                    self.in_use.add(uid)

                return uid, self.proxies[uid]

            # Không truyền uid → chọn proxy khả dụng (check cooldown như cũ)
            available = [
                u for u in self.proxies
                if u not in self.in_use
                   and (u not in self.cooldowns or self.cooldowns[u] <= time.time())
            ]
            if not available:
                logger.info("No proxy available")
                return None

            chosen_uid = random.choice(available)
            self.in_use.add(chosen_uid)
            return chosen_uid, self.proxies[chosen_uid]

    def release_proxy(self, uid: str):
        with self.lock:
            if uid in self.in_use:
                self.in_use.discard(uid)
                self.cooldowns[uid] = time.time() + self.release_cooldown

    def report_result(self, uid: str, country: str, success: bool):
        with self.lock:
            if success:
                self.country_score[country] += 1
            else:
                self.country_score[country] -= 1

        # Save ra file ngoài lock để tránh deadlock
        self.release_proxy(uid)
        self._save_scores()

    def get_total(self) -> int:
        return len(self.proxies)

    def get_in_use_count(self) -> int:
        with self.lock:
            return len(self.in_use)
