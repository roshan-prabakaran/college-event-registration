from flask import Flask, render_template, request, redirect, flash
import os
import gspread
import json
from google.oauth2 import service_account

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_default_secret_key')

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

if not credentials_json:
    raise ValueError("Google credentials not found in environment variables.")

creds_info = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(credentials)

# Department to Google Sheet ID mapping
department_sheet_map = {
    'Mathematics': '1H1_gPKbUNYJKMiOPlrA39ul5oSGaqrq7_4ZseyhVdeQ',
    'Physics': '1-qR-7UFjrfl2XIYE_5795iABn9j28zfqY09Z_gR47bw',
    'Chemistry': '1_SyTC3R-f94Ahu_G23JSe1CMj5iKUpwbSNiYtCgeCIc',
    'English': '1Nf_bwlAuMYdFPFcqDfcoTvF5ahO4IsNvoC0KF9Weo6o',
    'General Events': '1qkMNeZuKymjqb9YKca0IQMfmbKNFMKjW9GSrLF75Ezs'
}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/tracks')
def tracks():
    return render_template("tracks.html")

@app.route('/timeline')
def timeline():
    return render_template("timeline.html")

@app.route('/coordinators')
def coordinators():
    return render_template("coordinators.html")

@app.route('/prizes')
def prizes():
    return render_template("prizes.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        team_size = request.form.get('team_size', '')
        data = {
            'Team Size': team_size,
            'Team Name': request.form.get('team_name', '').strip(),
            'Team Lead': request.form.get('team_lead', '').strip(),
            'Team Lead Email': request.form.get('team_lead_email', '').strip(),
            'Member 1': request.form.get('member1', '').strip(),
            'Member 1 Email': request.form.get('member1_email', '').strip(),
            'Member 2': request.form.get('member2', '').strip(),
            'Member 2 Email': request.form.get('member2_email', '').strip(),
            'Contact Number': request.form.get('phone', '').strip(),
            'College': request.form.get('college', '').strip(),
            'Department': request.form.get('department', '').strip(),
            'Event': request.form.get('event', '').strip()
        }

        required_fields = ['Team Name', 'Team Lead', 'Team Lead Email', 'Contact Number', 'College', 'Department', 'Event']
        if team_size == '2':
            required_fields += ['Member 1', 'Member 1 Email']
        elif team_size == '3':
            required_fields += ['Member 1', 'Member 1 Email', 'Member 2', 'Member 2 Email']

        missing = [field for field in required_fields if not data.get(field)]
        if missing:
            flash(f"Missing fields: {', '.join(missing)}", 'error')
            return render_template("register.html", data=data)

        sheet_id = department_sheet_map.get(data['Department'])
        if not sheet_id:
            flash("Invalid department selected.", 'error')
            return render_template("register.html", data=data)

        try:
            sheet = client.open_by_key(sheet_id).sheet1
            sheet.append_row(list(data.values()))
            flash("✅ Registration successful!", 'success')
            return redirect('/')
        except gspread.exceptions.APIError as e:
            flash(f"⚠️ Google Sheets API error: {str(e)}", 'error')
        except Exception as e:
            flash(f"⚠️ Unexpected error occurred: {str(e)}", 'error')

        return render_template("register.html", data=data)

    return render_template("register.html")
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
