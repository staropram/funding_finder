import os
import json
from openai import OpenAI
from pathlib import Path
from hashlib import sha256
from urllib.parse import urlparse
from pathlib import PurePosixPath
from datetime import date,datetime

# probably we need to abstract this at some point but lets keep this simple for now
# we are using deepseek because it's cheap
class AIAssessor:

    def get_response_to_query(self,message_list,think=False):
        # send the request
        response = self.ai_client.chat.completions.create(
            model=self.ai_params["model"],
            messages=message_list,
            stream=(self.ai_params["stream"]=="True"),
            reasoning_effort=self.ai_params["reasoning_effort"],
            extra_body={
                "thinking" : {
                     "type": "enabled" if think else "disabled"
                }
            },
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content


    def make_ai_summary_of_funding_detail_page(self,funding_details,force_reload=False):
        funding_id = PurePosixPath(urlparse(funding_details.funding_card.link).path).name
        cached_fn = Path(f"data/cache/{funding_id}_ai_summary.json")
        print(f"Making AI summary for {funding_id}")

        if not force_reload and cached_fn.exists():
            with cached_fn.open(encoding="utf-8") as file:
                return json.load(file)

        # construct the message list
        summary_prompt = self.ai_prompts["summary_prompt"].replace("FUNDING_DETAILS",str(funding_details))
        ai_message_list=[
            {"role": "system", "content": self.ai_prompts["summary_system_prompt"]},
            {"role": "user", "content": summary_prompt},
        ]
        ai_response = self.get_response_to_query(ai_message_list)

        response_json = {
            "card_details" : funding_details.funding_card.to_dict(),
            "response" : ai_response
        }

        with cached_fn.open("w",encoding="utf-8") as file:
            json.dump(response_json,file)

        return response_json

    def make_ai_summary_of_funding_detail_pages(self,force_reload=False):
        return [self.make_ai_summary_of_funding_detail_page(page) for page in self.fd]

    def assess_objectives_against_summaries(self,objectives,force_reload=False):
        """ Assesses each objective against the summary list """
        ai_assessments = {}
        for objective in objectives['objectives']:
            print(objective)
            ai_assessment = self.assess_objective_against_summaries(objective,force_reload=force_reload)
            ai_assessments[objective['name']] = ai_assessment

        # re-rank these now
        ranked_assessments = {}
        print("Re-ranking assessments")
        for objective in objectives['objectives']:
            assessments = ai_assessments[objective['name']]
            ranked_assessment = self.rerank_assessments_against_objective(objective,assessments,force_reload=False)
            ranked_assessments[objective['name']] = ranked_assessment

        return ranked_assessments

    def assess_objective_against_summaries(self,objective,force_reload=False):
        """ Assesses one objective against the summary list """
        summary_assessments = []
        for summary in self.ai_summaries:
            summary_assessment = self.assess_objective_against_summary(objective,summary,force_reload=force_reload)
            summary_assessments.append(summary_assessment)
        return summary_assessments

    def assess_objective_against_summary(self,objective,summary,force_reload=False):
        """ Assess one objective against one summary """

        # construct the message list for the API call
        assessment_prompt = self.ai_prompts["assessment_prompt"] \
            .replace("TODAY",str(datetime.now())) \
            .replace("RESEARCH_OBJECTIVE",str(objective)) \
            .replace("FUNDING_SUMMARY",str(summary))

        ai_message_list=[
            {"role": "system", "content": self.ai_prompts["assessment_system_prompt"]},
            {"role": "user", "content": assessment_prompt},
        ]

        # we want to cache this too unless we force it
        # take the name and the hash of the details as the file name
        details_digest = sha256(objective['details'].encode()).hexdigest()
        safe_name = (objective['name'].lower()).replace(" ","_")
        funding_id = PurePosixPath(urlparse(summary["card_details"]["link"]).path).name
        output_filename = f"data/ai_output/{safe_name}_{funding_id}_{details_digest}.json"
        output_path = Path(output_filename)

        print(f"Asking AI to assess funding opportunity {funding_id} against objective {safe_name}")
        if output_path.exists():
            print("Loading cached response")
            assessment = json.loads(output_path.read_bytes())
            # temporary fix
            if assessment.get("id") is None:
                assessment["id"] = funding_id


            return assessment

        print("Querying AI")
        ai_response = self.get_response_to_query(ai_message_list)

        # parse as json
        assessment = json.loads(ai_response)

        # add in the id
        assessment["id"] = funding_id

        # save it
        with output_path.open("w",encoding="utf-8") as file:
            json.dump(assessment,file)

        return assessment

    def rerank_assessments_against_objective(self,objective,assessments,force_reload=False):
        """ Take the assessments and re-rank them"""

        # lets ignore assessments with "do not pursue" as it makes no sense to rank them
        feasible_assessments = []
        infeasible_assessments = []
        for i, assessment in enumerate(assessments):
            if assessment["recommendation"] != "do not pursue":
                assessment["rank_id"] = i
                feasible_assessments.append(assessment)
            else:
                infeasible_assessments.append(assessment)

        num_feasible_assessments = len(feasible_assessments)

        print(f"there are {num_feasible_assessments} feasible assessments")

        # construct the message list for the API call
        reranking_prompt = self.ai_prompts["reranking_prompt"] \
            .replace("TODAY",str(datetime.now())) \
            .replace("N_ASSESSMENTS",str(num_feasible_assessments)) \
            .replace("ASSESSMENTS",str(feasible_assessments))

        ai_message_list=[
            {"role": "system", "content": self.ai_prompts["reranking_system_prompt"]},
            {"role": "user", "content": reranking_prompt},
        ]

        # we want to cache this too unless we force it
        # take the name and the hash of the details as the file name
        safe_name = (objective['name'].lower()).replace(" ","_")
        output_filename = f"data/ai_output/{safe_name}_final_ranking.json"
        output_path = Path(output_filename)

        print(f"Asking AI to re-rank funding opportunities for {safe_name} against objective and each other")
        if output_path.exists():
            print("Loading cached response")
            ranked_assessments = output_path.read_bytes()
            return ranked_assessments

        print("Querying AI for rankings")
        ai_response = self.get_response_to_query(ai_message_list,think=True)
        rankings = json.loads(ai_response)

        rank_by_id = {item["rank_id"]: item["rank"] for item in rankings}

        for assessment in feasible_assessments:
            assessment["rank"] = rank_by_id[assessment["rank_id"]]

        # order by rank
        feasible_assessments.sort(key=lambda x: x["rank"])

        # append the infeasible
        for assessment in infeasible_assessments:
            feasible_assessments.append(assessment)

        # save it
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(feasible_assessments, file, indent=2)

        return feasible_assessments

    def __init__(self,funding_details,ai_params_path,ai_prompts_path):
        self.fd = funding_details
        # load in the ai params
        with Path(ai_params_path).open(encoding="utf-8") as file:
            self.ai_params = json.load(file)

        with Path(ai_prompts_path).open(encoding="utf-8") as file:
            self.ai_prompts = json.load(file)

        api_key_path = Path("/home/ash/dsapi.txt")
        api_key = api_key_path.read_text()

        self.ai_client = OpenAI(api_key=api_key,base_url="https://api.deepseek.com")

        self.ai_summaries = self.make_ai_summary_of_funding_detail_pages()


