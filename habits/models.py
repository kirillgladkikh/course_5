from datetime import timedelta

from django.core.validators import MaxValueValidator
from django.db.models import (CASCADE, SET_NULL, BooleanField, CharField, DurationField, ForeignKey, Model,
                              PositiveIntegerField, TimeField)

from config.settings import AUTH_USER_MODEL


class Habit(Model):
    habit_name = CharField(
        max_length=255,
        verbose_name="Название полезной привычки",
        help_text="Краткое название полезной привычки (например, «Утренняя зарядка»)",
    )
    place = CharField(
        max_length=255,
        verbose_name="Место",
        help_text="Где вы будете выполнять привычку (например, «Дома», «В парке», «Офис»)",
    )
    time = TimeField(
        verbose_name="Время выполнения", help_text="Время дня, когда вы планируете выполнять привычку (формат ЧЧ:ММ)"
    )
    action = CharField(
        max_length=255,
        verbose_name="Действие",
        help_text="Конкретное действие, которое нужно выполнить (например, «Пробежать 1 км», «Прочитать 10 страниц»)",
    )
    is_pleasant = BooleanField(
        default=True,
        verbose_name="Признак приятной привычки",
        help_text="Отметьте, если привычка приятная, а не полезная",
    )
    related_habit = ForeignKey(
        "self",
        on_delete=SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная привычка",
        help_text=(
            "Выберите привычку (не обязательно), которая будет триггером для этой "
            "(например, после «Чистка зубов» → «Медитация»)"
        ),
    )
    period = PositiveIntegerField(
        verbose_name="Период выполнения (в днях)",
        default=1,
        help_text="Периодичность выполнения в днях (1 — ежедневно, 2 — через день, 7 — еженедельно и т.д.)",
    )
    reward = CharField(
        max_length=255,
        verbose_name="Вознаграждение",
        help_text=(
            "Что вы получите за выполнение привычки (например, «Чашка кофе», «10 минут отдыха», " "«Эпизод сериала»)"
        ),
    )
    time_to_action = DurationField(
        default=timedelta(seconds=120),
        verbose_name="Время на выполнение",
        validators=[MaxValueValidator(timedelta(seconds=120))],  # Время выполнения должно быть не больше 120 секунд.
        help_text="Максимальное время, которое вы потратите на выполнение (не более 120 секунд / 2 минут)",
    )
    is_published = BooleanField(
        default=True,
        verbose_name="Признак публичности",
        help_text="Если отмечено, привычка будет видна другим пользователям",
    )
    owner = ForeignKey(
        AUTH_USER_MODEL,
        on_delete=CASCADE,
        null=True,
        blank=True,
        verbose_name="Создатель привычки",
        help_text="Пользователь, который создал эту привычку",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["habit_name"]

    def __str__(self):
        return self.habit_name
