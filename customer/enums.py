from django.db.models import TextChoices


class ScheduleChoices(TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"
    QUARTERLY = "quarterly", "Quarterly"
    # CUSTOM = "custom", "Custom"