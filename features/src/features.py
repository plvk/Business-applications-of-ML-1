import pika
import numpy as np
import json
import time
from datetime import datetime
from sklearn.datasets import load_diabetes
 
print("Features Start")

while True: #бесконечный цикл отправки сообщений в очередь
    try:
        X, y = load_diabetes(return_X_y=True) #загрузка датасета
        random_row = np.random.randint(0, X.shape[0]-1) #формирование случайного индекса строки
 
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq')) #подключение по адресу rabbitmq
        channel = connection.channel()
 
        channel.queue_declare(queue='y_true') #очередь y_true
        channel.queue_declare(queue='features') #очередь features

        message_id = datetime.timestamp(datetime.now())
        message_y_true = {
            'id': message_id,
            'body': y[random_row]
        }

        message_features = {
            'id': message_id,
            'body': list(X[random_row])
        }

        channel.basic_publish(exchange='', #публикация сообщения в очередь y_true
                            routing_key='y_true',
                            body=json.dumps(message_y_true))
        print('Сообщение с правильным ответом отправлено в очередь')
 
        channel.basic_publish(exchange='', #публикация сообщения в очередь features
                            routing_key='features',
                            body=json.dumps(message_features))
        print('Сообщение с вектором признаков отправлено в очередь')
 
        connection.close() #закрытие подключения

        time.sleep(10)
    except Exception as e:
        print('Не удалось подключиться к очереди ',e)
        time.sleep(10)