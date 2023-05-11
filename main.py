import os
import yaml
import requests
import discohook
from thefuzz import fuzz

# Setup

app = discohook.Client(
    application_id=os.getenv("APPLICATION_ID"),
    token=os.getenv("APPLICATION_TOKEN"),
    public_key=os.getenv("APPLICATION_PUBLIC_KEY"),
)


# Error Handler


@app.on_error
async def on_error(i: discohook.Interaction, err: Exception):
    if i.responded:
        await i.followup(f"```py\nError: {err}\n```", ephemeral=True)
    else:
        await i.response(f"```py\nError: {err}\n```", ephemeral=True)


# Docs


@app.command(
    name="docs",
    description="Search for documentation",
    options=[
        discohook.StringOption(
            name="query", description="Doc query", required=True, autocomplete=True
        )
    ],
)
async def docs(i: discohook.Interaction, *, query: str):
    btn = discohook.Button(
        label="Open in Space",
        url=query,
        style=discohook.ButtonStyle.link,
        emoji=discohook.PartialEmoji(name="deta", id="1047502818208137336"),
    )

    v = discohook.View()
    v.add_buttons(btn)

    e = discohook.Embed(
        description=f"> [`/{query.split('/en/')[1]}`]({query})",
        color=0xEE4196,
    )
    e.author(name="Doc Search", icon_url=i.author.avatar.url)

    await i.response(embed=e, view=v)


@docs.autocomplete(name="query")
async def d_ac(i: discohook.Interaction, value: str):
    data = requests.get(f"https://teletype.deta.dev/search?q={value}&l=25").json()[
        "hits"
    ]
    await i.autocomplete(
        choices=[discohook.Choice(name=a["fragments"], value=a["url"]) for a in data]
    )


# Tag


@app.command(
    name="tag",
    description="Search for tag",
    options=[
        discohook.StringOption(
            name="query",
            description="Tag name",
            required=True,
            autocomplete=True,
        )
    ],
)
async def tag(i: discohook.Interaction, query: str):
    btn = discohook.Button(label="🗑️", style=discohook.ButtonStyle.grey)

    v = discohook.View()
    v.add_buttons(btn)

    @btn.on_interaction
    async def on_submit(i: discohook.Interaction):
        await i.message.delete()

    data = requests.get(query).text.strip()
    if data.startswith("---"):
        _, meta, content = data.split("---", 2)
        metadata = yaml.safe_load(meta)

    title = metadata.get("embed", {}).get("title")
    # title = metadata.get("title")
    e = discohook.Embed(title=title, description=content, color=0xEE4196)
    await i.response(embed=e, view=v)


@tag.autocomplete(name="query")
async def t_ac(i: discohook.Interaction, value: str):
    data = requests.get(
        "https://api.github.com/repos/slumberdemon/deta-bot/contents/resources/tags"
    ).json()

    items = []
    for d in data:
        ratio = fuzz.ratio(d["name"].replace(".md", ""), value.lower())
        if ratio > 25:
            if len(items) <= 25:
                items.append(
                    {"name": d["name"].replace(".md", ""), "url": d["download_url"]}
                )
    await i.autocomplete(
        choices=[discohook.Choice(name=a["name"], value=a["url"]) for a in items]
    )
