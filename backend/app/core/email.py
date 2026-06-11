from __future__ import annotations

from html import escape
from typing import Optional

import resend

from app.core.config import settings
from app.modules.itineraries.schemas import ItineraryPlanResponse


def configure_resend() -> None:
    resend.api_key = settings.require_resend_api_key()


def send_html_email(email: str, subject: str, html: str) -> None:
    configure_resend()
    params: resend.Emails.SendParams = {
        "from": settings.MAIL_FROM,
        "to": [email],
        "subject": subject,
        "html": html,
    }
    resend.Emails.send(params)


def send_verification_email(email: str, token: str) -> None:
    verification_url = f"{settings.resolved_frontend_url}/verify-email?token={token}"
    send_html_email(
        email,
        "Verify your Isle Be There account",
        f"""
        <h2>Welcome to Isle Be There!</h2>
        <p>Click the link below to verify your email address:</p>
        <a href="{verification_url}">Verify Email</a>
        <p>This link expires in 24 hours.</p>
        """,
    )


def send_password_reset_email(email: str, token: str) -> None:
    reset_url = f"{settings.resolved_frontend_url}/reset-password?token={token}"
    send_html_email(
        email,
        "Reset your Isle Be There password",
        f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}">Reset Password</a>
        <p>This link expires in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        """,
    )


def send_itinerary_email(
    email: str,
    itinerary_title: str,
    itinerary: ItineraryPlanResponse,
    *,
    country: Optional[str] = None,
    interests: Optional[list[str]] = None,
    view_url: Optional[str] = None,
) -> None:
    subject_location = country or itinerary_title or "your trip"
    subject = f"Your Isle Be There itinerary for {subject_location}"
    html = build_itinerary_email_html(
        itinerary_title=itinerary_title,
        itinerary=itinerary,
        country=country,
        interests=interests or [],
        view_url=view_url,
    )
    send_html_email(email, subject, html)


def build_itinerary_email_html(
    *,
    itinerary_title: str,
    itinerary: ItineraryPlanResponse,
    country: Optional[str],
    interests: list[str],
    view_url: Optional[str],
) -> str:
    title = escape(itinerary_title or "Your itinerary")
    location = escape(country or "Caribbean")
    total_cost = format_currency(itinerary.total_estimated_cost)
    daily_budget = format_currency(itinerary.daily_target_budget)
    trip_days = itinerary.trip_days
    date_summary = format_trip_dates(itinerary)
    interest_html = "".join(
        render_chip(title_case(interest), "#ecfeff", "#155e75", "#bae6fd")
        for interest in interests
    )
    day_sections = "".join(render_day_section(day, index) for index, day in enumerate(itinerary.days))
    cta_html = (
        f"""
        <div style="margin-top: 24px;">
          <a
            href="{escape(view_url)}"
            style="display:inline-block;background:#0891b2;color:#ffffff;text-decoration:none;padding:14px 22px;border-radius:16px;font-weight:700;font-size:14px;"
          >
            View itinerary in app
          </a>
        </div>
        """
        if view_url
        else ""
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="x-apple-disable-message-reformatting">
        <title>{title}</title>
        <style>
          body, table, td, div, h1, p, a {{
            font-family: Arial, Helvetica, sans-serif;
          }}

          body {{
            margin: 0;
            padding: 0;
            background: #f8fafc;
            color: #0f172a;
          }}

          table {{
            border-collapse: collapse;
          }}

          .email-shell {{
            padding: 32px 16px;
            background: #f8fafc;
          }}

          .email-card {{
            width: 100%;
            max-width: 880px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 28px;
            overflow: hidden;
          }}

          .hero {{
            padding: 40px 32px;
            background: #020617;
          }}

          .section-padding {{
            padding-left: 24px;
            padding-right: 24px;
          }}

          .summary-table {{
            border-collapse: separate;
            border-spacing: 0 16px;
          }}

          .summary-cell {{
            width: 33.33%;
          }}

          .summary-cell-left {{
            padding: 0 8px 0 0;
          }}

          .summary-cell-center {{
            padding: 0 8px;
          }}

          .summary-cell-right {{
            padding: 0 0 0 8px;
          }}

          .summary-card {{
            height: 100%;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            background: #ffffff;
            padding: 18px 18px 16px;
          }}

          .day-card {{
            margin-top: 20px;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            overflow: hidden;
            background: #ffffff;
          }}

          .day-header {{
            padding: 20px 24px;
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
          }}

          .stop-row td {{
            vertical-align: top;
          }}

          .stop-meta {{
            width: 150px;
            padding: 0 16px 0 0;
          }}

          .stop-main {{
            padding: 0 16px 0 0;
          }}

          .stop-aside {{
            width: 110px;
            text-align: right;
          }}

          .summary-value,
          .day-title,
          .hero-title,
          .hero-copy,
          .stop-row-title,
          .stop-copy,
          .stop-location,
          .stop-meta-label,
          .stop-aside-copy {{
            word-break: break-word;
          }}

          @media only screen and (max-width: 620px) {{
            .email-shell {{
              padding: 16px 10px !important;
            }}

            .email-card {{
              border-radius: 20px !important;
            }}

            .hero {{
              padding: 28px 20px !important;
            }}

            .hero-title {{
              font-size: 28px !important;
              line-height: 1.2 !important;
            }}

            .hero-copy {{
              font-size: 15px !important;
              line-height: 1.6 !important;
            }}

            .section-padding {{
              padding-left: 14px !important;
              padding-right: 14px !important;
            }}

            .section-padding-top {{
              padding-top: 18px !important;
            }}

            .summary-table,
            .stop-layout {{
              display: block !important;
            }}

            .summary-table tbody,
            .summary-table tr,
            .summary-cell,
            .stop-layout tbody,
            .stop-row,
            .stop-meta,
            .stop-main,
            .stop-aside {{
              display: block !important;
              width: 100% !important;
            }}

            .summary-cell {{
              box-sizing: border-box !important;
              padding: 0 0 12px 0 !important;
            }}

            .summary-table tr:last-child .summary-cell:last-child {{
              padding-bottom: 0 !important;
            }}

            .summary-card {{
              padding: 16px !important;
            }}

            .day-card {{
              margin-top: 16px !important;
              border-radius: 20px !important;
            }}

            .day-header,
            .stop-shell {{
              padding: 18px 16px !important;
            }}

            .day-title {{
              font-size: 21px !important;
              line-height: 1.35 !important;
            }}

            .stop-meta,
            .stop-main {{
              padding: 0 0 14px 0 !important;
            }}

            .stop-aside {{
              padding: 0 !important;
              text-align: left !important;
            }}

            .stop-row-title {{
              font-size: 17px !important;
            }}
          }}
        </style>
      </head>
      <body style="margin:0;padding:0;background:#f8fafc;color:#0f172a;">
        <div class="email-shell" style="margin:0;padding:32px 16px;background:#f8fafc;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
            <tr>
              <td align="center">
                <div class="email-card" style="max-width:880px;margin:0 auto;overflow:hidden;border-radius:28px;border:1px solid #e2e8f0;background:#ffffff;">
                  <div class="hero" style="padding:40px 32px;background:#020617;">
                    <div style="font-size:12px;font-weight:700;letter-spacing:0.24em;text-transform:uppercase;color:#67e8f9;">
                      Itinerary builder
                    </div>
                    <h1 class="hero-title" style="margin:16px 0 0;font-size:36px;line-height:1.15;color:#ffffff;">
                      {title}
                    </h1>
                    <p class="hero-copy" style="margin:16px 0 0;max-width:620px;font-size:16px;line-height:1.7;color:#cbd5e1;">
                      Your Caribbean trip plan is ready. Here is the current day-by-day outline based on your destination, interests, budget, and pace.
                    </p>
                  </div>

                  <div class="section-padding section-padding-top" style="padding:24px 24px 8px;background:#ffffff;">
                    <table class="summary-table" role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:separate;border-spacing:0 16px;">
                      <tr>
                        <td class="summary-cell summary-cell-left" style="width:33.33%;padding:0 8px 0 0;">
                          {render_summary_card("Destination", location)}
                        </td>
                        <td class="summary-cell summary-cell-center" style="width:33.33%;padding:0 8px;">
                          {render_summary_card("Travel dates", escape(date_summary))}
                        </td>
                        <td class="summary-cell summary-cell-right" style="width:33.33%;padding:0 0 0 8px;">
                          {render_summary_card("Trip style", f"{escape(itinerary.budget_level.value.title())} budget | {escape(itinerary.pace.value.title())} pace")}
                        </td>
                      </tr>
                      <tr>
                        <td class="summary-cell summary-cell-left" style="width:33.33%;padding:0 8px 0 0;">
                          {render_summary_card("Trip length", f"{trip_days} {'day' if trip_days == 1 else 'days'}")}
                        </td>
                        <td class="summary-cell summary-cell-center" style="width:33.33%;padding:0 8px;">
                          {render_summary_card("Estimated total", total_cost)}
                        </td>
                        <td class="summary-cell summary-cell-right" style="width:33.33%;padding:0 0 0 8px;">
                          {render_summary_card("Daily target", daily_budget)}
                        </td>
                      </tr>
                    </table>
                  </div>

                  <div class="section-padding" style="padding:0 24px 24px;background:#ffffff;">
                    <div style="border:1px solid #e2e8f0;border-radius:24px;background:#f8fafc;padding:20px 20px 16px;">
                      <div style="font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:0.14em;color:#0891b2;">
                        Selected interests
                      </div>
                      <div style="margin-top:12px;">
                        {interest_html or '<span style="font-size:14px;color:#64748b;">No interests were selected.</span>'}
                      </div>
                    </div>
                  </div>

                  <div class="section-padding" style="padding:0 24px 32px;background:#ffffff;">
                    {day_sections or '<div style="padding:28px;border:1px solid #e2e8f0;border-radius:24px;background:#ffffff;color:#64748b;">No itinerary stops are available yet.</div>'}
                    {cta_html}
                  </div>
                </div>
              </td>
            </tr>
          </table>
        </div>
      </body>
    </html>
    """


def render_summary_card(label: str, value: str) -> str:
    return f"""
    <div class="summary-card" style="height:100%;border:1px solid #e2e8f0;border-radius:20px;background:#ffffff;padding:18px 18px 16px;">
      <div style="font-size:12px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#64748b;">
        {escape(label)}
      </div>
      <div class="summary-value" style="margin-top:10px;font-size:16px;font-weight:700;line-height:1.5;color:#0f172a;">
        {value}
      </div>
    </div>
    """


def render_day_section(day, index: int) -> str:
    total_cost = format_currency(day.total_estimated_cost)
    total_hours = f"{day.total_duration_hours:g} hours"
    stops_html = "".join(render_stop(stop) for stop in day.stops)
    return f"""
    <div class="day-card" style="margin-top:20px;overflow:hidden;border:1px solid #e2e8f0;border-radius:24px;background:#ffffff;">
      <div class="day-header" style="padding:20px 24px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">
        <div style="font-size:12px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#0891b2;">
          Day {index + 1}
        </div>
        <div class="day-title" style="margin-top:6px;font-size:24px;font-weight:700;color:#020617;">
          {escape(day.date.strftime("%A, %B %d, %Y"))}
        </div>
        <div style="margin-top:8px;font-size:14px;font-weight:700;color:#64748b;">
          {total_cost} estimated | {escape(total_hours)}
        </div>
      </div>
      {stops_html}
    </div>
    """


def render_stop(stop) -> str:
    business_type = escape((stop.business_type_name or "stop").replace("_", " ").title())
    description = escape(stop.description or "")
    city = escape(str((stop.address or {}).get("city") or ""))
    country = escape(str((stop.address or {}).get("country") or ""))
    location = ", ".join(part for part in [city, country] if part)
    tags_html = "".join(render_reason_tag(tag) for tag in stop.reason_tags)
    description_html = (
        f'<div class="stop-copy" style="margin-top:10px;font-size:14px;line-height:1.7;color:#475569;">{description}</div>'
        if description
        else ""
    )
    location_html = (
        f'<div class="stop-location" style="margin-top:8px;font-size:14px;font-weight:600;color:#64748b;">{location}</div>'
        if location
        else ""
    )
    tags_block = (
        f'<div style="margin-top:14px;">{tags_html}</div>'
        if tags_html
        else ""
    )
    return f"""
    <div class="stop-shell" style="padding:22px 24px;border-top:1px solid #f1f5f9;">
      <table class="stop-layout" role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
        <tr class="stop-row">
          <td class="stop-meta" style="width:150px;vertical-align:top;padding:0 16px 0 0;">
            <div class="stop-meta-label" style="font-size:15px;font-weight:700;color:#020617;">
              {escape(stop.start_time)} - {escape(stop.end_time)}
            </div>
            <div style="margin-top:8px;font-size:11px;font-weight:700;letter-spacing:0.16em;text-transform:uppercase;color:#94a3b8;">
              {business_type}
            </div>
          </td>
          <td class="stop-main" style="vertical-align:top;padding:0 16px 0 0;">
            <div class="stop-row-title" style="font-size:18px;font-weight:700;color:#020617;">
              {escape(stop.title)}
            </div>
            {location_html}
            {description_html}
            {tags_block}
          </td>
          <td class="stop-aside" style="width:110px;vertical-align:top;text-align:right;">
            <div style="font-size:16px;font-weight:700;color:#020617;">
              {format_currency(stop.estimated_cost)}
            </div>
            <div class="stop-aside-copy" style="margin-top:8px;font-size:13px;color:#64748b;">
              {stop.estimated_duration_hours:g} h
            </div>
          </td>
        </tr>
      </table>
    </div>
    """


def render_reason_tag(tag: str) -> str:
    normalized = (tag or "").strip().lower()
    label, colors = reason_tag_meta(normalized)
    return render_chip(label, colors[0], colors[1], colors[2])


def render_chip(label: str, background: str, text_color: str, border: str) -> str:
    return (
        f'<span style="display:inline-block;margin:0 8px 8px 0;padding:7px 12px;'
        f'border-radius:999px;background:{background};color:{text_color};'
        f'border:1px solid {border};font-size:12px;font-weight:700;">{escape(label)}</span>'
    )


def reason_tag_meta(tag: str) -> tuple[str, tuple[str, str, str]]:
    mapped = {
        "interest_match": ("Matches interests", ("#ecfdf5", "#166534", "#bbf7d0")),
        "variety": ("Adds variety", ("#ecfeff", "#155e75", "#bae6fd")),
        "within_budget": ("Within budget", ("#ecfdf5", "#166534", "#bbf7d0")),
        "near_previous_stop": ("Near previous stop", ("#f1f5f9", "#475569", "#cbd5e1")),
        "hotel_checkin": ("Hotel check-in", ("#fffbeb", "#92400e", "#fde68a")),
        "hotel_stay": ("Hotel stay", ("#f8fafc", "#475569", "#cbd5e1")),
    }
    if tag in mapped:
        return mapped[tag]

    if ":" in tag:
        prefix, value = tag.split(":", maxsplit=1)
        value_label = title_case(value.replace("_", " ").replace("-", " "))
        prefix = prefix.strip().lower()
        if prefix == "interest":
            return (
                f"Interest: {value_label}",
                ("#ecfdf5", "#166534", "#bbf7d0"),
            )
        if prefix == "category":
            return (
                f"Category: {value_label}",
                ("#ecfeff", "#155e75", "#bae6fd"),
            )
        if prefix == "pace":
            return (
                f"Pace: {value_label}",
                ("#f1f5f9", "#475569", "#cbd5e1"),
            )

    humanized = title_case(tag.replace("_", " ").replace("-", " "))
    return humanized, ("#f1f5f9", "#475569", "#cbd5e1")


def format_trip_dates(itinerary: ItineraryPlanResponse) -> str:
    if not itinerary.days:
        return "Dates to be confirmed"
    start_date = itinerary.days[0].date.strftime("%b %d, %Y")
    end_date = itinerary.days[-1].date.strftime("%b %d, %Y")
    if start_date == end_date:
        return start_date
    return f"{start_date} to {end_date}"


def format_currency(value: float) -> str:
    return f"${float(value or 0):,.2f}"


def title_case(value: str) -> str:
    return " ".join(word.capitalize() for word in value.split())
