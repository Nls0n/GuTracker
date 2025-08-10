import requests

response = requests.get('https://lk.gubkin.ru/new//api/api.php?module=study&resource=Performance&method=getPerformance&studentId=152558-1', cookies={'PHPSESSID': 'usm7n7cf7fg4kb53kjnli3m2r2'})

print(response.json())