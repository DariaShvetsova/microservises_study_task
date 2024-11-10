import pika
import pickle
import numpy as np
import json

# Создаём подключение по адресу rabbitmq:
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', credentials=credentials))
channel = connection.channel()

# Объявляем очередь features
channel.queue_declare(queue='features')
# Объявляем очередь y_pred
channel.queue_declare(queue='y_pred')

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

# Создаём функцию callback для обработки данных из очереди
def callback(ch, method, properties, body):
    print(f'Получен вектор признаков {body}')
    features = json.loads(body)
    mid = features['id']
    replay = {}
    replay['id'] = mid
    pred = regressor.predict(np.array(features['body']).reshape(1, -1))
    replay['body'] = pred[0]
    channel.basic_publish(exchange='',
                          routing_key='y_pred',
                          body=json.dumps(replay))
    print(f'Предсказание {replay} отправлено в очередь y_pred')

try:

    # Извлекаем сообщение из очереди features

    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')

    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except Exception as e:
    print(f'Не удалось подключиться к очереди {e}')