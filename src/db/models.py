from src.db.manager import DatabaseManager

@DatabaseManager.collection('telegram_id', 'is_admin', 'is_blocked')
class User:
    def can_participate_in_another_raffle(self, user_id):
        raffles_count = Number.objects.find({'user_id': user_id}).distinct('raffle_id').count_documents({})
        return raffles_count < 2

    def can_take_number(self, raffle_id, user_id):
        numbers_count = Number.objects.count_documents({'raffle_id':raffle_id, 'user_id': user_id})
        return numbers_count < 2


@DatabaseManager.collection('name', 'description', 'photo', 'is_open', 'max_number')
class Raffle:
    def available_numbers(self, raffle_id):
        numbers = Number.objects.find({'raffle_id': raffle_id}, ['number'])
        taken_numbers = set([document['number'] for document in numbers])

        max_number = Raffle.objects.find({'raffle_id': raffle_id}, ['max_number'])
        all_numbers = set([document['max_number'] for document in max_number])

        return all_numbers - taken_numbers


@DatabaseManager.collection('user_id', 'raffle_id', 'number')
class Number:
    pass