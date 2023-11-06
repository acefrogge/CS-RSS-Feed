# Counter-Strike RSS-Feed Repository
This repository provides a collection of RSS feeds for news and updates on the [new Counter-Strike website](https://counter-strike.net), which is updated regularly as the new website unfortunately lacks this feature.  

News and Release Notes are being sent to my Discord Server [CS: Femboy](discord.gg/Z22Mjsf7RG).
You can also follow the announcement channel #cs2-updates to receive all the latest News and Release Notes in your own server.

Using [Github Workflows](https://docs.github.com/en/actions/using-workflows), the website is checked for new entries every 5-15 minutes. The RSS feeds are only updated when there are actually new entries to reduce repository noise.  

Updating the updates feed requires only one request to the website.  
Updating the news feed requires 16 requests to the website.  

## Available RSS-Feeds
### [News](https://raw.githubusercontent.com/acefrogge/CS-RSS-Feed/master/feeds/news-feed-en.xml)
### [Updates](https://raw.githubusercontent.com/acefrogge/CS-RSS-Feed/master/feeds/updates-feed-en.xml)

**Notes:**
- Valve does not localize all of their blog/update posts immediately.
  - Translations are partly driven by the community and may be available at a later date.
- Time information on the website is generally not localized.
  - When running the python scripts locally, you may have issues parsing dates.

## Acknowledgements
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
- [Feedgen](https://feedgen.kiesow.be/)
- [Feedparser](https://github.com/kurtmckee/feedparser)
- [stefanzweifel/git-auto-commit-action](https://github.com/stefanzweifel/git-auto-commit-action)
