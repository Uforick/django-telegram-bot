from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from django.shortcuts import get_object_or_404

from tgbot.handlers.onboarding.manage_data import TRENING_BUTTON, CYCLE_BUTTON, WEEK_BUTTON, DAY_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text
from tgbot.models import Trening, Cycle, TreningWeek


def make_keyboard_for_start_command(user) -> InlineKeyboardMarkup:
    trening_button = []
    buttons = []
    trenings = Trening.objects.all()
    for trening in trenings:
        if trening in user.available_training.all():
            trening_button.append(trening)
    for spec in trening_button:
        buttons.append(
            [InlineKeyboardButton(
                text = str(spec.name),
                callback_data = f'{TRENING_BUTTON} {str(spec.name)}',
            )]
        )
    # buttons = [[
    #     InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
    #     InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}')
    # ]]

    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_choice_cycle_in_trenning(name_trening):
    cycle_button = []
    buttons = []
    
    trening = get_object_or_404(
        Trening,
        name=name_trening
    )
    cycles = trening.cycle.all()
    for cycle in cycles:
        cycle_button.append(cycle)
    for spec in cycle_button:
        buttons.append(
            [InlineKeyboardButton(
                text = str(spec.admin_name),
                callback_data = f'{CYCLE_BUTTON} {str(spec.admin_name)}',
            )]
        )
    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_choice_week_in_cycle(name_cycle):
    week_button = []
    buttons = []
    
    cycle = get_object_or_404(
        Cycle,
        admin_name=name_cycle
    )
    weeks = cycle.week.all()
    for week in weeks:
        week_button.append(week)
    for spec in week_button:
        buttons.append(
            [InlineKeyboardButton(
                text = str(spec.admin_name),
                callback_data = f'{WEEK_BUTTON} {str(spec.admin_name)}',
            )]
        )
    return InlineKeyboardMarkup(buttons)


def make_keyboard_for_choice_day_in_week(name_week):
    day_button = []
    buttons = []
    
    week = get_object_or_404(
        TreningWeek,
        admin_name=name_week
    )
    days = week.trening_day.all()
    for day in days:
        day_button.append(day)
    for spec in day_button:
        buttons.append(
            [InlineKeyboardButton(
                text = str(spec.admin_name),
                callback_data = f'{DAY_BUTTON} {str(spec.admin_name)}',
            )]
        )
    return InlineKeyboardMarkup(buttons)
    
