import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

_template_dir = os.path.join(os.path.dirname(__file__), "templates")
_env = Environment(
    loader=FileSystemLoader(_template_dir),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

def render_template(template_name: str, **kwargs) -> str:
    template = _env.get_template(template_name)
    return template.render(**kwargs).strip()
