from aiogram.fsm.state import StatesGroup, State


class Order(StatesGroup):
    getting_phone = State()
    writing_start_address = State()
    writing_destination_address = State()
    writing_note = State()
    confirmation = State()
    # waiting_for_operator = State()


class Conversation(StatesGroup):
    conversation = State()
