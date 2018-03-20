""" Scrapes Senate of Canada votes for 42-1 Session onwards into JSON. """
import json
import io
import os
import requests
import bs4

class RedChamber(object):
	""" Scrape the Canadian senate for the 42-1 Session onwards into JSON. """

	def __init__(self):
		""" Initializes and loads config file. """

		self.config = json.load(io.open("config.json", "r"))
		self.sessions = {}

	def scrape_sessions(self):
		""" Scrapes all sessions of interest. """

		for session in self.config["session_set"]:
			self.scrape_session(session)

	def scrape_session(self, session):
		""" Scrapes a single session of interest. """

		url = self.config["domain"] + self.config["vote_list_url"] + session

		page = requests.get(url).text
		vote_parser = bs4.BeautifulSoup(page, "lxml")
		vote_table = vote_parser.find("table", {"id": "votes-table"}).find_all("tr")[1:]
		self.sessions[session] = []
		for vote in vote_table:
			vote_check = vote.find_all("td")[1].find("a")["href"]
			self.sessions[session].append(self.scrape_vote(vote_check, session))

	def scrape_vote(self, vote_check, session):
		""" Scrapes a single vote of interest and writes JSON file out. """

		vote_id = vote_check.rsplit("/", 1)[1]
		if (os.path.isfile("votes/" + session + "_" + vote_id + ".json") and \
			not self.config["overwrite_found"]):
			return json.load(io.open("votes/" + session + "_" + vote_id + ".json", "r", encoding="utf-8"))

		url = self.config["domain"] + vote_check
		page = requests.get(url).text
		vote_parser = bs4.BeautifulSoup(page, "lxml")
		output = {}
		output["title"] = vote_parser.find("div", {"class": "vote-web-title"}).contents[0].strip()
		output["votes"] = []
		people_votes = vote_parser.find("table", {"id": "vote-details-table"}).find_all("tr")[1:]
		for person_vote in people_votes:
			vote_assembly = {}
			vote_assembly["name"] = person_vote.find("td").find("a").contents[0].strip()
			vote_assembly["party"] = person_vote.find_all("td")[1].contents[0].strip()
			vote_assembly["province"] = person_vote.find_all("td")[2].contents[0].strip()
			vote_assembly["vote"] = -1
			possible_votes = person_vote.find_all("td")[3:]
			for i in xrange(0, len(possible_votes)):
				if possible_votes[i].find("i"):
					vote_assembly["vote"] = i
					break

			output["votes"].append(vote_assembly)

		if not os.path.isdir("votes/"):
			os.mkdir("votes/")

		with io.open("votes/" + session + "_" + vote_id + ".json", "w", encoding="utf-8") as file_out:
			file_out.write(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=4))

		return output

def do_scrape():
	""" Helper to create and run scraper if ran from command line. """

	scraper = RedChamber()
	scraper.scrape_sessions()

if __name__ == "__main__":
	do_scrape()
