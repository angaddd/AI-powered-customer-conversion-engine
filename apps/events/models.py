from django.db import models

from apps.companies.models import Company
from apps.leads.models import Lead, VisitorSession


class Event(models.Model):
    EVENT_TYPES = [
        ("page_view", "Page View"),
        ("product_view", "Product View"),
        ("add_to_cart", "Add To Cart"),
        ("remove_from_cart", "Remove From Cart"),
        ("checkout_started", "Checkout Started"),
        ("checkout_abandoned", "Checkout Abandoned"),
        ("purchase_completed", "Purchase Completed"),
        ("form_submitted", "Form Submitted"),
        ("scroll_depth", "Scroll Depth"),
        ("button_clicked", "Button Clicked"),
        ("repeat_visit", "Repeat Visit"),
        ("custom", "Custom"),
    ]

    # main part which tell strcutures the database schema 
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="events") # on_delete=models.CASCADE= delete all entries if coampy is deleted 
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, related_name="events", null=True, blank=True)
    visitor_id = models.CharField(max_length=120)
    visitor_session = models.ForeignKey(VisitorSession, on_delete=models.SET_NULL, related_name="events", null=True, blank=True)
    session_id = models.CharField(max_length=120)
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES)
    url = models.URLField(blank=True)
    properties = models.JSONField(default=dict, blank=True) # put default to empty dict ....default={} would give error ....so use default=dict
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True) # auto_now =true changes at every update but auto_now_add add once at the initial time
    

    # meta class (inner class) helps in configurations 
    class Meta:
        indexes = [
            models.Index(fields=["company", "created_at"]),
            models.Index(fields=["company", "event_type"]),
            models.Index(fields=["company", "visitor_id"]),
            models.Index(fields=["company", "session_id"]),
        ]
