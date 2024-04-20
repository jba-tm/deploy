from app.core.enums import TextChoices


class FileInfoStatus(TextChoices):
    PENDING = "pending"
    ON_PROCESS = "on_process"
    COMPLETED = "completed"
