import json
from pathlib import Path
from email.message import EmailMessage

class HTMLGenerator:

    def __init__(self,ranked_assessments):
        self.ranked_assessments = ranked_assessments

    def _build_card_html(self, data):
        """Builds HTML for a single opportunity card."""
        concerns_li = "".join([f"<li>{c}</li>" for c in data.get("key_concerns", [])])

        return f"""
        <div class="card" id="call-{data.get("id",[])}">
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
        cards_markup = "".join(
            self._build_card_html(assessment)
            for assessment in self.ranked_assessments
            if assessment["recommendation"] != "do not pursue"
        )

        # Load your base template
        with open("config/output_template.html", "r") as f:
            template = f.read()

        # Inject the generated cards into {cards_html} placeholder
        final_html = template.replace("{cards_html}", cards_markup)

        # Write to destination file
        with open(html_file_name, "w") as f:
            f.write(final_html)

        # generate email too
        msg = EmailMessage()
        msg["Subject"] = "Funding opportunities"
        msg["From"] = "you@example.com"
        msg["To"] = "recipient@example.com"

        msg.set_content(
            final_html,
            subtype="html"
        )

        email_filename = "tests/test_data/kidney_ranked_assessments.eml"
        Path(email_filename).write_bytes(msg.as_bytes())

        print(f"Report generated: {html_file_name}")