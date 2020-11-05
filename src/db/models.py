import logging

from src.db.manager import DatabaseManager
from src.utils.utils import get_numbers

@DatabaseManager.collection('telegram_id', 'is_admin', 'is_blocked')
class User:

    def can_participate_in_another_raffle(self):
        raffles_count = len(Number.documents.distinct({'user_id': self.telegram_id}, 'raffle_id'))
        logging.info(f'[MODEL can_participate_in_another_raffle] raffles_count - {raffles_count}')
        return raffles_count < 2

    def can_take_number(self, raffle_id):
        numbers_count = self.numbers_in_raffle(raffle_id)
        logging.info(f'[MODEL can_take_number] numbers_count - {numbers_count}')
        return numbers_count < 2

    def numbers_in_raffle(self, raffle_id):
        return Number.documents.count({'raffle_id': raffle_id, 'user_id': self.telegram_id})

    def get_number_in_raffle(self, raffle_id):
        return get_numbers({'raffle_id': raffle_id, 'user_id': self.telegram_id})

    def in_raffle(self, raffle_id):
        return self.numbers_in_raffle(raffle_id) > 0

    def get_raffles(self):
        raffles_id = Number.documents.distinct({'user_id': self.telegram_id}, 'raffle_id')
        logging.info(f'[MODEL get_raffles] raffles_id - {raffles_id}')
        return [Raffle.documents.get(raffle_id) for raffle_id in raffles_id]


@DatabaseManager.collection('name', 'description', 'photo', 'is_open', 'max_numbers')
class Raffle:

    def taken_numbers(self):
        numbers = get_numbers({'raffle_id': str(self._id)})
        logging.info(f'[MODEL taken_numbers] numbers - {numbers}')
        return numbers

    def available_numbers(self):
        taken_numbers = set(self.taken_numbers())
        logging.info(f'[MODEL available_numbers] taken_numbers - {taken_numbers}')
        all_numbers = set(range(1, self.max_numbers + 1))
        return all_numbers - taken_numbers

    def taken_numbers_count(self):
        return len(self.taken_numbers())

    def __str__(self):
        return f'{self._id} - {self.name} ({self.max_numbers})'


@DatabaseManager.collection('user_id', 'raffle_id', 'number')
class Number:
    def __str__(self):
        return f'Number ({self.number})'