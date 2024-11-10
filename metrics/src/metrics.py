import os
import json
import aio_pika
import asyncio
import aiofiles


# Путь к файлу для логирования метрик
log_file_path = '/app/logs/metric_log.csv'

# Создаем директорию для логов, если она не существует
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Инициализируем файл CSV и записываем заголовки, если файл не существует
if not os.path.isfile(log_file_path):
    with open(log_file_path, 'w') as f:
        f.write('id,y_true,y_pred,absolute_error\n')

# Словарь для хранения значений y_true и y_pred
metrics = {}


def calculate_absolute_error(y_true, y_pred):
    return abs(y_true - y_pred)


async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        # Декодируем сообщение
        message_data = json.loads(message.body)
        message_id = message_data['id']
        print(f'Для очереди {message.routing_key} сообщение {message_data}')
        print(f'metrics is {metrics}')

        if message.routing_key == 'y_true':
            metrics[message_id] = {'y_true': message_data['body'], 'y_pred': None}
        elif message.routing_key == 'y_pred':
            if message_id in metrics:
                metrics[message_id]['y_pred'] = message_data['body']
                y_true = metrics[message_id]['y_true']
                y_pred = metrics[message_id]['y_pred']

                # Вычисляем абсолютную ошибку
                absolute_error = calculate_absolute_error(y_true, y_pred)

                # Записываем данные в CSV файл
                async with aiofiles.open(log_file_path, 'a') as f:
                    await f.write(f'{message_id},{y_true},{y_pred},{absolute_error}\n')

                # Удаляем запись из словаря, чтобы избежать повторной обработки
                del metrics[message_id]

        print(f'Из очереди {message.routing_key} получено значение {message_data}')


async def listen_queues():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    async with connection:
        channel = await connection.channel()  # Создаем канал

        queue1 = await channel.declare_queue("y_true", durable=False)
        queue2 = await channel.declare_queue("y_pred", durable=False)

        await queue1.consume(callback)
        await queue2.consume(callback)

        print("Listening on queue1 and queue2...")
        await asyncio.Future()  # Бесконечный цикл

# Запускаем асинхронный цикл
asyncio.run(listen_queues())