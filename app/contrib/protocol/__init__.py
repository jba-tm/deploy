from app.core.enums import TextChoices


class ProtocolSourceChoices(TextChoices):
    BE = "be"
    PUBMED = "pubmed"
    OG = "og"


class FileType(TextChoices):
    PDF = "pdf"
    DOCX = "docx"
