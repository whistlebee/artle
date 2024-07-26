from pathlib import Path

from litestar import Litestar, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.response import Template
from litestar.static_files import create_static_files_router


import polars as pl

dataset = pl.read_csv("archive/artDataset.csv")
def get_random_art() -> dict:
    art = dataset.sample(1).to_dicts()[0]
    art["id"] = art[""]
    return art


@get("/")
async def index() -> Template:
    return Template(template_name="index.html", context=get_random_art())


@get("/art/random")
async def random_art() -> dict:
    return get_random_art()


app = Litestar(
    route_handlers=[
        index,
        random_art,
        create_static_files_router(path="/artwork/", directories=["archive/artDataset"])
    ],
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
)
