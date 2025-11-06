# backend/routes_contact.py
from flask import Blueprint, request, jsonify
from mailer import send_email

bp = Blueprint("contact", __name__, url_prefix="/api")

@bp.post("/contact")
def contact():
    try:
        data = request.get_json()
        
        # Validate required fields
        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        email = data.get("email", "").strip()
        message = data.get("message", "").strip()
        
        if not all([first_name, last_name, email, message]):
            return jsonify({"error": "All fields are required"}), 400
        
        # Create email content
        subject = f"Contact Form Submission from {first_name} {last_name}"
        
        html_content = f"""
        <html>
        <body>
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {first_name} {last_name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong></p>
            <p>{message.replace(chr(10), '<br>')}</p>
        </body>
        </html>
        """
        
        text_content = f"""
New Contact Form Submission

Name: {first_name} {last_name}
Email: {email}

Message:
{message}
        """
        
        # Send email
        send_email(
            to="support@titansportshq.com",
            subject=subject,
            html=html_content,
            text=text_content
        )
        
        return jsonify({"success": True, "message": "Thank you for contacting us! We'll get back to you soon."}), 200
        
    except Exception as e:
        print(f"Error sending contact email: {e}")
        return jsonify({"error": "Failed to send message. Please try again later."}), 500