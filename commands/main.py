"""entry point file"""

import os
from pathlib import Path
import json
import click

import importlib.metadata

import commands.utils 

# containing save path
CONFIG_FILENAME = Path(os.path.dirname(__file__)) / "config.json"


def print_version(ctx, param, value):
    """eager function callback to print out version"""

    if not value or ctx.resilient_parsing:
        return
    # get version from pyproject.toml 
    version = importlib.metadata.version("forgify")
    click.echo(version)
    ctx.exit()


def set_path(ctx, param, value):
    """define the path where to save the decklist to."""

    if not value or ctx.resilient_parsing:
        return

    # define config file
    config_dict = {
        "savepath" : value,
    }

    # save to json file
    with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
        json.dump(config_dict, f)

    print(f"savepath changed to: {value:s}")

    # exit here, otherwise the rest will run after
    ctx.exit()


@click.command()
@click.argument("url", type=str)
@click.option("--verbose", "-v", is_flag=True, help="Will print verbose messages.")
@click.option("--version", is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="print version number.")
@click.option("--set_path", callback=set_path,
              expose_value=True, is_eager=True, help="set path to where decklists are saved.")
def cli(url, verbose, set_path) -> None:
    """Command line tool to fetch decklists from Moxfield.com and translate them
    into deck list readable with MtG forge.
    
    --- Save time and play more ---
    """

    # get savepath
    if not os.path.isfile(CONFIG_FILENAME):
        save_path = Path(os.getcwd())
    else:
        with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
            data = json.load(f)
            config_dict = data
        save_path = Path(config_dict["savepath"])


    # get decklist from web
    deck_string = commands.utils.get_decklist_from_url(url, verbose)
    # create single string for forge
    deck_string, commander = commands.utils.map_to_dck(deck_string, verbose)

    # save to file
    commands.utils.save_to_dck(deck_string, commander, save_path, verbose)
