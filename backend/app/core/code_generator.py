"""
编号生成器
各类实体的编号格式：前缀 + 四位数字
"""
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# 编号前缀定义
CODE_PREFIXES = {
    "warehouse": "WH",      # 库房
    "production_line": "PL", # 产线
    "shelf": "SF",          # 货架
    "location": "LC",       # 库位
    "material_type": "MT",  # 物资类型
    "device_type": "DT",    # 设备类型
    "device": "DV",         # 设备
    "iot_device": "IOT",    # IOT设备
}

# 编号格式正则
CODE_PATTERN = re.compile(r'^([A-Z]{2,4})-(\d{4})$')


def generate_code(prefix: str, sequence: int) -> str:
    """
    生成编号
    :param prefix: 前缀
    :param sequence: 序号
    :return: 格式化的编号，如 WH-0001
    """
    return f"{prefix}-{sequence:04d}"


def validate_code(code: str, expected_prefix: str) -> bool:
    """
    验证编号格式
    :param code: 编号
    :param expected_prefix: 期望的前缀
    :return: 是否有效
    """
    match = CODE_PATTERN.match(code)
    if not match:
        return False
    prefix = match.group(1)
    return prefix == expected_prefix


def parse_code(code: str) -> tuple[str, int]:
    """
    解析编号
    :param code: 编号
    :return: (前缀, 序号)
    """
    match = CODE_PATTERN.match(code)
    if not match:
        raise ValueError(f"Invalid code format: {code}")
    return match.group(1), int(match.group(2))


async def get_next_sequence(db: AsyncSession, model, code_field: str, prefix: str) -> int:
    """
    获取下一个序号
    :param db: 数据库会话
    :param model: 模型类
    :param code_field: 编号字段名
    :param prefix: 前缀
    :return: 下一个序号
    """
    # 查询该前缀下最大的序号
    result = await db.execute(
        select(getattr(model, code_field))
        .where(getattr(model, code_field).like(f"{prefix}-%"))
        .order_by(getattr(model, code_field).desc())
        .limit(1)
    )
    last_code = result.scalar_one_or_none()
    
    if last_code:
        try:
            _, seq = parse_code(last_code)
            return seq + 1
        except ValueError:
            return 1
    return 1


async def generate_unique_code(db: AsyncSession, model, code_field: str, entity_type: str) -> str:
    """
    生成唯一编号
    :param db: 数据库会话
    :param model: 模型类
    :param code_field: 编号字段名
    :param entity_type: 实体类型（用于获取前缀）
    :return: 唯一编号
    """
    prefix = CODE_PREFIXES.get(entity_type)
    if not prefix:
        raise ValueError(f"Unknown entity type: {entity_type}")
    
    seq = await get_next_sequence(db, model, code_field, prefix)
    return generate_code(prefix, seq)
