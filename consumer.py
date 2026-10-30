import boto3
import json
import time
import os

from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

# AWS SQS
sqs = boto3.client(
    "sqs",
    region_name="eu-north-1"
)

# AWS SES
ses = boto3.client(
    "ses",
    region_name="eu-north-1"
)

QUEUE_URL = "https://sqs.eu-north-1.amazonaws.com/560245954931/ticket"

SENDER_EMAIL = os.getenv("SES_FROM_EMAIL")


while True:

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])

    for message in messages:

        try:
            booking = json.loads(message["Body"])

            # 1. Save booking in MariaDB
            connection = get_db_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO ticket_data (
                            booking_id,
                            event_id,
                            event_name,
                            customer_name,
                            customer_email,
                            quantity,
                            unit_price,
                            total_amount
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            booking_id = booking_id
                        """,
                        (
                            booking["booking_id"],
                            booking["event_id"],
                            booking["event_name"],
                            booking["customer_name"],
                            booking["customer_email"],
                            booking["quantity"],
                            booking["unit_price"],
                            booking["total_amount"]
                        )
                    )

                connection.commit()

            finally:
                connection.close()

            print("Booking saved successfully!")

            # 2. Send confirmation email using SES
            email_body = f"""
Hello {booking['customer_name']},

Your ticket booking has been received!

Booking ID: {booking['booking_id']}
Event: {booking['event_name']}
Quantity: {booking['quantity']}
Total Amount: Rs. {booking['total_amount']}

Thank you for booking with us!

Ticket Booking Team
"""

            email_response = ses.send_email(
                Source=SENDER_EMAIL,
                Destination={
                    "ToAddresses": [
                        booking["customer_email"]
                    ]
                },
                Message={
                    "Subject": {
                        "Data": "Your Ticket Booking Confirmation"
                    },
                    "Body": {
                        "Text": {
                            "Data": email_body
                        }
                    }
                }
            )

            print("Confirmation email sent!")
            print("Email Message ID:", email_response["MessageId"])

            # 3. Delete SQS message after successful processing
            sqs.delete_message(
                QueueUrl=QUEUE_URL,
                ReceiptHandle=message["ReceiptHandle"]
            )

            print("SQS message deleted successfully!")

        except Exception as error:
            print("Booking processing failed:", error)
            print("Message will be retried by SQS.")
            time.sleep(2)
