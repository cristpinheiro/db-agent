from sqlalchemy.engine import Engine

from app.services.glossary.admin_glossary import admin_glossary
from app.services.glossary.feedback_glossary import feedback_glossary
from app.services.glossary.schema_aware_glossary import schema_aware_glossary
from app.services.schema_discovery import schema_discovery


class GlossaryCompositor:
    def build_glossary_prompt(self, engine: Engine, connection_name: str) -> str:
        schema_info = schema_discovery.discover(engine, connection_name)

        admin_section = admin_glossary.format_for_prompt(connection_name)
        feedback_section = feedback_glossary.format_for_prompt(connection_name)
        schema_section = schema_aware_glossary.format_for_prompt(schema_info, connection_name)

        parts = []
        if admin_section:
            parts.append(admin_section)
        if feedback_section:
            parts.append(feedback_section)
        if schema_section:
            parts.append(schema_section)

        if not parts:
            return ""

        header = (
            "=== BUSINESS GLOSSARY ===\n"
            "Priority: Admin > Feedback > Schema-inferred\n"
        )
        return header + "\n\n".join(parts)


glossary_compositor = GlossaryCompositor()
