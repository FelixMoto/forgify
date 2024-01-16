"""import packages"""
# %%
from pathlib import Path

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
    
    Returns
    -------
    decklist : str
        the decklist as a string
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

    # click more button
    driver.find_elements(By.ID, "subheader-more")[0].click()
    driver.implicitly_wait(1)

    # click on export
    driver.find_elements(By.LINK_TEXT,"Export")[0].click()
    driver.implicitly_wait(2)

    # get text from text area containing the decklist
    text_area = driver.find_elements(By.CLASS_NAME, "form-control")[0]
    decklist_str = text_area.text
    driver.quit()

    return decklist_str


def map_to_dck(decklist, verbose):
    """takes the single string returned from get_decklist_from_url
    and map that onto a decklist that can be read by forge
    
    Parameters
    ----------
    decklist : str
        the decklist as a single string
    verbose - bool
        if the decklist and the total number of cards should be
        printed to the command line
        
    Returns
    -------
    deck_str : str
        one string containing the decklist in the forge format
    commander_name : str
        name of the commander, which serves as the file name

    """

    # split decklist into cards by the return str
    card_list = decklist.split("\n")

    # go through all cards and transform the string
    forge_list = []
    num_cards = []
    for ii, element in enumerate(card_list):
        # get amount of that card
        amount, rest = element.split(" ", 1)
        # get card name and expansion
        cardname, expansion = rest.split("(")
        cardname = cardname.split("/",1)[0].strip()
        expansion, _ = expansion.split(")")
        forge_list.append(amount.strip() + " " + "|".join([cardname.strip(),expansion.strip(),"1"]))
        num_cards.append(int(amount))

        # we assume the first card to be the commander
        if ii == 0:
            commander_name = cardname

    # concatenate strings into decklist
    header = f"[metadata]\nName={commander_name:s}\n[Commander]\n{forge_list[0]:s}\n"
    main = "[Main]\n" + "\n".join([elements for elements in forge_list[1:]]) + "\n[Sideboard]"
    deck_str = header + main

    # command line invert color and reset
    REVERSE = "\033[97;45m" # white text on magenta background
    RESET = "\033[0m"

    # print our decklist
    print("\n")
    print(f"{REVERSE}Decklist:{RESET}") # only to demonstrate different coloring
    print(deck_str + "\n")
    # print number of cards in list
    print(f"{REVERSE}Number of cards{RESET}")
    print(sum(num_cards), "\n")

    return deck_str, commander_name


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
