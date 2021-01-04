# Chii - twin's Cool Bot for Amazon Polly

A bot designed to let Mizuki be heard once again. **Also, Nightcore!**

**Unfortunately**, I can't give out the link to my instance of this bot. The AWS Polly API's limits aren't especially forgiving, and paying for Mizuki isn't something I'm up for.

# Setting Up

**Requirements**

* All packages specified in requirements.txt (use `pip install -r requirements.txt`).

* 2 SQL Databses - one for server settings, and one for the character count - though really, a database for the latter might be a bit much. If you'd like to set up a more elegant solution for keeping track of one persistent value, it's for sure encouraged.

* AWS Key/Secret Key - see [here](https://aws.amazon.com/).

* Discord Bot Token - see [here](https://discordapp.com/developers).

If you plan to run this using Docker, I wouold advise using Docker's Slim Buster image.