#Archive
#Import splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt

# Set up Splinter
#executable_path = {'executable_path': ChromeDriverManager().install()}
#browser = Browser('chrome', **executable_path, headless=False)

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere": mars_hemisphere(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# Visit the Mars news site
def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

### JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemisphere(browser):
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    hemisphere_image_urls = []

##Error Occuring here - Browser not defined
#imgs_links = browser.find_by_css("a.product-item h3")

    for x in range(4):
        hemisphere = {}

        browser.find_by_css("a.product-item h3")[x].click()

        sample_img = browser.find_link_by_text("Sample").first
        hemisphere['img_url'] = sample_img['href']

        hemisphere['title'] = browser.find_by_css("h2.title").text

        hemisphere_image_urls.append(hemisphere)
        if x < 3:
            browser.back()

    return hemisphere_image_urls
    #sample_img = browser.find_link_by_text("Sample").first
    #hemisphere['img_url'] = sample_img['href']

    #hemisphere['title'] = browser.find_by_css("h2.title").text

    #hemisphere_image_urls.append(hemisphere)
    #browser.back()

    #emisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

# def scrape_hemisphere(html_text):
#     hemi_soup = soup(html_text, "html.parser")
#     try:
#         title_elem = hemi_soup.find("h2", class_="title").get_text()
#         sample_elem = hemi_soup.find("a", text="Sample").get("href")
#     except AttributeError:
#         title_elem = None
#         sample_elem = None
#     hemispheres = {
#         "title": title_elem,
#         "img_url": sample_elem
#     }
#     return hemispheres