from aiogram.fsm.state import StatesGroup, State


class StartData(StatesGroup):
    start = State()


class Order(StatesGroup):
    getting_phone = State()
    writing_start_address = State()
    writing_destination_address = State()
    writing_note = State()
    confirmation = State()
    cancel_or_keep = State()


class Conversation(StatesGroup):
    conversation = State()
