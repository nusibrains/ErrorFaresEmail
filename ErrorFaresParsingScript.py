from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from email.mime.text import MIMEText
import smtplib
import sys


MY_URL = 'http://www.secretflying.com/posts/category/error-fare/'
USER_CLIENT = uReq(MY_URL)
PAGE_HTML = USER_CLIENT.read()
USER_CLIENT.close()
PAGE_SOUP = soup(PAGE_HTML, "html.parser")
ERROR_FARES_CONTENT = PAGE_SOUP.findAll("div", {"class": "article-content-wrapper entry-main-content"})
ORIGINAL_TEXT_FILE = "errorfarelist.txt"
DIFFERENCES_TEXT_FILE = "errorfaresdiffs.txt"


# This writes the previous data from a text file into a list prior to the next function potentially finding updates.
def store_existing_deals_in_mem():
    with open(ORIGINAL_TEXT_FILE, "r") as F:
        current_deals_file = []
        for word in F:
            current_deals_file.append(word.strip('\n'))
    return current_deals_file


# The website page 'titles' are parsed then the content is written to a text file (overwrites all data in the file).
def parse_and_write_to_file():
    with open(ORIGINAL_TEXT_FILE, "w+") as F:
        for deals in ERROR_FARES_CONTENT:
            try:
                deal = deals.div.a["title"]
                deal_string = str(deal)
            except FailedToParse:
                print("Error scraping website data")
                sys.exit(1)
            F.write(deal_string + "\n" "\n")
    return


# The newly written page 'titles' are looped over and placed into a second list in memory for comparision.
def store_latest_deals_in_mem():
    with open(ORIGINAL_TEXT_FILE, "r") as F:
        latest_deals_file = []
        for word in F: latest_deals_file.append(word.strip('\n'))
    return latest_deals_file


# Both lists in memory are compared. Differences are written to a second file. No differences results in a blank file.
def store_diffs_in_file(new_scrape, old_scrape):
    differences = "\n \n".join([i for i in new_scrape + old_scrape if (i not in new_scrape) or (i not in old_scrape)])
    with open(DIFFERENCES_TEXT_FILE, "w+") as F:
        F.write(differences)
    return differences


# This function is only executed if there is content in the 'differences' text file, if data exists, email is sent.
def construct_email():
    with open(DIFFERENCES_TEXT_FILE, "r") as list:
        msg = MIMEText(list.read())
    from_addr = "calebkurtz@gmail.com"
    to_addr = "calebkurtz@hotmail.com"
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Latest Error Fares"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_addr, "kurtzkid")
    text = msg.as_string()
    server.sendmail(from_addr, to_addr, text)
    server.quit()
    print("email sent successfully")


if __name__ == '__main__':
    current_deals_file = store_existing_deals_in_mem()
    parse_and_write_to_file()
    latest_deals_file = store_latest_deals_in_mem()
    differences = store_diffs_in_file(latest_deals_file, current_deals_file)
    if differences:
        construct_email()
    else:
        print("no new updates")
        sys.exit(1)
