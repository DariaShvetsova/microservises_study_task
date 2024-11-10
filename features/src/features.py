import pika
import numpy as np
import json
import time
from datetime import datetime
from sklearn.datasets import load_diabetes

# Загружаем датасет о диабете
X, y = load_diabetes(return_X_y=True)

# Создаём подключение по адресу rabbitmq:
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=credentials))
channel = connection.channel()

 # Создаём очередь y_true
channel.queue_declare(queue='y_true')
# Создаём очередь features
channel.queue_declare(queue='features')

# Создаём бесконечный цикл для отправки сообщений в очередь
while True:
    try:
        # Формируем случайный индекс строки
        random_row = np.random.randint(0, X.shape[0] - 1)

        # Создаём уникальный идентификатор сообщения
        message_id = datetime.timestamp(datetime.now())


        # Формируем сообщение для y_true
        message_y_true = {
            'id': message_id,
            'body': y[random_row].tolist()  # Преобразуем в список для сериализации
        }
        # Публикуем сообщение в очередь y_true
        channel.basic_publish(exchange='',
                              routing_key='y_true',
                              body=json.dumps(message_y_true))
        print('Сообщение с правильным ответом отправлено в очередь y_true:', message_y_true)

        # Формируем сообщение для features
        message_features = {
            'id': message_id,
            'body': list(X[random_row])  # Преобразуем в список для сериализации
        }
        # Публикуем сообщение в очередь features
        channel.basic_publish(exchange='',
                              routing_key='features',
                              body=json.dumps(message_features))
        print('Сообщение с вектором признаков отправлено в очередь:', message_features)


        # Задержка перед следующей итерацией
        time.sleep(10)  # Усыпляем программу на 10 секунд

    except Exception as e:
        print('Не удалось подключиться к очереди:', e)

