from src.db.manager import DatabaseManager

@DatabaseManager.collection('telegram_id', 'is_admin', 'is_blocked')
class User:
    def can_participate_in_another_raffle(self):
        raffles_count = Number.documents.find({'user_id': self.telegram_id}).distinct('raffle_id').count_documents({})
        return raffles_count < 2

    def can_take_number(self, raffle_id):
        numbers_count = Number.documents.count_documents({'raffle_id':raffle_id, 'user_id': self.telegram_id})
        return numbers_count < 2

    def get_number_in_raffle(self, raffle_id):
        return Number.documents.values_list({'raffle_id': raffle_id, 'user_id': self.telegram_id}, 'number')

    def in_raffle(self, raffle_id):
        return len(self.get_number_in_raffle(raffle_id)) > 0


@DatabaseManager.collection('name', 'description', 'photo', 'is_open', 'max_numbers')
class Raffle:
    def taken_numbers(self):
        return Number.documents.values_list({'raffle_id': self._id}, 'number')

    def available_numbers(self):
        taken_numbers = set(self.taken_numbers())

        max_number = Raffle.documents.values_list({'raffle_id': self._id}, 'max_numbers')[0]
        all_numbers = set(range(1, max_number + 1))

        return all_numbers - taken_numbers

    def taken_numbers_count(self):
        return len(self.taken_numbers())


@DatabaseManager.collection('user_id', 'raffle_id', 'number')
class Number:
    pass