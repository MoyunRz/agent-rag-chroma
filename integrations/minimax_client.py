"""MiniMax Chat API 封装."""
import logging

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class MiniMaxError(Exception):
    """MiniMax API 错误."""
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f'MiniMax {code}: {msg}')


class MiniMaxClient:
    def __init__(self):
        cfg = settings.MINIMAX_CONFIG
        self.api_key = cfg['api_key']
        self.base_url = cfg['base_url'].rstrip('/')
        self.chat_model = cfg['chat_model']

    def _headers(self) -> dict:
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    def _check_error(self, data: dict):
        br = data.get('base_resp')
        if br and br.get('status_code') != 0:
            raise MiniMaxError(br['status_code'], br.get('status_msg', ''))

    def chat(self, messages: list[dict], stream: bool = False) -> str:
        """对话补全，返回模型回复文本（自动去除 M2 系列的 <think> 标签）."""
        resp = requests.post(
            f'{self.base_url}/v1/chat/completions',
            headers=self._headers(),
            json={'model': self.chat_model, 'messages': messages, 'stream': stream},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        self._check_error(data)
        if 'choices' in data:
            content = data['choices'][0]['message']['content']
            return self._strip_think(content)
        if 'reply' in data:
            return self._strip_think(data['reply'])
        raise KeyError(f'无法解析 chat 响应，keys: {list(data.keys())}')

    @staticmethod
    def _strip_think(text: str) -> str:
        """去除 M2 推理模型的 <think>...</think> 标签."""
        import re
        return re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL).strip()
