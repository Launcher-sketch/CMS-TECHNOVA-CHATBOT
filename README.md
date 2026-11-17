# CMS TECHNOVA AI Assistant

A small Flask-based event information chatbot starter project.

## Run on Windows

1. Open this folder in VS Code.
2. In the terminal, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Start the website:

   ```powershell
   python app.py
   ```

5. Open http://127.0.0.1:5000 in your browser.

## Important

The FAQ and event information in `data/technova.json` is starter/demo content, not verified official CMS TECHNOVA information. Replace it with confirmed details from the official brochure or organisers before publishing.

## Deploying

The repository includes a `Procfile` and `render.yaml` for a Render web service. Push the *contents of this folder* to the root of your GitHub repository, so `requirements.txt` and `app.py` are at the repository root.


## CMS event categories and adding new events

The homepage displays the categories configured in `data/technova.json`.
Categories can remain visible with the status `Coming soon` until verified information is available.

To add an event, add an object to the `events` array, for example:

```json
{
  "name": "Sample Quiz",
  "category": "academic",
  "description": "Add only confirmed information from an official CMS notice here.",
  "keywords": ["sample quiz", "quiz"]
}
```

Use one of these category IDs: `technova`, `cultural`, `sports`, `science`, `academic`, or `other`.
After editing the JSON, commit the change to GitHub. Render will redeploy the site automatically if auto-deploy is enabled.

Important: the uploaded ZIP contained an empty `events` list and only generic starter FAQs. It did not contain the detailed TECHNOVA brochure information. Add verified brochure facts to the data file before treating TECHNOVA answers as complete.
