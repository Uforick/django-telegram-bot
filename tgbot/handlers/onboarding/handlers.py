import datetime

from django.utils import timezone
from django.shortcuts import get_object_or_404
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User, TreningDay, Exercise, AddExerciseInTreningDay
from tgbot.handlers.onboarding.keyboards import (
    make_keyboard_for_start_command,
    make_keyboard_for_choice_cycle_in_trenning,
    make_keyboard_for_choice_week_in_cycle,
    make_keyboard_for_choice_day_in_week
)
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


def week_after_cycle(update: Update, context: CallbackContext) -> None:
    #
    query = update.callback_query
    cycle_in_button = query.data
    query.answer()
    
    name = cycle_in_button.replace('CYC_CH ', '')
    text = static_text.choise_cycle.format(name_cycle=name)
    # text = f"{update.message.text.replace(f'{TRENING_BUTTON} ', '')}"
    
    query.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_choice_week_in_cycle(name),
        )

def day_after_week(update: Update, context: CallbackContext) -> None:
    #
    query = update.callback_query
    week_in_button = query.data
    query.answer()
    
    name = week_in_button.replace('WEEK_CH ', '')
    text = static_text.choise_week.format(name_week=name)
    # text = f"{update.message.text.replace(f'{TRENING_BUTTON} ', '')}"
    
    query.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_choice_day_in_week(name),
        )


def exercise_on_day(update: Update, context: CallbackContext) -> None:
    #
    texts=[]
    query = update.callback_query
    day_in_button = query.data
    query.answer()
    
    day = get_object_or_404(
        TreningDay,
        admin_name=day_in_button.replace('DAY_CH ', '')
    )
    # exercises = day.exercise.all()
    exercises = AddExerciseInTreningDay.objects.filter(trening_day=day.trening_day)
    for exercise in exercises:
        do_exercise = get_object_or_404(
                        Exercise,
                        pk=exercise.exercise.pk)
        teleg_exercise = static_text.trening_text.format(
                        exercise=do_exercise.name,
                        short_discription=do_exercise.short_discription,
                        representation=do_exercise.representation,
                        cycle=exercise.cycle,
                        amount=exercise.amount,
                        rir=exercise.rir,
        )
        texts.append(teleg_exercise)
    for text in texts:
        query.message.reply_text(text=text)
