from flask import Flask, render_template, request, jsonify
import os
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
import re

os.environ['OPENAI_API_KEY'] = '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'

app = Flask(__name__)

llm_doctor = OpenAI(temperature=0.6)
prompt_template_doctor = PromptTemplate(
    input_variables=['age', 'symptoms', 'gender', 'medical_history', 'location', 'allergies'],
    template="First Aid recommendation (before meeting actual doctor physically)system:\n"
            "I want to recommend symptopms matching diseses 4 results,"
            " 3 Medicines for initial relief before meeting doctor,"
            "5 Do's and Don.t Before meeting doctors,"
            "based on the following criteria:\n"
             "Person age: {age}\n"
             "Person symptoms: {symptoms}\n"
             "Person gender: {gender}\n"
             "Person medical_history: {medical_history}\n"
             "Person location: {location}\n"
             "Person allergies: {allergies}\n"
             "Give your response in this format only and only as i am parsing your response so example:- ,"
             "1. Symptoms Matching Diseases: 1.Influenza,2.Pneumonia,3.Tuberculosis,4.Bronchitis"
             "2. Medicines for Initial Relief before Meeting Doctor: 1.Ibuprofen,2.Paracetamol,3.Cough Syrup."
             "3. Do's Before Meeting Doctor: 1.Take rest,2.drink plenty of fluids,3.gargle with salt water,4.cover your nose and mouth when coughing and sneezing."
             "4. Don'ts Before Meeting Doctor: 1.Don't take any over-the-counter medications without consulting a doctor,2.don't drink alcohol, and don't smoke."
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == "POST":
        symptom_data = request.form['symptoms']
        input_data = {
            'age': request.form['age'],
            'symptoms': symptom_data,
            'gender': request.form['gender'],
            'medical_history': request.form['medical_history'],
            'location': request.form['location'],
            'allergies': request.form['allergies']
        }

        chain_doctor = LLMChain(llm=llm_doctor, prompt=prompt_template_doctor)
        results = chain_doctor.run(input_data)

        # Extract recommendations based on the response
        # Adjust these regex patterns based on the actual response format
        match = re.search(r'Symptoms Matching Diseases:(.*?)(Medicines for Initial Relief before Meeting Doctor:)(.*?)(Do\'s Before Meeting Doctor:)(.*?)(Don\'ts Before Meeting Doctor:)(.*?)$', results, re.DOTALL)

        # Initialize lists to store recommendations
        diseases = []
        first_aid_medicines = []
        dos_before_meeting = []
        donts_before_meeting = []

        if match:
            diseases = [d.strip() for d in match.group(1).split(',')]
            first_aid_medicines = [m.strip() for m in match.group(3).split(',')]
            dos_before_meeting = [do.strip() for do in match.group(5).split(',')]
            donts_before_meeting = [dont.strip() for dont in match.group(7).split(',')]

        # Check if recommendations are empty
        if not diseases:
            diseases.append("Better contact our center physically")

        if not first_aid_medicines:
            first_aid_medicines.append("Better contact our center physically")

        if not dos_before_meeting:
            dos_before_meeting.append("Better contact our center physically")

        if not donts_before_meeting:
            donts_before_meeting.append("Better contact our center physically")

        return render_template('result.html',
                               diseases=diseases,
                               first_aid_medicines=first_aid_medicines,
                               dos_before_meeting=dos_before_meeting,
                               donts_before_meeting=donts_before_meeting)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)


