from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text
from tgbot.models import Trening


def make_keyboard_for_start_command(user) -> InlineKeyboardMarkup:
    texts = []
    trening_button = []
    buttons = []
    trenings = Trening.objects.all()
    for trening in trenings:
        trening_button.append(trening)
    for spec in trening_button:
        buttons.append(
            [InlineKeyboardButton(
                text = str(spec.name),
                callback_data = str(spec.name),
            )]
        )
    # buttons = [[
    #     InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
    #     InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}')
    # ]]

    return InlineKeyboardMarkup(buttons)
