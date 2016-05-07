from kafka import KafkaProducer, KafkaClient
import datetime
import time
import json

#Example : http://www.giantflyingsaucer.com/blog/?p=5541
class IotProducer:
    def __init__(self, kafka_ip_ports, discriminator):
        self.discriminator = discriminator
        self.kafka_ip_ports = kafka_ip_ports
        self.producer = KafkaProducer(bootstrap_servers=[kafka_ip_ports], value_serializer=lambda m: json.dumps(m).encode('ascii'))
        #self.producer = KafkaProducer(bootstrap_servers=[kafka_ip_ports])
        print("created producer")
    def enqueue(self, m):
        print("In enqueue method!!!!!!!")
        m = {'hello' : 'world'}
        try:
            print("attempting to send message to queue: " + self.discriminator)
            self.producer.send(self.discriminator, m)
            print("message succeeded!!!!!")
        except:
            print("Exception")
            time.sleep(1)
            self.producer.send(self.discriminator, m)
    def close(self):
        print("shutting down")
        self.producer.close()

