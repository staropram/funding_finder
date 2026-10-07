import json
from pathlib import Path
from datetime import datetime
from datetime import time
from email.message import EmailMessage

class HTMLGenerator:
    # helpers
    def format_ordinal_day(self,day: int) -> str:
        """Return day with ordinal suffix (1st, 2nd, 3rd, 4th, etc.)."""
        if 11 <= day <= 13:
            return f"{day}th"
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        return f"{day}{suffixes.get(day % 10, 'th')}"

    def format_card_date(self,raw_date_str: str) -> str:
        if not raw_date_str or raw_date_str == "NA":
            return "NA"
        
        try:
            dt = datetime.fromisoformat(raw_date_str)
            date_part = f"{self.format_ordinal_day(dt.day)} {dt.strftime('%B %Y')}"
            
            # Check if the time is 00:00:00 (midnight)
            if dt.time() == time(0, 0, 0):
                return date_part
            
            # Format non-zero times (e.g., 5pm or 5:30pm)
            if dt.minute == 0:
                time_part = dt.strftime("%I%p").lstrip("0").lower()
            else:
                time_part = dt.strftime("%I:%M%p").lstrip("0").lower()
                
            return f"{date_part}, {time_part}"
        
        except (ValueError, TypeError):
            return "NA"

    def __init__(self,ranked_assessments,name):
        self.name = name.lower().replace(" ","_")
        self.ranked_assessments = ranked_assessments.get("assessments")
        self.priority_summary = ranked_assessments.get("priority_summary")

    def _build_card_html(self, data):
        """Builds HTML for a single opportunity card."""
        concerns_li = "".join([f"<li>{c}</li>" for c in data.get("key_concerns", [])])
        rewritten_url = data.get("url", "#").replace(
            "https://nihr.ac.uk",
            "https://www.nihr.ac.uk"
        )
        card_details = data.get("card_details")
        closes_raw = card_details.get("closes","NA")
        opens_string = self.format_card_date(card_details.get("opens","NA"))
        closes_string = self.format_card_date(closes_raw)

        return f"""
        <div class="card" id="call-{data.get("id",[])}">
            <div class="section-title">Title: {card_details.get('title',0)}</div>

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

            <div class="dates">
                <span><strong>Opens:</strong> {opens_string}</span>
                <span><strong>Closes:</strong> {closes_string}</span>

                <!-- Dedicated Days Left Field -->
                <span class="days-left-badge">
                    <script>
                    {{
                        const raw = '{closes_raw}';
                        if (raw && raw !== 'NA') {{
                        const d = Math.ceil((new Date(raw) - new Date()) / 864e5);
                        document.write(d > 0 ? `${{d}} days left` : d === 0 ? 'Closes today' : 'Closed');
                        }}
                    }}
                    </script>
                </span>
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
                <a href="{rewritten_url}" target="_blank" rel="noopener">View Call Details &rarr;</a>
            </div>
        </div>
        """

    def to_html(self):

        html_filename = f"data/final_ai_output/{self.name}_final_output.html"
        email_filename = f"data/final_ai_output/{self.name}_final_output.eml"

        # Generate HTML for all sorted cards
        cards_markup = "".join(
            self._build_card_html(assessment)
            for assessment in self.ranked_assessments
            if assessment["recommendation"] != "do not pursue"
        )

        # Load your base template
        with open("config/output_template.html", "r") as f:
            template = f.read()

        stage2 = template.replace("{priority_summary}",self.priority_summary)
        # Inject the generated cards into {cards_html} placeholder
        final_html = stage2.replace("{cards_html}", cards_markup)


        # Write to destination file
        with open(html_filename, "w") as f:
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

        Path(email_filename).write_bytes(msg.as_bytes())

        print(f"Report generated: {html_filename}")