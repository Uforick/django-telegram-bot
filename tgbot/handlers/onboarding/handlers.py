import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command, make_keyboard_for_choice_cycle_in_trenning
from tgbot.handlers.onboarding.manage_data import TRENING_BUTTON, CYCLE_BUTTON, WEEK_BUTTON, DAY_BUTTON


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    u = User.get_user(update, context)

    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(u))


def cycle_after_trening(update: Update, context: CallbackContext) -> None:
    #
    query = update.callback_query
    trening_in_button = query.data
    query.answer()
    
    name = trening_in_button.replace('TRN_CH ', '')
    text = static_text.choise_trening.format(name_trening=name)
    # text = f"{update.message.text.replace(f'{TRENING_BUTTON} ', '')}"
    
    query.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_choice_cycle_in_trenning(name),
        )