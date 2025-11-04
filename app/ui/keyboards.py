from __future__ import annotations

from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def make_numpad(
    *,
    include_mid_steps: bool = False,
    placeholder: Optional[str] = None,
) -> ReplyKeyboardMarkup:
    """Создаёт компактную цифровую клавиатуру для ввода чисел."""

    first_row = ["−10", "−1", "+1", "+10"]
    if include_mid_steps:
        first_row = ["−10", "−5", "−1", "+1", "+5", "+10"]

    keyboard = [
        [KeyboardButton(text=item) for item in first_row],
        [KeyboardButton(text=text) for text in ("1", "2", "3")],
        [KeyboardButton(text=text) for text in ("4", "5", "6")],
        [KeyboardButton(text=text) for text in ("7", "8", "9")],
        [KeyboardButton(text="0")],
        [
            KeyboardButton(text="Очистить"),
            KeyboardButton(text="Готово"),
            KeyboardButton(text="Пропустить"),
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=placeholder,
    )


def make_infusions_kb() -> InlineKeyboardMarkup:
    """Клавиатура пресетов и действий для времени проливов."""

    presets = [
        InlineKeyboardButton(text=f"{value}s", callback_data=f"inf:set:{value}")
        for value in (5, 10, 15, 20, 25, 30)
    ]

    adjustments = [
        InlineKeyboardButton(text="−5s", callback_data="inf:adj:-5"),
        InlineKeyboardButton(text="+5s", callback_data="inf:adj:5"),
    ]

    controls = [
        InlineKeyboardButton(text="Очистить", callback_data="inf:clear"),
        InlineKeyboardButton(text="Готово", callback_data="inf:done"),
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=[presets, adjustments, controls]
    )
