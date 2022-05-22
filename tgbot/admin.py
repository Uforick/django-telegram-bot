from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dtb.settings import DEBUG

from tgbot.models import (
    User,
    Exercise,
    TreningDay,
    TreningWeek,
    Cycle,
    Trening,
    AddCycleInTrening,
    AddWeekInCycle,
    AddTreningdayInWeek,
    AddExerciseInTreningDay,
)
from tgbot.forms import BroadcastForm

from tgbot.tasks import broadcast_message
from tgbot.handlers.broadcast_message.utils import _send_message


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id', 'username', 'first_name', 'last_name', 
        'language_code', 'deep_link',
        'created_at', 'updated_at', "is_blocked_bot",
    ]
    list_filter = ["is_blocked_bot", ]
    search_fields = ('username', 'user_id')

    actions = ['broadcast']

    def broadcast(self, request, queryset):
        """ Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        user_ids = queryset.values_list('user_id', flat=True).distinct().iterator()
        if 'apply' in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            if DEBUG:  # for test / debug purposes - run in same thread
                for user_id in user_ids:
                    _send_message(
                        user_id=user_id,
                        text=broadcast_message_text,
                    )
                self.message_user(request, f"Just broadcasted to {len(queryset)} users")
            else:
                broadcast_message.delay(text=broadcast_message_text, user_ids=list(user_ids))
                self.message_user(request, f"Broadcasting of {len(queryset)} messages has been started")

            return HttpResponseRedirect(request.get_full_path())
        else:
            form = BroadcastForm(initial={'_selected_action': user_ids})
            return render(
                request, "admin/broadcast_message.html", {'form': form, 'title': u'Broadcast message'}
            )


class AddExerciseInTreningDayAdmin(admin.TabularInline):
    model = AddExerciseInTreningDay


class AddTreningdayInWeekAdmin(admin.TabularInline):
    model = AddTreningdayInWeek


class AddWeekInCycleAdmin(admin.TabularInline):
    model = AddWeekInCycle


class AddCycleInTreningAdmin(admin.TabularInline):
    model = AddCycleInTrening


@admin.register(TreningDay)
class TreningDayAdmin(admin.ModelAdmin):
    list_display = ('admin_name', )
    search_fields = ('admin_name', )
    empty_value_display = '-пусто-'
    inlines = [AddExerciseInTreningDayAdmin]


@admin.register(TreningWeek)
class TreningWeekAdmin(admin.ModelAdmin):
    list_display = ('admin_name', )
    search_fields = ('admin_name', )
    empty_value_display = '-пусто-'
    inlines = [AddTreningdayInWeekAdmin]


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('admin_name', )
    search_fields = ('admin_name', )
    empty_value_display = '-пусто-'
    inlines = [AddWeekInCycleAdmin]


@admin.register(Trening)
class TreningAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    empty_value_display = '-пусто-'
    inlines = [AddCycleInTreningAdmin]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_discription', 'long_discription', 'representation')
    search_fields = ('name', )
    empty_value_display = '-пусто-'