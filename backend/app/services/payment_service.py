import secrets
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.payment import Payment, Invoice, PaymentStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.pass_attendance import FestPass, PassStatus
from app.models.notification import Notification
from app.models.user import User
from app.schemas.payment import PaymentOut, InvoiceOut
from app.utils.qr import generate_qr_code_image


class PaymentService:
    @staticmethod
    def process_payment(
        db: Session,
        user: User,
        registration_id: int,
        transaction_id: Optional[str] = None,
        payment_method: str = "UPI"
    ) -> PaymentOut:
        reg = db.query(Registration).options(
            joinedload(Registration.event),
            joinedload(Registration.user)
        ).filter(Registration.id == registration_id).first()

        if not reg:
            raise HTTPException(status_code=404, detail="Registration not found")

        if reg.user_id != user.id:
            raise HTTPException(status_code=403, detail="You can only pay for your own registration")

        if reg.status == RegistrationStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="Registration is already paid and confirmed")

        tx_id = transaction_id or f"TXN-{secrets.token_hex(8).upper()}"

        # 1. Create Payment record
        payment = Payment(
            registration_id=reg.id,
            user_id=user.id,
            amount=reg.amount,
            transaction_id=tx_id,
            payment_method=payment_method,
            status=PaymentStatus.SUCCESS,
            paid_at=datetime.now(timezone.utc)
        )
        db.add(payment)
        db.flush()

        # 2. Generate Invoice
        invoice_number = f"INV-{datetime.now().year}-{reg.id}-{secrets.token_hex(3).upper()}"
        invoice = Invoice(
            payment_id=payment.id,
            invoice_number=invoice_number,
            invoice_url=f"/api/payments/invoice/{invoice_number}"
        )
        db.add(invoice)

        # 3. Confirm registration & increment event counter
        reg.status = RegistrationStatus.CONFIRMED
        event = reg.event
        if event:
            event.registered_count += 1

        # 4. Generate Fest Pass with QR code
        qr_token = f"FEST-PASS-{reg.id}-{secrets.token_hex(8).upper()}"
        qr_url = generate_qr_code_image(qr_token)

        existing_pass = db.query(FestPass).filter(FestPass.registration_id == reg.id).first()
        if not existing_pass:
            fest_pass = FestPass(
                registration_id=reg.id,
                qr_token=qr_token,
                qr_image_url=qr_url,
                status=PassStatus.ACTIVE
            )
            db.add(fest_pass)

        # 5. Add notification
        db.add(
            Notification(
                user_id=user.id,
                title="Payment Successful!",
                message=f"Payment of ₹{float(reg.amount):.2f} confirmed for {event.name}. Your Fest Pass is active.",
                type="PAYMENT",
                link=f"/passes/{reg.id}"
            )
        )

        db.commit()
        db.refresh(payment)

        return PaymentOut(
            id=payment.id,
            registration_id=reg.id,
            event_name=event.name,
            amount=float(payment.amount),
            transaction_id=payment.transaction_id,
            payment_method=payment.payment_method,
            status=payment.status,
            paid_at=payment.paid_at,
            invoice=InvoiceOut(
                id=invoice.id,
                invoice_number=invoice.invoice_number,
                amount=float(payment.amount),
                issued_at=invoice.issued_at,
                invoice_url=invoice.invoice_url
            )
        )

    @staticmethod
    def get_my_payments(db: Session, user: User) -> List[PaymentOut]:
        payments = db.query(Payment).options(
            joinedload(Payment.registration).joinedload(Registration.event),
            joinedload(Payment.invoice)
        ).filter(Payment.user_id == user.id).order_by(Payment.created_at.desc()).all()

        results = []
        for p in payments:
            results.append(
                PaymentOut(
                    id=p.id,
                    registration_id=p.registration_id,
                    event_name=p.registration.event.name if p.registration and p.registration.event else "Event",
                    amount=float(p.amount),
                    transaction_id=p.transaction_id,
                    payment_method=p.payment_method,
                    status=p.status,
                    paid_at=p.paid_at,
                    invoice=InvoiceOut(
                        id=p.invoice.id,
                        invoice_number=p.invoice.invoice_number,
                        amount=float(p.amount),
                        issued_at=p.invoice.issued_at,
                        invoice_url=p.invoice.invoice_url
                    ) if p.invoice else None
                )
            )
        return results
