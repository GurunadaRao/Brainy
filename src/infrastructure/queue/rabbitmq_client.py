import json
from typing import Callable, Any
import pika
from src.configs.settings import settings


class RabbitMQClient:
    def __init__(self) -> None:
        self.credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        self.connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=self.credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

    def _get_connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(self.connection_params)

    def publish(self, queue_name: str, message: dict) -> None:
        """Publish a JSON message to a queue."""
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Inject OTel context headers
        from opentelemetry import propagate
        headers = {}
        propagate.inject(headers)
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                headers=headers
            )
        )
        connection.close()

    def start_consumer(self, queue_name: str, callback: Callable[[dict], None]) -> None:
        """
        Start consuming messages from a queue. 
        Runs blocking loop in the calling thread.
        """
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        # Process 1 message at a time
        channel.basic_qos(prefetch_count=1)

        def on_message(ch: Any, method: Any, properties: Any, body: bytes) -> None:
            from opentelemetry import propagate, trace
            headers = properties.headers or {}
            context = propagate.extract(headers)
            
            tracer = trace.get_tracer("rabbitmq-consumer")
            with tracer.start_as_current_span(f"rabbitmq_consume_{queue_name}", context=context):
                try:
                    msg_dict = json.loads(body.decode())
                    callback(msg_dict)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    print(f"Error processing message from queue '{queue_name}': {e}")
                    # Reject message and requeue it
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        channel.basic_consume(queue=queue_name, on_message_callback=on_message)
        print(f"RabbitMQ: Started consumer on queue '{queue_name}'")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        finally:
            connection.close()


# Global RabbitMQ client instance
rabbitmq_client = RabbitMQClient()
