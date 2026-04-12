import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, BaseLoader

from app.core.config import settings


EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a1a1a; background: #f5f5f5; margin: 0; padding: 0; }
  .container { max-width: 600px; margin: 32px auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e5e5; }
  .header { padding: 28px 32px; background: #0f0f0f; }
  .header h1 { color: #ffffff; margin: 0; font-size: 20px; font-weight: 600; }
  .header p { color: #888; margin: 4px 0 0; font-size: 13px; }
  .health-bar { padding: 16px 32px; font-size: 13px; font-weight: 500; }
  .health-green { background: #d1fae5; color: #065f46; }
  .health-yellow { background: #fef9c3; color: #713f12; }
  .health-red { background: #fee2e2; color: #7f1d1d; }
  .body { padding: 24px 32px; }
  .summary { font-size: 15px; line-height: 1.7; color: #333; white-space: pre-wrap; }
  .section { margin-top: 24px; }
  .section h2 { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #888; margin-bottom: 10px; }
  .pill-list { display: flex; flex-direction: column; gap: 6px; }
  .pill { background: #f5f5f5; border-radius: 6px; padding: 8px 12px; font-size: 13px; color: #333; }
  .pill.stale { background: #fff7ed; color: #92400e; }
  .pill.action { background: #eff6ff; color: #1e40af; }
  .footer { padding: 16px 32px; border-top: 1px solid #e5e5e5; font-size: 12px; color: #aaa; }
  .stat-row { display: flex; gap: 12px; margin-top: 20px; }
  .stat { flex: 1; background: #f9f9f9; border-radius: 8px; padding: 12px; text-align: center; }
  .stat .num { font-size: 22px; font-weight: 600; color: #111; }
  .stat .label { font-size: 11px; color: #888; margin-top: 2px; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>DevPulse — {{ repo }}</h1>
    <p>Last {{ period }} days &middot; Generated {{ generated_at }}</p>
  </div>

  <div class="health-bar health-{{ health }}">
    {{ health_icon }} {{ health.upper() }} &mdash; {{ health_reason }}
  </div>

  <div class="body">
    <div class="stat-row">
      <div class="stat"><div class="num">{{ stats.total_commits }}</div><div class="label">Commits</div></div>
      <div class="stat"><div class="num">{{ stats.total_prs_merged }}</div><div class="label">PRs merged</div></div>
      <div class="stat"><div class="num">{{ stats.total_issues_closed }}</div><div class="label">Issues closed</div></div>
      <div class="stat"><div class="num">{{ stats.contributors | length }}</div><div class="label">Contributors</div></div>
    </div>

    <div class="section">
      <div class="summary">{{ summary }}</div>
    </div>

    {% if highlights %}
    <div class="section">
      <h2>Highlights</h2>
      <div class="pill-list">
        {% for h in highlights %}
        <div class="pill">{{ h }}</div>
        {% endfor %}
      </div>
    </div>
    {% endif %}

    {% if stale_items %}
    <div class="section">
      <h2>Watch out</h2>
      <div class="pill-list">
        {% for s in stale_items %}
        <div class="pill stale">{{ s }}</div>
        {% endfor %}
      </div>
    </div>
    {% endif %}

    {% if action_items %}
    <div class="section">
      <h2>Action items</h2>
      <div class="pill-list">
        {% for a in action_items %}
        <div class="pill action">{{ a }}</div>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>

  <div class="footer">
    Sent by DevPulse &middot; <a href="{{ dashboard_url }}" style="color:#888">View in dashboard</a>
  </div>
</div>
</body>
</html>
"""


class EmailService:
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.template = self.env.from_string(EMAIL_TEMPLATE)

    def _render(self, digest: dict, repo: str, period: int, stats: dict) -> str:
        from datetime import datetime

        health = digest.get("overall_health", "yellow")
        icons = {"green": "✓", "yellow": "!", "red": "x"}

        return self.template.render(
            repo=repo,
            period=period,
            generated_at=datetime.utcnow().strftime("%b %d, %Y %H:%M UTC"),
            health=health,
            health_icon=icons.get(health, "!"),
            health_reason=digest.get("health_reason", ""),
            summary=digest.get("summary", ""),
            highlights=digest.get("highlights", []),
            stale_items=digest.get("stale_items", []),
            action_items=digest.get("action_items", []),
            stats=stats,
            dashboard_url=settings.frontend_url,
        )

    def send_digest(
        self,
        to_email: str,
        digest: dict,
        repo: str,
        period: int,
        stats: dict,
    ) -> bool:
        html_body = self._render(digest, repo, period, stats)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"DevPulse: {repo} — {period}-day digest"
        msg["From"] = settings.email_from
        msg["To"] = to_email

        msg.attach(MIMEText(digest.get("summary", ""), "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.email_from, to_email, msg.as_string())
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False


email_service = EmailService()
