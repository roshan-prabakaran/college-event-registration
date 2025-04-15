from flask import Flask, render_template, request, redirect, flash
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Map department to sheet name (Google Sheet IDs)
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
            'Team Name': request.form.get('team_name', ''),
            'Team Lead': request.form.get('team_lead', ''),
            'Team Lead Email': request.form.get('team_lead_email', ''),
            'Member 1': request.form.get('member1', ''),
            'Member 1 Email': request.form.get('member1_email', ''),
            'Member 2': request.form.get('member2', ''),
            'Member 2 Email': request.form.get('member2_email', ''),
            'Contact Number': request.form.get('phone', ''),
            'College': request.form.get('college', ''),
            'Department': request.form.get('department', ''),
            'Event': request.form.get('event', '')
        }

        # Required field validation
        required_fields = ['Team Name', 'Team Lead', 'Team Lead Email', 'Contact Number', 'College', 'Department',
                           'Event']
        if team_size == '2':
            required_fields += ['Member 1', 'Member 1 Email']
        elif team_size == '3':
            required_fields += ['Member 1', 'Member 1 Email', 'Member 2', 'Member 2 Email']

        missing = [field for field in required_fields if not data[field]]
        if missing:
            flash(f"Missing fields: {', '.join(missing)}", 'error')
            return render_template("register.html")

        # Get correct Google Sheet
        sheet_id = department_sheet_map.get(data['Department'])
        if not sheet_id:
            flash("Invalid department selected.", 'error')
            return render_template("register.html")

        try:
            # Debug: Log the data being sent
            print("Data being saved to Google Sheets:", data)

            # Open the correct Google Sheet based on the department
            sheet = client.open_by_key(sheet_id).sheet1

            # Append the registration data to the sheet
            sheet.append_row(list(data.values()))
            # Flash the success message after registration
            flash("Registration successful!", 'success')
            return redirect('/')

        except gspread.exceptions.APIError as e:
            # Detailed error logging
            print(f"Google Sheets API error: {e}")
            flash(f"Error saving to Google Sheets: {e}", 'error')
            return render_template("register.html")
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash(f"Unexpected error: {e}", 'error')
            return render_template("register.html")

    return render_template("register.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
