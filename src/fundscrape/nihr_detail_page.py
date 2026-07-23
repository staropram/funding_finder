from bs4 import BeautifulSoup
import re

class NihrDetailPage:

    def extract_overview(self):

        # find main overview details and dump it all as text
        overview_div = self.fpd.find("div",id="tab-overview")
        if overview_div==None:
            self.overview_main = "No overview details"
        else:
            paragraphs = overview_div.find("div",class_="paragraph--type--rich-text")

        if paragraphs==None:
            self.overview_main = "No overview details"
        else:
            paragraph_text = paragraphs.text
            self.overview_main = re.sub(r"\n{3,}", "\n\n", paragraph_text)
        
        # eligibility
        #eligibility_p = overview_div.find("h2", string="Eligibility").find_next_sibling("p")
        #if eligibility_p==None:
        #    self.overview_eligibility = "No eligibility found"
        #self.overview_eligibility = eligibility_p.text

        # timeline
        timeline_div = overview_div.find("div",class_="timeline")
        if timeline_div==None:
            self.overview_timeline = "No timeline found"
        else:
            timeline_text = timeline_div.text
            self.overview_timeline = re.sub(r"\n{3,}","\n\n",timeline_text)

    def extract_research_spec(self):
        rspec_div = self.fpd.find("div",id="tab-research-specification")
        if rspec_div==None:
            self.research_spec = "No research spec found"
        else:
            self.research_spec = rspec_div.text


    def __str__(self):
        output_string = f"OVERVIEW MAIN: {self.overview_main}\n"
        #output_string = output_string + f"OVERVIEW ELIGIBILITY: {self.overview_eligibility}\n"
        output_string = output_string + f"OVERVIEW TIMELINE : {self.overview_timeline}\n"
        output_string = output_string + f"RESEARCH SPECIFICATION: {self.research_spec}\n"
        return output_string

    def __init__(self,fpd,funding_card):
        self.fpd = BeautifulSoup(fpd,"lxml")
        self.funding_card = funding_card
        # parse the doc
        self.extract_overview()
        self.extract_research_spec()
