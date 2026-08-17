import json
from pathlib import Path

class HTMLGenerator:
    # make sure the ai response is valid json and sorted
    def sort_ai_response(self,ai_response_raw):
        print("sort_ai_response")
        ai_response_raw_json = json.loads(ai_response_raw)
        ai_response_sorted = sorted(
            ai_response_raw_json.items(),
            key=lambda item: item[1].get("fit_score", 0),
            reverse=True
        )
        return ai_response_sorted


    def __init__(self,ai_response):
        self.ai_response = self.sort_ai_response(ai_response)

    def _build_card_html(self, item_id, data):
        """Builds HTML for a single opportunity card."""
        concerns_li = "".join([f"<li>{c}</li>" for c in data.get("key_concerns", [])])

        return f"""
        <div class="card" id="call-{item_id}">
            <div class="header">
                <div class="scores">
                    <div class="score-box">
                        <div class="label">Fit</div>
                        <div class="value">{data.get('fit_score', 0)}</div>
                    </div>
                    <div class="score-box">
                        <div class="label">Feasibility</div>
                        <div class="value">{data.get('feasibility_score', 0)}</div>
                    </div>
                    <div class="score-box">
                        <div class="label">Overall</div>
                        <div class="value">{data.get('overall_score', 0)}</div>
                    </div>
                </div>
                <span class="recommendation">{data.get('recommendation', 'N/A')}</span>
            </div>

            <div class="section-title">Fit Assessment</div>
            <p>{data.get('fit_assessment', '')}</p>

            <div class="section-title">Feasibility Assessment</div>
            <p>{data.get('feasibility_assessment', '')}</p>

            <div class="section-title">Key Concerns</div>
            <ul class="concerns-list">
                {concerns_li}
            </ul>

            <div class="meta-footer">
                <span><strong>Deadline:</strong> {data.get('closing_date', 'N/A')}</span>
                <a href="{data.get('url', '#')}" target="_blank" rel="noopener">View Call Details &rarr;</a>
            </div>
        </div>
        """

    def to_html(self, html_file_name):
        # Generate HTML for all sorted cards
        cards_markup = "".join([
            self._build_card_html(item_id, data) 
            for item_id, data in self.ai_response
        ])

        # Load your base template
        with open("config/output_template.html", "r") as f:
            template = f.read()

        # Inject the generated cards into {cards_html} placeholder
        final_html = template.replace("{cards_html}", cards_markup)

        # Write to destination file
        with open(html_file_name, "w") as f:
            f.write(final_html)

        print(f"Report generated: {html_file_name}")