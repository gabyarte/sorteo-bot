from django.db import models

MAX_NUMBER_PER_RAFFLE = 2
MAX_NUMBER_OF_RAFFLE = 2


class User(models.Model):
    telegram_id = models.PositiveIntegerField(primary_key=True)
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def can_take_number(self, raffle_id):
        return self.numbers.filter(raffle_id=raffle_id).count() <= MAX_NUMBER_PER_RAFFLE

    def can_participate_in_another_raffle(self):
        return self.numbers.count('raflle_id') <= MAX_NUMBER_OF_RAFFLE


class Raffle(models.Model):
    product_name = models.CharField(max_length=20)
    product_description = models.TextField()
    product_photo = models.ImageField()
    max_numbers = models.PositiveSmallIntegerField(default=25)
    is_open = models.BooleanField(default=True)

    def available_numbers(self):
        taken_numbers = set(self.numbers.all().values_list('number', flat=True))
        all_numbers = set(range(1, self.max_numbers + 1))
        return all_numbers - taken_numbers


class Number(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='numbers')
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='taken_numbers')
    number = models.PositiveSmallIntegerField()
