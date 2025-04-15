from flask import Flask, render_template, request, redirect, flash
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Map department to sheet ID
department_sheet_map = {
    'Mathematics': '1H1_gPKbUNYJKMiOPlrA39ul5oSGaqrq7_4ZseyhVdeQ',
    'Physics': '1-qR-7UFjrfl2XIYE_5795iABn9j28zfqY09Z_gR47bw',
    'Chemistry': '1_SyTC3R-f94Ahu_G23JSe1CMj5iKUpwbSNiYtCgeCIc',
    'English': '1Nf_bwlAuMYdFPFcqDfcoTvF5ahO4IsNvoC0KF9Weo6o',
    'General Events': '1qkMNeZuKymjqb9YKca0IQMfmbKNFMKjW9GSrLF75Ezs'
}

# Phone number validation (10 digits)
def validate_phone(phone):
    return bool(re.match(r'^\d{10}$', phone))

# Routes
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
        # Collect form data
        data = {
            'Team Name': request.form.get('team_name', '').strip(),
            'Team Lead': request.form.get('team_lead', '').strip(),
            'Team Lead Email': request.form.get('team_lead_email', '').strip(),
            'Team Lead Phone': request.form.get('team_lead_phone', '').strip(),
            'Member 1': request.form.get('member1', '').strip(),
            'Member 1 Phone': request.form.get('member1_phone', '').strip(),
            'College': request.form.get('college', '').strip(),
            'Department': request.form.get('department', '').strip(),
            'Event': request.form.get('event', '').strip()
        }

        # Validate required fields
        required_fields = list(data.keys())
        missing = [field for field in required_fields if not data[field]]
        if missing:
            flash(f"Missing fields: {', '.join(missing)}", 'error')
            return render_template("register.html", form=data)

        # Validate phone numbers
        if not validate_phone(data['Team Lead Phone']):
            flash("Invalid phone number format for Team Lead.", 'error')
            return render_template("register.html", form=data)

        if not validate_phone(data['Member 1 Phone']):
            flash("Invalid phone number format for Member 1.", 'error')
            return render_template("register.html", form=data)

        # Get correct Google Sheet
        sheet_id = department_sheet_map.get(data['Department'])
        if not sheet_id:
            flash("Invalid department selected.", 'error')
            return render_template("register.html", form=data)

        # Try saving to Google Sheet
        try:
            print("Saving to Google Sheet:", data)
            sheet = client.open_by_key(sheet_id).sheet1
            sheet.append_row(list(data.values()))
            flash("✅ Registration successful!", 'success')
            return redirect('/')
        except gspread.exceptions.APIError as e:
            print(f"Google Sheets API error: {e}")
            flash("⚠️ Error saving to Google Sheets. Please try again.", 'error')
            return render_template("register.html", form=data)
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("⚠️ An unexpected error occurred. Please contact support.", 'error')
            return render_template("register.html", form=data)

    return render_template("register.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
