import pandas as pd
import matplotlib.pyplot as plt
import os
import time

log_file_path = '/app/logs/metric_log.csv'
output_image_path = '/app/logs/error_distribution.png'


def plot_error_distribution():
    # Читаем данные из CSV файла
    if os.path.isfile(log_file_path):
        df = pd.read_csv(log_file_path)

        # Проверяем, есть ли данные
        if not df.empty:
            plt.figure(figsize=(10, 6))
            plt.hist(df['absolute_error'], bins=30, color='blue', alpha=0.7)
            plt.title('Распределение абсолютных ошибок')
            plt.xlabel('Абсолютная ошибка')
            plt.ylabel('Частота')
            plt.grid(axis='y', alpha=0.75)
            plt.savefig(output_image_path)
            plt.close()
            print(f'График сохранен в {output_image_path}')
        else:
            print('Файл пуст.')
    else:
        print('Файл metric_log.csv не найден.')


if __name__ == '__main__':
    while True:
        plot_error_distribution()
        time.sleep(5)  # Обновляем график каждые 5 секунд
