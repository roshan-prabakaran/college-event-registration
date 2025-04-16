from flask import Flask, render_template, request, redirect, flash
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

google_creds_str = os.environ.get('GOOGLE_CREDENTIALS_JSON')
if not google_creds_str:
    raise ValueError("Missing GOOGLE_CREDENTIALS_JSON environment variable.")

google_creds_dict = json.loads(google_creds_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds_dict, scope)
client = gspread.authorize(creds)

# Department to Sheet ID Mapping
department_sheet_map = {
    'Mathematics': '1H1_gPKbUNYJKMiOPlrA39ul5oSGaqrq7_4ZseyhVdeQ',
    'Physics': '1-qR-7UFjrfl2XIYE_5795iABn9j28zfqY09Z_gR47bw',
    'Chemistry': '1_SyTC3R-f94Ahu_G23JSe1CMj5iKUpwbSNiYtCgeCIc',
    'English': '1Nf_bwlAuMYdFPFcqDfcoTvF5ahO4IsNvoC0KF9Weo6o',
    'General Events': '1qkMNeZuKymjqb9YKca0IQMfmbKNFMKjW9GSrLF75Ezs'
}

def validate_phone(phone):
    return bool(re.match(r'^\d{10}$', phone))

def ensure_headers(sheet, headers):
    """Write headers if the sheet is empty"""
    existing_data = sheet.get_all_values()
    if not existing_data:
        sheet.insert_row(headers, index=1)

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
        data = {
            'Team Name': request.form.get('team_name', '').strip(),
            'Team Lead': request.form.get('team_lead', '').strip(),
            'Team Lead Email': request.form.get('team_lead_email', '').strip(),
            'Team Lead Phone': request.form.get('team_lead_phone', '').strip(),  # Corrected
            'Member 1': request.form.get('member1', '').strip(),
            'Member 1 Phone': request.form.get('member1_phone', '').strip(),  # Corrected
            'College': request.form.get('college', '').strip(),
            'College Address': request.form.get('college_address', '').strip(),
            'Department': request.form.get('department', '').strip(),
            'Event': request.form.get('event', '').strip(),
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        required_fields = list(data.keys())
        missing = [field for field in required_fields if not data[field]]
        if missing:
            flash(f"❌ Missing fields: {', '.join(missing)}", 'error')
            return render_template("register.html", form=data)

        if not validate_phone(data['Team Lead Phone']):
            flash("❌ Invalid phone number for Team Lead.", 'error')
            return render_template("register.html", form=data)

        if not validate_phone(data['Member 1 Phone']):
            flash("❌ Invalid phone number for Member 1.", 'error')
            return render_template("register.html", form=data)

        sheet_id = department_sheet_map.get(data['Department'])
        if not sheet_id:
            flash("❌ Invalid department selected.", 'error')
            return render_template("register.html", form=data)

        try:
            sheet = client.open_by_key(sheet_id).sheet1

            # Ensure headers exist
            headers = list(data.keys())
            ensure_headers(sheet, headers)

            # Append data
            sheet.append_row(list(data.values()))

            # WhatsApp community link
            whatsapp_link = "https://chat.whatsapp.com/L9Va0pKN2oWCqJ7zvKbcnV"  # Replace with your actual link

            flash(f"✅ Registration successful! Join our WhatsApp community: {whatsapp_link}", 'success')
            return redirect('/')

        except gspread.exceptions.APIError as e:
            print(f"Google Sheets API error: {e}")
            flash("⚠️ Google Sheets error. Please try again later.", 'error')
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("⚠️ Unexpected error. Please contact support.", 'error')

        return render_template("register.html", form=data)

    return render_template("register.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
