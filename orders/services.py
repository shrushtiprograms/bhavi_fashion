"""
Services for orders app
"""
import logging
import uuid
import razorpay
from django.conf import settings
from django.utils import timezone
from .models import Payment, RazorpayPayment, Order

# Setup logger
logger = logging.getLogger(__name__)

class PaymentService:
    """
    Service class for handling payments through Razorpay
    """
    @staticmethod
    def get_razorpay_client():
        """
        Get Razorpay client using credentials from settings
        """
        try:
            # Check if credentials are available
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                logger.error("Razorpay credentials not configured")
                return None

            # Create client instance
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            return client
        except Exception as e:
            logger.error(f"Error creating Razorpay client: {str(e)}")
            return None

    @staticmethod
    def create_razorpay_order(order_number, amount_inr):
        """
        Create a Razorpay order

        Args:
            order_number (str): Order number
            amount_inr (float): Amount in INR

        Returns:
            dict: Razorpay order response or None if failed
        """
        try:
            # Get Razorpay client
            client = PaymentService.get_razorpay_client()
            if not client:
                return None

            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_paise = int(amount_inr * 100)

            # Generate unique receipt ID
            receipt = f"receipt_{order_number}_{uuid.uuid4().hex[:8]}"

            # Create order
            order_data = {
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': receipt,
                'notes': {
                    'order_number': order_number
                }
            }

            razorpay_order = client.order.create(data=order_data)
            logger.info(f"Created Razorpay order: {razorpay_order['id']} for order #{order_number}")

            return razorpay_order

        except Exception as e:
            logger.error(f"Error creating Razorpay order for #{order_number}: {str(e)}")
            return None

    @staticmethod
    def verify_payment_signature(payment_id, order_id, signature):
        """
        Verify Razorpay payment signature

        Args:
            payment_id (str): Razorpay payment ID
            order_id (str): Razorpay order ID
            signature (str): Razorpay signature

        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Get Razorpay client
            client = PaymentService.get_razorpay_client()
            if not client:
                return False

            # Prepare parameters
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify signature
            client.utility.verify_payment_signature(params_dict)
            return True

        except razorpay.errors.SignatureVerificationError:
            logger.error(f"Invalid payment signature for payment {payment_id}")
            return False
        except Exception as e:
            logger.error(f"Error verifying payment signature: {str(e)}")
            return False

    @staticmethod
    def process_payment_success(payment_id, order_number, signature, razorpay_order_id):
        """
        Process successful payment callback from Razorpay

        Args:
            payment_id (str): Razorpay payment ID
            order_number (str): Order number
            signature (str): Razorpay signature
            razorpay_order_id (str): Razorpay order ID

        Returns:
            bool: True if payment processed successfully, False otherwise
        """
        try:
            # Find related order and payment records
            try:
                order = Order.objects.get(order_number=order_number)
                payment = Payment.objects.get(order=order)
                razorpay_payment = RazorpayPayment.objects.get(payment=payment, razorpay_order_id=razorpay_order_id)
            except (Order.DoesNotExist, Payment.DoesNotExist, RazorpayPayment.DoesNotExist) as e:
                logger.error(f"Could not find order/payment records for order #{order_number}: {str(e)}")
                return False

            # Verify payment signature
            if not PaymentService.verify_payment_signature(payment_id, razorpay_order_id, signature):
                logger.error(f"Payment signature verification failed for order #{order_number}")

                # Update payment status to failed
                razorpay_payment.status = 'failed'
                razorpay_payment.attempts += 1
                razorpay_payment.last_attempt = timezone.now()
                razorpay_payment.save()

                payment.status = 'failed'
                payment.updated_at = timezone.now()
                payment.save()

                return False

            # Get payment details from Razorpay
            client = PaymentService.get_razorpay_client()
            payment_details = client.payment.fetch(payment_id)

            # Update RazorpayPayment record
            razorpay_payment.razorpay_payment_id = payment_id
            razorpay_payment.signature = signature
            razorpay_payment.status = 'captured'
            razorpay_payment.razorpay_response = payment_details
            razorpay_payment.attempts += 1
            razorpay_payment.last_attempt = timezone.now()
            razorpay_payment.save()

            # Update Payment record
            payment.status = 'completed'
            payment.transaction_id = payment_id
            payment.payment_response = payment_details
            payment.updated_at = timezone.now()
            payment.save()

            # Update Order status
            order.payment_status = 'paid'
            if order.order_status == 'pending':
                order.order_status = 'processing'
            order.save()

            logger.info(f"Payment processed successfully for order #{order_number}")
            return True

        except Exception as e:
            logger.error(f"Error processing payment for order #{order_number}: {str(e)}")
            return False

    @staticmethod
    def get_payment_status(order_number):
        """
        Get current payment status for an order

        Args:
            order_number (str): Order number

        Returns:
            dict: Status information or None if not found
        """
        try:
            order = Order.objects.get(order_number=order_number)
            payment = Payment.objects.get(order=order)

            try:
                razorpay_payment = RazorpayPayment.objects.get(payment=payment)

                return {
                    'order_status': order.order_status,
                    'payment_status': payment.status,
                    'payment_method': payment.payment_method,
                    'razorpay_status': razorpay_payment.status,
                    'razorpay_order_id': razorpay_payment.razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment.razorpay_payment_id,
                    'attempts': razorpay_payment.attempts,
                    'last_attempt': razorpay_payment.last_attempt,
                }
            except RazorpayPayment.DoesNotExist:
                return {
                    'order_status': order.order_status,
                    'payment_status': payment.status,
                    'payment_method': payment.payment_method,
                    'razorpay_status': None,
                }

        except (Order.DoesNotExist, Payment.DoesNotExist) as e:
            logger.error(f"Could not find order/payment records for order #{order_number}: {str(e)}")
            return None