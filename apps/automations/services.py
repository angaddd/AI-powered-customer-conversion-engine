from datetime import timedelta

from django.utils import timezone

from apps.messaging.services import send_message
from .models import AutomationExecution, AutomationRule


def _conditions_match(rule, event):
    conditions = rule.conditions or {}
    if rule.trigger_type == "event_based":
        expected_event = conditions.get("event")
        if expected_event and event.event_type != expected_event:
            return False
    if rule.trigger_type == "score_based":
        min_score = conditions.get("intent_score_greater_than", 0)
        if event.lead.intent_score <= min_score:
            return False
    return True


def _cooldown_passed(rule, lead):
    cutoff = timezone.now() - timedelta(minutes=rule.cooldown_minutes)
    return not AutomationExecution.objects.filter(
        automation_rule=rule,
        lead=lead,
        executed_at__gte=cutoff,
    ).exists()


def evaluate_automations(event):
    if not event.lead:
        return []
    rules = AutomationRule.objects.filter(company=event.company, is_active=True)
    executions = []
    for rule in rules:
        if not _conditions_match(rule, event) or not _cooldown_passed(rule, event.lead):
            continue
        result = {"actions": []}
        for action in rule.actions:
            action_type = action.get("type")
            if action_type in ["send_email", "send_sms"]:
                channel = "email" if action_type == "send_email" else "sms"
                log = send_message(event.company, event.lead, channel, action["template"], {"event_type": event.event_type})
                result["actions"].append({"type": action_type, "message_log_id": log.id if log else None})
        executions.append(AutomationExecution.objects.create(
            company=event.company,
            automation_rule=rule,
            lead=event.lead,
            trigger_event_id=event.id,
            result=result,
        ))
    return executions

