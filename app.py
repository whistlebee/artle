from os import urandom
from pathlib import Path
from typing import Annotated

import polars as pl
from litestar import Litestar, get, post
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.enums import RequestEncodingType
from litestar.middleware.session.client_side import CookieBackendConfig
from litestar.params import Body
from litestar.response import Template
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from dataclasses import dataclass
dataset = pl.read_csv("archive/artDataset.csv")


@get("/")
async def index() -> Template:
    art = dataset.sample(1).to_dicts()[0]
    art["id"] = art[""]
    return Template(template_name="index.html", context=art)


@dataclass
class Guess:
    price: int

def remove_non_numeric(s: str) -> int:
    return int("".join([c for c in s if c.isdigit()]))


@post("/artwork/guess/{art_id:int}")
async def guess(
    art_id: int,
    data: Annotated[Guess, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> Template:
    art = dataset.filter(pl.col("") == art_id).to_dicts()[0]
    actual_price = remove_non_numeric(art["price"])
    print(actual_price)
    guessed_price = data.price

    # if within 5% of the actual price then correct
    correct = abs(actual_price - guessed_price) / actual_price < 0.05

    difference = actual_price - guessed_price

    context = dict(
        art_id=art_id,
        guessed_price=guessed_price,
        correct=correct,
        difference=difference,
        actual_price=actual_price,
    )
    return Template(template_name="partials/guess.html", context=context)


session_config = CookieBackendConfig(secret=urandom(16))  # type: ignore[arg-type]

app = Litestar(
    route_handlers=[
        index,
        guess,
        create_static_files_router(
            path="/artwork/", directories=["archive/artDataset"]
        ),
    ],
    template_config=TemplateConfig(
        directory=Path("templates"),
        engine=JinjaTemplateEngine,
    ),
    # middleware=[session_config.middleware],
)
