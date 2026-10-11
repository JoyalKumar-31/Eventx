import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.payment import Payment, Invoice
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User
from app.models.enums import PaymentStatus, RegistrationStatus
from app.services.audit_service import log_action
from app.services.notification_service import create_notification


class PaymentService:
    @staticmethod
    def create_payment_order(db: Session, registration_id: int, user_id: int) -> Payment:
        registration = db.query(Registration).filter(Registration.id == registration_id).first()
        if not registration:
            raise HTTPException(status_code=404, detail="Registration record not found")

        if registration.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to initiate payment for this registration")

        event = db.query(Event).filter(Event.id == registration.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Check existing successful payment
        existing_success = db.query(Payment).filter(
            Payment.registration_id == registration_id,
            Payment.status == PaymentStatus.SUCCESS
        ).first()
        if existing_success:
            raise HTTPException(status_code=400, detail="This registration has already been paid for")

        gateway_order_id = f"ORDER_{uuid.uuid4().hex[:12].upper()}"

        payment = Payment(
            registration_id=registration.id,
            user_id=user_id,
            amount=event.registration_fee,
            currency="INR",
            status=PaymentStatus.PENDING,
            payment_gateway="GATEWAY_SANDBOX",
            gateway_order_id=gateway_order_id
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        log_action(
            db,
            action="PAYMENT_ORDER_CREATED",
            entity_type="Payment",
            entity_id=str(payment.id),
            user_id=user_id,
            new_values={"amount": payment.amount, "gateway_order_id": gateway_order_id}
        )

        return payment

    @staticmethod
    def verify_and_complete_payment(
        db: Session,
        payment_id: int,
        transaction_id: str,
        payment_method: str = "CARD",
        simulate_status: str = "SUCCESS",
        user_id: Optional[int] = None
    ) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment record not found")

        if user_id and payment.user_id != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized payment verification")

        if payment.status == PaymentStatus.SUCCESS:
            return payment

        if simulate_status.upper() == "SUCCESS":
            payment.status = PaymentStatus.SUCCESS
            payment.transaction_id = transaction_id
            payment.payment_method = payment_method
            payment.paid_at = datetime.now(timezone.utc)

            # Update registration status to CONFIRMED
            if payment.registration_id:
                reg = db.query(Registration).filter(Registration.id == payment.registration_id).first()
                if reg:
                    reg.status = RegistrationStatus.CONFIRMED
                    if reg.team_id:
                        team_regs = db.query(Registration).filter(
                            Registration.event_id == reg.event_id,
                            Registration.team_id == reg.team_id
                        ).all()
                        for tr in team_regs:
                            tr.status = RegistrationStatus.CONFIRMED

            # Generate Invoice
            import uuid
            user = db.query(User).filter(User.id == payment.user_id).first()
            inv_number = f"INV-{datetime.now().strftime('%Y%m')}-{payment.id:04d}-{uuid.uuid4().hex[:4].upper()}"
            tax = round(payment.amount * 0.18, 2) if payment.amount > 0 else 0.0

            invoice = Invoice(
                invoice_number=inv_number,
                payment_id=payment.id,
                registration_id=payment.registration_id,
                amount=payment.amount,
                tax_amount=tax,
                total_amount=payment.amount + tax,
                issued_to_name=user.full_name if user else "Participant",
                issued_to_email=user.email if user else "",
                billing_details=f"Payment via {payment_method}. Transaction Ref: {transaction_id}",
                issued_at=datetime.now(timezone.utc)
            )
            db.add(invoice)

            # Notify user
            create_notification(
                db,
                user_id=payment.user_id,
                title="Payment Confirmed",
                message=f"Your payment of ₹{payment.amount:.2f} for registration was successful. Invoice #{inv_number} generated."
            )

        else:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = "Transaction declined by gateway simulation"

        db.commit()
        db.refresh(payment)

        log_action(
            db,
            action=f"PAYMENT_{payment.status.value}",
            entity_type="Payment",
            entity_id=str(payment.id),
            user_id=payment.user_id,
            new_values={"status": payment.status.value, "transaction_id": transaction_id}
        )

        return payment
