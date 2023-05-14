import os

import requests
import yaml
from discohook import (
    Button,
    ButtonStyle,
    Choice,
    Client,
    Embed,
    Interaction,
    PartialEmoji,
    StringOption,
    View,
)
from thefuzz import fuzz

APPLICATION_ID = os.getenv("APPLICATION_ID")
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")
APPLICATION_PUBLIC_KEY = os.getenv("APPLICATION_PUBLIC_KEY")

if not (APPLICATION_ID and APPLICATION_TOKEN and APPLICATION_PUBLIC_KEY):
    raise ValueError("Missing environment variables.")

app = Client(
    application_id=APPLICATION_ID,
    token=APPLICATION_TOKEN,
    public_key=APPLICATION_PUBLIC_KEY,
)


@app.on_error
async def on_error(i: Interaction, err: Exception):
    if i.responded:
        await i.followup(f"```py\nError: {err}\n```", ephemeral=True)
    else:
        await i.response(f"```py\nError: {err}\n```", ephemeral=True)


@app.command(
    name="docs",
    description="Search for documentation",
    options=[
        StringOption(
            name="query",
            description="Doc query",
            required=True,
            autocomplete=True,
        )
    ],
)
async def docs(i: Interaction, *, query: str):
    button = Button(
        label="Open in Space",
        url=query,
        style=ButtonStyle.link,
        emoji=PartialEmoji(name="deta", id="1047502818208137336"),
    )

    view = View()
    view.add_buttons(button)

    embed = Embed(
        description=f"> [`/{query.split('/en/')[1]}`]({query})",
        color=0xEE4196,
    )
    embed.author(name="Doc Search", icon_url=i.author.avatar.url)  # type: ignore

    await i.response(embed=embed, view=view)


@docs.autocomplete(name="query")
async def docs_autocomplete(i: Interaction, value: str):
    hits = requests.get(f"https://teletype.deta.dev/search?q={value}&l=25").json()["hits"]
    await i.autocomplete(choices=[Choice(name=hit["fragments"], value=hit["url"]) for hit in hits])


@app.command(
    name="tag",
    description="Search for tag",
    options=[
        StringOption(
            name="query",
            description="Tag name",
            required=True,
            autocomplete=True,
        )
    ],
)
async def tag(i: Interaction, query: str):
    data = requests.get(query).text.strip()
    if data.startswith("---"):
        _, meta, content = data.split("---", 2)
        metadata = yaml.safe_load(meta)
    else:
        raise ValueError(f"Failed to parse tag with url {query}.")

    title = metadata.get("title")

    delete_button = Button(label="🗑️", style=ButtonStyle.grey)
    edit_button = Button(
        label="✏️ Edit",
        url=f"https://github.com/SlumberDemon/deta-bot/blob/main/resources/tags/{query.split('/tags/')[1]}",
        style=ButtonStyle.link,
    )

    view = View()
    view.add_buttons(edit_button, delete_button)

    @delete_button.on_interaction
    async def on_submit(i: Interaction):
        await i.message.delete()  # type: ignore

    embed = Embed(title=title, description=content, color=0xEE4196)
    await i.response(embed=embed, view=view)


@tag.autocomplete(name="query")
async def tag_autocomplete(i: Interaction, value: str):
    tags_info = requests.get("https://api.github.com/repos/slumberdemon/deta-bot/contents/resources/tags").json()

    items = []
    for tag_item in tags_info:
        ratio = fuzz.ratio(tag_item["name"].replace(".md", ""), value.lower())
        if ratio > 25:
            if len(items) <= 25:
                items.append({"name": tag_item["name"].replace(".md", ""), "url": tag_item["download_url"]})

    await i.autocomplete(choices=[Choice(name=item["name"], value=item["url"]) for item in items])
