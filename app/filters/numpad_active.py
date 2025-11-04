from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram import types


class NumpadActive(BaseFilter):
    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        data = await state.get_data()
        return bool(data.get("numpad_active"))


class NumpadActiveCallback(BaseFilter):
    async def __call__(self, query: types.CallbackQuery, state: FSMContext) -> bool:
        data = await state.get_data()
        return bool(data.get("numpad_active"))
