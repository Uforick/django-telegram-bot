from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager


#Block related to training bot
#Scheme: training course - training cycles - training weeks - training days - exercises
class Exercise(models.Model):
    # Упражнение
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
    )
    short_discription = models.TextField(
        verbose_name='Короткое описание',
        help_text='Короткое описание для напоминания',
        null=True,
        blank=True,
    )
    long_discription = models.TextField(
        verbose_name='Подробное описание',
        help_text='Подробное описание для понимания',
        null=True,
        blank=True,
    )
    representation = models.TextField(
        verbose_name='Ссылка на видео',
        help_text='Ссылка на видео упражнения',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Упражнение'
        verbose_name_plural = 'Упражнения'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class TreningDay(models.Model):
    # Тренировачные дни в неделе
    admin_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название для тренера',
    )
    user_name = models.CharField(
        max_length=255,
        verbose_name='Название для клиента',
        default='None',
    )
    exercise = models.ManyToManyField(
        Exercise,
        through='AddExerciseInTreningDay',
        related_name='exercises',
        verbose_name='Упражнения',
    )

    class Meta:
        verbose_name = 'Тренировачный день'
        verbose_name_plural = 'Тренировачные дни'
        ordering = ('-admin_name',)

    def __str__(self):
        return self.admin_name


class TreningWeek(models.Model):
    #Недели в циклих
    admin_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название для тренера',
    )
    user_name = models.CharField(
        max_length=255,
        verbose_name='Название для клиента',
        default='None',
    )
    trening_day = models.ManyToManyField(
        TreningDay,
        through='AddTreningdayInWeek',
        related_name='trening_days',
        verbose_name='Тренировачный день',
    )

    class Meta:
        verbose_name = 'Тренировачная неделя'
        verbose_name_plural = 'Тренировачные недели'
        ordering = ('-admin_name',)

    def __str__(self):
        return self.admin_name


class Cycle(models.Model):
    # Циклы в курсах тренировок
    admin_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название для тренера',
    )
    user_name = models.CharField(
        max_length=255,
        verbose_name='Название для клиента',
        default='None',
    )
    week = models.ManyToManyField(
        TreningWeek,
        through='AddWeekInCycle',
        related_name='weeks',
        verbose_name='Неделя',
    )

    class Meta:
        verbose_name = 'Цикл'
        verbose_name_plural = 'Циклы'
        ordering = ('-admin_name',)

    def __str__(self):
        return self.admin_name


class Trening(models.Model):
    # Курсы тренировок
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
    )
    cycle = models.ManyToManyField(
        Cycle,
        through='AddCycleInTrening',
        related_name='cycle',
        verbose_name='Цикл',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class AddCycleInTrening(models.Model):
    # Добавление циклов в курс тренировок
    trening = models.ForeignKey(
        Trening,
        on_delete=models.CASCADE,
    )
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Добавление цикла в курс'
        verbose_name_plural = 'Добавление цикла в курс'
        constraints = [
            models.UniqueConstraint(
                fields=['trening', 'cycle'],
                name='cycle_in_trening'
            )
        ]

    def __str__(self):
        return f'{self.trening} {self.cycle}'


class AddWeekInCycle(models.Model):
    # Добавление недель в циклы
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.CASCADE,
    )
    week = models.ForeignKey(
        TreningWeek,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Добавление недели в цикл'
        verbose_name_plural = 'Добавление недели в цикл'
        constraints = [
            models.UniqueConstraint(
                fields=['cycle', 'week'],
                name='week_in_cycle'
            )
        ]

    def __str__(self):
        return f'{self.cycle} {self.week}'


class AddTreningdayInWeek(models.Model):
    # Добавление тренировачных дней в недели
    week = models.ForeignKey(
        TreningWeek,
        on_delete=models.CASCADE,
    )
    trening_day = models.ForeignKey(
        TreningDay,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Добавление тренировачных дней в неделю'
        verbose_name_plural = 'Добавление тренировачных дней в неделю'
        constraints = [
            models.UniqueConstraint(
                fields=['week', 'trening_day'],
                name='treining_in_week'
            )
        ]

    def __str__(self):
        return f'{self.week} {self.trening_day}'


class AddExerciseInTreningDay(models.Model):
    # Добавление упражнений в тренировачный день
    trening_day = models.ForeignKey(
        TreningDay,
        on_delete=models.CASCADE,
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
    )
    cycle = models.IntegerField(
        verbose_name='Количество подходов',
        null=True,
        blank=True,
    )
    amount = models.IntegerField(
        verbose_name='Количество повторений',
        null=True,
        blank=True,
    )
    rir = models.IntegerField(
        verbose_name='Субъективный уровень нагрузки',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Добавление упражнений в тренировачных день'
        verbose_name_plural = 'Добавление упражнений в тренировачных день'
        constraints = [
            models.UniqueConstraint(
                fields=['trening_day', 'exercise'],
                name='trening_day_exercise_unique'
            )
        ]

    def __str__(self):
        return f'{self.trening_day} {self.exercise}'


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)

def default_trening():
    return Trening.objects.get(pk=1)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)

    is_blocked_bot = models.BooleanField(default=False)

    is_admin = models.BooleanField(default=False)

    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()
    available_training = models.ManyToManyField(
        Trening,
        related_name='user',
        verbose_name='Доступные тренировки',
        default=default_trening, #тестовая строка, расскоментировать после создания первого тренинка
    )
    
    

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"
