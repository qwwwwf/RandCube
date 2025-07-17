from aiogram.fsm.state import StatesGroup, State


class ChangeParams(StatesGroup):
    generation_count_number = State()
    generation_count_password = State()
    allowable_values = State()
    change_password_size = State()


class GetData(StatesGroup):
    get_file = State()
    post_url = State()
    event_key = State()
    event_creation = State()
    edit_event_description = State()
