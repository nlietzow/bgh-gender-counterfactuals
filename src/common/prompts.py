"""
This module contains the prompts used in the application.
"""

from src.common import config

CREATE_CASE_INFO_SYSTEM = (
    (config.PROMPTS_DIR / "create_case_info_system.txt")
    .read_text(encoding="utf-8")
    .strip()
)

CREATE_CASE_INFO_USER = (
    (config.PROMPTS_DIR / "create_case_info_user.txt")
    .read_text(encoding="utf-8")
    .strip()
)

CREATE_AUGMENTATION_SYSTEM = (
    (config.PROMPTS_DIR / "create_augmentation_system.txt")
    .read_text(encoding="utf-8")
    .strip()
)
