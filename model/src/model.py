import pika
import pickle
import numpy as np
import json
 
print("Model start")

with open('myfile.pkl', 'rb') as pkl_file: #чтение файла с сериализованной моделью
    regressor = pickle.load(pkl_file)
while True: 
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq')) #создание подключения по адресу rabbitmq
        channel = connection.channel()
    
        channel.queue_declare(queue='features') #очередь features
        channel.queue_declare(queue='y_pred') #очередь y_pred
    
        def callback(ch, method, properties, body): #функция callback для обработки данных из очереди
            print(f'\n\nПолучен вектор признаков {body}\n')
            features_set = json.loads(body)
            message_id = features_set['id']
            features = features_set['body']
            
            pred = regressor.predict(np.array(features).reshape(1, -1))

            message_y_pred = {
            'id': message_id,
            'body': pred[0]
            }

            channel.basic_publish(exchange='',
                            routing_key='y_pred',
                            body=json.dumps(message_y_pred))
            print(f'Предсказание {pred[0]} отправлено в очередь y_pred')
    
        channel.basic_consume( #извлечение сообщения из очереди features
            queue='features',
            on_message_callback=callback,
            auto_ack=True
        )
        print('Ожидание сообщений, для выхода нажмите CTRL+C')
    
        channel.start_consuming() #запуск режима ожидания прихода сообщений
    except Exception as e:
        print('Не удалось подключиться к очереди', e)