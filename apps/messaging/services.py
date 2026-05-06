from .models import MessageLog, MessageTemplate
from .providers import provider_for


def render_template(text, lead, context=None):
    context = context or {}
    values = {
        "name": lead.name or "there",
        "email": lead.email,
        "intent_score": lead.intent_score,
        **context,
    }
    for key, value in values.items():
        text = text.replace("{{ " + key + " }}", str(value))
        text = text.replace("{{" + key + "}}", str(value))
    return text


def send_message(company, lead, channel, template_name, context=None):
    template = MessageTemplate.objects.get(company=company, channel=channel, name=template_name)
    recipient = lead.email if channel == "email" else lead.phone
    if not recipient:
        return None
    log = MessageLog.objects.create(
        company=company,
        lead=lead,
        channel=channel,
        recipient=recipient,
        subject=render_template(template.subject, lead, context),
        body=render_template(template.body, lead, context),
    )
    provider_for(channel).send(log)
    return log

