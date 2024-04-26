from app.core.enums import TextChoices


class FileInfoStatusChoices(TextChoices):
    PENDING = "pending"
    ON_PROCESS = "on_process"
    COMPLETED = "completed"
