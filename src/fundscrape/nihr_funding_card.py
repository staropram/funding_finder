import re
import arrow
from datetime import datetime, timezone

class NihrFundingCard:
    def extract_link(self,fcd):
        link = fcd.find("a",href=True)
        if link==None:
            raise ValueError("No href found in funding card")
        return f"https://nihr.ac.uk{link['href']}"

    def extract_title(self,fcd):
        title_div = fcd.find("div",id=re.compile("^card-title"))
        if title_div==None:
            raise ValueError("No title div found in funding card")
        title_h3 = title_div.find("h3")
        if title_h3==None:
            raise ValueError("No title div found in funding card (h3)")

        return title_h3.get_text(strip=True)

    def extract_desc(self,fcd: str) -> str:
        desc_div = fcd.find("div",class_=re.compile("^text-regular"))
        if desc_div==None:
            raise ValueError("No description div found in funding card")
        desc_div2 = desc_div.find("div")
        if desc_div2==None:
            raise ValueError("No description div found in funding card (subdiv)")
        
        return desc_div2.get_text(strip=True)

    def parse_timestamp(self,ts: str) -> datetime:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)

    def extract_timebound(self,fcd: str,selected_end: str) -> datetime:
        class_name = f"field--name-field-{selected_end}-datetime"
        time_div = fcd.find("div",class_=class_name)
        if time_div==None:
            raise ValueError(f"No time div found in funding card ({selected_end})")
        
        time_div2 = time_div.find("time",datetime=True)
        if time_div2==None:
            raise ValueError(f"No time element found in funding card ({selected_end})")
        
        return self.parse_timestamp(time_div2["datetime"])

    def extract_status(self,fcd:str) -> str:
        status_div = fcd.find("div",class_="status")
        if status_div==None:
            raise ValueError("No status element found in funding card")
        
        return status_div.get_text(strip=True)

    def __str__(self):
        opens = ""
        closes = ""
        if self.status!="Opening soon":
            opens = arrow.get(self.opens).format("Do MMMM YYYY [at] ha")
            closes = arrow.get(self.closes).format("Do MMMM YYYY [at] ha")

        output_string = f"Title: {self.title}\nStatus: {self.status}\nOpens: {opens}\nCloses: {closes}\nDescription: {self.desc}\nURL: {self.link}"
        return output_string

    def __init__(self,fcd):
        self.link = self.extract_link(fcd)
        self.title = self.extract_title(fcd)
        self.desc = self.extract_desc(fcd)
        self.status = self.extract_status(fcd)
        if self.status=="Opening soon":
            self.opens = None
            self.closes = None
        else:
            self.opens = self.extract_timebound(fcd,"start")
            self.closes = self.extract_timebound(fcd,"end")
        print(self)


