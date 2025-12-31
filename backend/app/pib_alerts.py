"""
PIB Alert System
Sends email alerts to PIB officers when negative news is detected
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from .config import settings
from .database import get_database, PIBAlert

logger = logging.getLogger(__name__)


def send_pib_alert(
    article_title: str,
    article_summary: str,
    article_link: str,
    language: str,
    sentiment_score: float,
    article_id: str,
    schemes: list = None,
) -> bool:
    """
    Sends an email alert to the PIB officer for scheme-related negative news.
    
    Args:
        article_title: Title of the article
        article_summary: Summary of the article
        article_link: URL to the article
        language: Language of the article
        sentiment_score: Sentiment confidence score
        article_id: Database ID of the article
        schemes: List of government schemes mentioned in the article
        
    Returns:
        bool: True if alert was sent successfully, False otherwise
    """
    try:
        logger.info(f"PIB Alert triggered for article: {article_id}")
        logger.info(f"   Title: {article_title[:100]}...")
        logger.info(f"   Sentiment Score: {sentiment_score:.2f}")
        logger.info(f"   Language: {language}")
        logger.info(f"   Schemes: {', '.join(schemes) if schemes else 'None'}")
        
        # Create database record first
        db = get_database()
        alert_id = None
        try:
            with db.get_session() as session:
                # Check if alert already exists for this article
                existing_alert = session.query(PIBAlert).filter(
                    PIBAlert.article_id == article_id
                ).first()
                
                if existing_alert:
                    logger.info(f"Alert already exists for article {article_id}, skipping duplicate")
                    return False
                
                # Create new alert record
                alert = PIBAlert(
                    article_id=article_id,
                    title=article_title,
                    summary=article_summary,
                    link=article_link,
                    language=language,
                    sentiment_score=sentiment_score,
                    is_reviewed=False,
                    email_sent=False,
                )
                session.add(alert)
                session.commit()
                alert_id = alert.id
                logger.info(f"PIB Alert record created in database: {alert_id}")
        except Exception as db_error:
            logger.warning(f"Could not save alert to database: {db_error}")
            logger.info("  Continuing with email notification...")
        
        # Send email if SMTP is configured
        if settings.SMTP_ENABLED:
            logger.info(f"Attempting to send email alert to {settings.PIB_ALERT_EMAIL}...")
            success = _send_email_notification(
                article_title,
                article_summary,
                article_link,
                language,
                sentiment_score,
                schemes
            )
            
            # Update email sent status
            if alert_id:
                try:
                    with db.get_session() as session:
                        alert = session.query(PIBAlert).filter(PIBAlert.id == alert_id).first()
                        if alert:
                            alert.email_sent = success
                            if success:
                                alert.email_sent_at = datetime.utcnow()
                            session.commit()
                except Exception as e:
                    logger.warning(f"⚠ Could not update email status in database: {e}")
            
            if success:
                logger.info(f"Email alert sent successfully to {settings.PIB_ALERT_EMAIL}")
            else:
                logger.warning(f"Failed to send email alert")
            
            return success
        else:
            logger.info("SMTP is disabled, email not sent")
            return alert_id is not None  # Success if database record was created
            
    except Exception as e:
        logger.exception(f"Failed to create PIB alert: {e}")
        return False


def _send_email_notification(
    article_title: str,
    article_summary: str,
    article_link: str,
    language: str,
    sentiment_score: float,
    schemes: list = None,
) -> bool:
    """
    Internal function to send professional email notification via Gmail SMTP
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Validate SMTP configuration
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured. Please set SMTP_USERNAME and SMTP_PASSWORD in .env")
            logger.error("   For Gmail: Use your Gmail address and an App Password (not your regular password)")
            logger.error("   Generate App Password at: https://myaccount.google.com/apppasswords")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"PIB Alert: Negative Sentiment Detected in Scheme-Related News"
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = settings.PIB_ALERT_EMAIL
        
        logger.info(f"   From: {settings.SMTP_FROM_EMAIL}")
        logger.info(f"   To: {settings.PIB_ALERT_EMAIL}")
        logger.info(f"   SMTP Server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        
        # Format schemes list
        schemes_text = ', '.join(schemes) if schemes else 'None detected'
        
        # Create professional email body
        text_body = f"""
Dear Officer,

This is an automated alert from the NewsScope India monitoring system.

A news article with negative sentiment related to government schemes has been detected and requires your attention.

ARTICLE DETAILS:

Title: {article_title}

Summary: {article_summary or 'Not available'}

Source Link: {article_link}

Language: {language.upper()}

Sentiment Score: {sentiment_score:.2f} (Negative)

Government Schemes Mentioned: {schemes_text}

RECOMMENDED ACTION:
Please review this article and assess whether any official response or corrective action is required.

Access the alert dashboard at: {settings.FRONTEND_URL}/pib-alerts

Best regards,
NewsScope India Alert System

Note: This is an automated message. Please do not reply to this email.
        """
        
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 650px; margin: 0 auto; padding: 0; background-color: #f5f5f5; }}
        .header {{ background-color: #1e3a8a; color: white; padding: 25px 30px; }}
        .header h2 {{ margin: 0; font-size: 20px; font-weight: 600; }}
        .content {{ background-color: white; padding: 30px; }}
        .greeting {{ margin-bottom: 20px; color: #1e3a8a; font-weight: 500; }}
        .info-section {{ margin: 25px 0; }}
        .info-section h3 {{ color: #1e3a8a; font-size: 14px; text-transform: uppercase; margin-bottom: 15px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }}
        .info-row {{ margin: 12px 0; padding: 12px; background-color: #f9fafb; border-left: 3px solid #dc2626; }}
        .label {{ font-weight: 600; color: #4b5563; display: block; margin-bottom: 5px; font-size: 13px; }}
        .value {{ color: #1f2937; }}
        .action-section {{ margin-top: 30px; padding: 20px; background-color: #fef2f2; border-radius: 5px; }}
        .action-section h4 {{ margin-top: 0; color: #991b1b; font-size: 14px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #1e3a8a; color: white; text-decoration: none; border-radius: 4px; margin-top: 15px; font-weight: 500; }}
        .button:hover {{ background-color: #1e40af; }}
        .footer {{ padding: 20px 30px; text-align: center; color: #6b7280; font-size: 12px; background-color: #f9fafb; }}
        .footer p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Press Information Bureau - Alert Notification</h2>
        </div>
        <div class="content">
            <p class="greeting">Dear Officer,</p>
            <p>This is an automated alert from the NewsScope India monitoring system. A news article with negative sentiment related to government schemes has been detected and requires your attention.</p>
            
            <div class="info-section">
                <h3>Article Details</h3>
                
                <div class="info-row">
                    <span class="label">Title</span>
                    <span class="value">{article_title}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">Summary</span>
                    <span class="value">{article_summary or 'Not available'}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">Source Link</span>
                    <span class="value"><a href="{article_link}" target="_blank" style="color: #2563eb;">{article_link}</a></span>
                </div>
                
                <div class="info-row">
                    <span class="label">Language</span>
                    <span class="value">{language.upper()}</span>
                </div>
                
                <div class="info-row">
                    <span class="label">Sentiment Score</span>
                    <span class="value" style="color: #dc2626; font-weight: 600;">{sentiment_score:.2f} (Negative)</span>
                </div>
                
                <div class="info-row">
                    <span class="label">Government Schemes Mentioned</span>
                    <span class="value">{', '.join(schemes) if schemes else 'None detected'}</span>
                </div>
            </div>
            
            <div class="action-section">
                <h4>Recommended Action</h4>
                <p>Please review this article and assess whether any official response or corrective action is required.</p>
                <a href="{settings.FRONTEND_URL}/pib-alerts" class="button">Access Alert Dashboard</a>
            </div>
        </div>
        <div class="footer">
            <p><strong>NewsScope India Alert System</strong></p>
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>&copy; {datetime.now().year} Press Information Bureau, Government of India</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via Gmail SMTP
        logger.info(f"   Connecting to Gmail SMTP server...")
        
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=30) as server:
            server.set_debuglevel(0)  # Set to 1 for detailed SMTP debugging
            
            if settings.SMTP_USE_TLS:
                logger.info(f"   Starting TLS encryption...")
                server.starttls()
            
            logger.info(f"   Authenticating with Gmail...")
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            logger.info(f"   Sending email message...")
            server.send_message(msg)
        
        logger.info("PIB alert email sent successfully via Gmail SMTP")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Gmail SMTP Authentication Failed: {e}")
        logger.error("   Please check:")
        logger.error("   1. SMTP_USERNAME is your full Gmail address")
        logger.error("   2. SMTP_PASSWORD is an App Password (not your regular Gmail password)")
        logger.error("   3. Generate App Password at: https://myaccount.google.com/apppasswords")
        logger.error("   4. 2-Step Verification must be enabled on your Google account")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: {e}")
        return False
    except Exception as e:
        logger.exception(f"Failed to send PIB alert email: {e}")
        return False


def create_alert_record(
    article_id: str,
    article_title: str,
    article_summary: str,
    article_link: str,
    language: str,
    sentiment_score: float,
) -> Optional[str]:
    """
    Create a PIB alert record in the database without sending email
    
    Returns:
        str: Alert ID if created successfully, None otherwise
    """
    try:
        db = get_database()
        with db.get_session() as session:
            # Check if alert already exists
            existing_alert = session.query(PIBAlert).filter(
                PIBAlert.article_id == article_id
            ).first()
            
            if existing_alert:
                logger.info(f"Alert already exists for article {article_id}")
                return existing_alert.id
            
            # Create new alert
            alert = PIBAlert(
                article_id=article_id,
                title=article_title,
                summary=article_summary,
                link=article_link,
                language=language,
                sentiment_score=sentiment_score,
                is_reviewed=False,
                email_sent=False,
            )
            session.add(alert)
            session.commit()
            logger.info(f"PIB Alert record created: {alert.id}")
            return alert.id
            
    except Exception as e:
        logger.exception(f"Failed to create PIB alert record: {e}")
        return None


def get_unread_alert_count() -> int:
    """
    Get count of unreviewed PIB alerts
    
    Returns:
        int: Number of unreviewed alerts
    """
    try:
        db = get_database()
        with db.get_session() as session:
            count = session.query(PIBAlert).filter(
                PIBAlert.is_reviewed == False
            ).count()
            return count
    except Exception as e:
        logger.exception(f"Failed to get unread alert count: {e}")
        return 0
