"""import packages"""


# %%
from pathlib import Path
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_decklist_from_url(url, verbose):
    """take a url to moxfield, click through more and export buttons
    to reveal the decklist and return the text
    
    Parameters
    ----------
    url : str
        the url to the desired deck
    verbose : bool
        detail printed to command line
    
    Returns
    -------
    Deck : dict
        containing the fields
        Deckname - name of the deck from moxfield
        Decklist - full string with all cards
        N_Commanders - the number of commanders
    """

    # Set Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    # Create a Chrome webdriver instance with the specified options
    driver = webdriver.Chrome(options=chrome_options)
    if verbose:
        print("running Chrome in headless mode")

    # Example: Open a website in headless Firefox
    driver.get(url)


    # wait for page to fully load
    # Wait until the page is fully loaded
    if verbose:
        print("catching list from website")
    wait = WebDriverWait(driver, 10)

    wait.until(EC.presence_of_element_located((By.ID, "subheader-more")))

    # click Download button
    driver.find_elements(By.LINK_TEXT, "Download")[0].click()
    driver.implicitly_wait(30)

    # get text from text area containing the decklist
    text_area = driver.find_elements(By.CLASS_NAME, "form-control")[0]
    decklist_str = text_area.text

    # check if one or two commanders are in the list
    cmd_tag = driver.find_elements(By.CLASS_NAME, "d-inline-block")[1].text
    # find all numbers in string
    n_cmd = re.findall(r'\d+', cmd_tag)
    # if we have numbers, take the first, otherwise assume we have just one commander
    if n_cmd:
        n_cmd = int(n_cmd[0])
    else:
        n_cmd = 1

    # find the deck name
    deckname = driver.find_elements(By.CLASS_NAME, "deckheader-name")[0].text
    # modify deckname to remove amojis and slashes, that could mess up the save directory
    deckname = remove_emoji(deckname)
    deckname = deckname.replace("/", " ")

    driver.quit()

    # pack into dict
    Deck = {
        "deckname" : deckname,
        "n_commanders" : n_cmd,
        "decklist" : decklist_str,
    }

    return Deck


def map_to_dck(Deck):
    """takes the single string returned from get_decklist_from_url
    and map that onto a decklist that can be read by forge
    
    Parameters
    ----------
    decklist : dict
        the output from the function get_decklist_from_url
        expected to contain the deckname, the card list as a single string
        and the number of commanders
        
    Returns
    -------
    deck_str : str
        one string containing the decklist in the forge format
    commander_name : str
        name of the commander, which serves as the file name

    """

    # unpack dict
    deckname = Deck["deckname"]
    decklist = Deck["decklist"]
    n_cmd = Deck["n_commanders"]

    # split decklist into main and sideboard, if we have sideboard cards
    main_sideboard = decklist.split("\n\n")
    # split decklist into cards by the return str, ignore sideboard for now
    card_list = main_sideboard[0].split("\n")

    # go through all cards and transform the string
    forge_list = []
    num_cards = []
    for element in card_list:
        # get amount of that card
        amount, rest = element.split(" ", 1)
        # get card name and expansion
        cardname, expansion = rest.split("(")
        cardname = cardname.split("/",1)[0].strip()
        expansion, _ = expansion.split(")")
        forge_list.append(amount.strip() + " " + "|".join([cardname.strip(),expansion.strip(),"1"]))
        num_cards.append(int(amount))


    # concatenate strings into decklist
    commanders = "\n".join([elements for elements in forge_list[:n_cmd]])
    header = f"[metadata]\nName={deckname:s}\n[Commander]\n{commanders:s}\n"
    main = "[Main]\n" + "\n".join([elements for elements in forge_list[n_cmd:]]) + "\n[Sideboard]"
    deck_str = header + main

    # command line invert color and reset
    reverse = "\033[97;45m" # white text on magenta background
    reset = "\033[0m"

    # print our decklist
    print("\n")
    print(f"{reverse}Decklist:{reset}") # only to demonstrate different coloring
    print(deck_str + "\n")
    # print number of cards in list
    print(f"{reverse}Number of cards{reset}")
    print(sum(num_cards), "\n")

    return deck_str, deckname


def save_to_dck(decklist, commander, save_path, verbose) -> None:
    """takes the decklist string and save it to the desired path as a .dck file
    
    Parameters
    ----------
    decklist : str
        the decklist in a single string
    commander :  str
        name of the commander, after which the file will be named
    save_path : pathlib Path
        path to where forge save its files
    
    Returns
    -------
    None
    
    """

    # set default save path
    if save_path is None:
        # get default path
        save_path = Path("/Users/broehl/Documents/")
    filename = save_path / f"{commander:s}.dck"

    if verbose:
        print(f"saving decklist to: \n {str(save_path):s}")

    # save decklist as file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(decklist)


def remove_emoji(string):
    """ removes emojis from a string. useful for the deck names, because somtimes peorple
    put emojis in there.

    reference:
    https://gist.github.com/slowkow/7a7f61f495e3dbb7e3d767f97bd7304b
    
    Parameters
    ----------
    string : str
        input string
    
    Returns
    -------
    emoji_pattern : str
        modified string without emojis
    """

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)

    emoji_pattern =  emoji_pattern.sub(r'', string)

    return emoji_pattern


# %%
