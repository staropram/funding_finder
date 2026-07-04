import re

class NihrFundingCard:
    def extract_link(self,fcd):
        link = fcd.find("a",href=True)
        if link==None:
            raise ValueError("No href found in funding card")
        return link

    def extract_title(self,fcd):
        title_div = fcd.find("div",id=re.compile("^card-title"))
        if title_div==None:
            raise ValueError("No title div found in funding card")
        title_h3 = title_div.find("h3")
        if title_h3==None:
            raise ValueError("No title div found in funding card (h3)")

        return title_h3.get_text(strip=True)

    def __init__(self,fcd):
        self.link = self.extract_link(fcd)
        self.title = self.extract_title(fcd)
        self.desc = fcd.find("div",class_=re.compile("^text-regular")).find("div").text
        self.opens = self.parse_timestamp(fcd.find("div",class_="field--name-field-start-datetime").find("time")["datetime"])
        self.closes = self.parse_timestamp(fcd.find("div",class_="field--name-field-end-datetime").find("time")["datetime"])
        self.status = fcd.find("div",class_="status").text.strip("\n ")


