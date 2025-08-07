import redis
from lk_parser import parse_grades, password

r = redis.Redis(host='localhost')

while True:
    _, user_data = r.brpop('queue:grades')
    user_id, login, password = user_data.decode().split(':')

    try:
        grades = parse_grades(login, password)
    except Exception as e:
        r.lpush(f'errors:{user_id}', str(e))
