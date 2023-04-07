# -*- encoding: utf-8 -*-

"""定义 Http Response 要包含的字段信息
"""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ResponseEntity(object):
    """ResponseEntity 用于规范所有 http 响应的数据格式"""

    # 业务层面的消息
    message: str = None

    # 代码层面的异常消息
    error: str = None

    # 返回的数据
    data: Any = None

    def to_dict(self):
        return asdict(self)
