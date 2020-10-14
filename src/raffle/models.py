from mongoengine import Document
from mongoengine import fields
from mongoengine.queryset.base import CASCADE
from mongoengine.queryset.manager import queryset_manager


class User(Document):
    telegram_id = fields.IntField(primary_key=True)
    is_admin = fields.BooleanField(default=False)
    is_blocked = fields.BooleanField(default=False)

    @queryset_manager
    def admins(self, queryset):
        return queryset.filter(is_admin=True)

    @queryset_manager
    def blocked(self, queryset):
        return queryset.filter(is_blocked=True)

    def can_participate_in_another_raffle(self):
        raffles_count = Number.objects(user__telegram_id=self.telegram_id) \
                              .distict('raffle') \
                              .count()
        return raffles_count < 2

    def can_take_other_number(self, raffle_id):
        numbers_count = Number.objects(user__telegram_id=self.telegram_id,
                                       raffle__id=raffle_id).count()
        return numbers_count < 2


class Raffle(Document):
    name = fields.StringField(max_length=50)
    description = fields.StringField()
    image = fields.ImageField()
    max_numbers = fields.IntField(min_value=1)
    is_open = fields.BooleanField(default=True)

    def available_numbers(self):
        taken_numbers = set(Number.objects(raffle__id=self.id).scalar('numbers'))
        all_numbers = set(range(1, self.max_numbers + 1))
        return all_numbers - taken_numbers


class Number(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE)
    raffle = fields.ReferenceField(Raffle, reverse_delete_rule=CASCADE)
    number = fields.IntField()
