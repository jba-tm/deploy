from app.core.enums import TextChoices


class EntityChoices(TextChoices):
    CHAT_Q_A = "chat_q_a", "Q&A"
    CHAT_FAVORITE = "chat_favorite", "Chat favorite"
    GRAPH_KNOWLEDGE = "graph_knowledge", "Graph Knowledge"
    PROTOCOL = "protocol", "Protocol"


class SubjectChoices(TextChoices):
    CHAT_Q_A_ROOM_CREATED = "chat_q_a_room_created", "Chat Q&A room created"
    CHAT_Q_A_QUERY = "chat_q_a_query", "Chat Q&A query"
    CHAT_FAVORITE_ROOM_CREATED = "chat_favorite_created", "Chat favorite room created"
    CHAT_FAVORITE_QUERY = "chat_favorite_query", "Chat Q&A query"

    PROTOCOL_CREATED = "protocol_created", "Protocol created"
    PROTOCOL_FILE_GENERATED = "protocol_file_generated", "Protocol file generated"
