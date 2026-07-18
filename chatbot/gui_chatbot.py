import nltk 
from nltk.stem import WordNetLemmatizer 
lemmatizer = WordNetLemmatizer() 
import pickle 
import numpy as np 
from typing import Any 
from keras.models import load_model 
import json 
import random 
import tkinter as tk
import sqlite3
from ddgs import DDGS

# Load configurations safely
model: Any = load_model('chatbot_model.h5') 
intents = json.load(open('intents.json')) 
words = pickle.load(open('words.pkl', 'rb')) 
classes = pickle.load(open('classes.pkl', 'rb')) 

# Global state trackers for multi-turn processing memory
current_context = ""
adr_temp_data = {"drug": "", "symptom": ""}

def clean_up_sentence(sentence): 
    sentence_words = nltk.word_tokenize(sentence) 
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words] 
    return sentence_words 

def bag_of_words(sentence, words, show_details=False): 
    sentence_words = clean_up_sentence(sentence) 
    bag = [0] * len(words) 
    for s in sentence_words: 
        for i, word in enumerate(words): 
            if word == s: 
                bag[i] = 1 
    return np.array(bag) 

def predict_classes(sentence): 
    p = bag_of_words(sentence, words, show_details=False) 
    res = model.predict(np.array([p]), verbose=0)[0] 
    
    # FIX: Lowered threshold to 0.20 to catch matching local intents easily
    ERROR_THRESHOLD = 0.20  
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD] 
    
    results.sort(key=lambda x: x[1], reverse=True) 
    return_list = [] 
    for r in results: 
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])}) 
        
    # DEBUG PRINT: This will print the model's thoughts inside your terminal
    print("🤖 Model Predictions:", return_list)
    
    return return_list 

def search_internet_fallback(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
            if results:
                title = results[0].get('title', 'Web Info')
                body = results[0].get('body', '')
                url = results[0].get('href', '')
                return f"🌐 Live Web Results:\n\n\"{body}\"\n\nSource: {title} ({url})"
    except Exception as e:
        print(f"Search Error: {e}")
    return "I'm sorry, I couldn't find that in my database or on the internet. Can you retry?"

def process_database_logic(user_input, tag):
    global current_context, adr_temp_data
    
    conn = sqlite3.connect('medical_system.db')
    cursor = conn.cursor()
    
    # 1. ADR Collection Flow Step A: Store Drug Name
    if current_context == "collect_adr_drug_name":
        adr_temp_data["drug"] = user_input
        current_context = "collect_adr_symptom" 
        conn.close()
        return f"Got it, tracking side effects for '{user_input}'. What specific symptoms or reactions are you experiencing?"

    # 2. ADR Collection Flow Step B: Store Symptom, Save to SQL, and Web Lookup
    if current_context == "collect_adr_symptom":
        adr_temp_data["symptom"] = user_input
        current_context = "" 
        
        cursor.execute(
            "INSERT INTO adverse_reactions (drug_name, symptom, severity) VALUES (?, ?, ?)",
            (adr_temp_data["drug"], adr_temp_data["symptom"], "Unverified")
        )
        conn.commit()
        conn.close()
        
        search_query = f"{adr_temp_data['drug']} side effects {adr_temp_data['symptom']}"
        web_info = ""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(search_query, max_results=1))
                if results:
                    web_info = f"\n\n🩺 Live Web Clinical Context:\n\"{results[0].get('body', '')}\""
        except Exception:
            web_info = "\n\n⚠️ (Unable to establish a live connection to check alternative warning indices right now)."

        return f"✅ Incident recorded in system registry!\n💊 Medication: {adr_temp_data['drug']}\n🤢 Reported Effect: {adr_temp_data['symptom']}{web_info}"

    # 3. Pharmacy Search Flow
    if current_context == "search_pharmacy_by_name":
        current_context = "" 
        cursor.execute("SELECT address, phone FROM pharmacies WHERE name LIKE ?", (f"%{user_input}%",))
        db_res = cursor.fetchone()
        conn.close()
        if db_res:
            return f"System Registry Lookup:\n📍 Address: {db_res[0]}\n📞 Phone: {db_res[1]}"
        return f"Could not find any pharmacies matching '{user_input}'."

    # 4. Blood Pressure Record Lookup Flow
    if current_context == "search_blood_pressure_by_patient_id":
        current_context = "" 
        cursor.execute("SELECT systolic, diastolic, timestamp FROM blood_pressure WHERE patient_id = ? ORDER BY timestamp DESC", (user_input,))
        db_records = cursor.fetchall()
        conn.close()
        if db_records:
            response_text = f"Found {len(db_records)} logs for Patient {user_input}:\n"
            for row in db_records:
                response_text += f"• {row[0]}/{row[1]} mmHg (Logged: {row[2]})\n"
            return response_text
        return f"No medical logs found for Patient ID: {user_input}."

    # Update states if the user triggered a brand new intent tag path
    for intent in intents['intents']:
        if intent['tag'] == tag:
            if intent.get('context') and intent['context'] != "":
                current_context = intent['context']
    
    conn.close()
    return None

def get_response(ints, intents_json, user_input): 
    global current_context
    
    ACTIVE_CONTEXT_LIST = [
        "search_pharmacy_by_name", 
        "search_blood_pressure_by_patient_id", 
        "collect_adr_drug_name", 
        "collect_adr_symptom"
    ]
    if current_context in ACTIVE_CONTEXT_LIST:
        db_intercept_message = process_database_logic(user_input, None)
        if db_intercept_message:
            return db_intercept_message

    if not ints: 
        return search_internet_fallback(user_input)
        
    tag = ints[0]['intent'] 
    
    db_intercept_message = process_database_logic(user_input, tag)
    if db_intercept_message:
        return db_intercept_message
        
    list_of_intents = intents_json['intents'] 
    result = "I'm sorry, I don't have a response configured for that." 
    for i in list_of_intents: 
        if i['tag'] == tag: 
            if i.get('responses'): 
                result = random.choice(i['responses']) 
            break 
    return result 

# --- GUI Setup ---
def send(): 
    msg = EntryBox.get("1.0", 'end-1c').strip() 
    EntryBox.delete("1.0", tk.END) 
    
    if msg: 
        ChatLog.config(state=tk.NORMAL) 
        ChatLog.insert(tk.END, "You: " + msg + "\n\n") 
        ChatLog.config(foreground="#442265", font=("Verdana", 12)) 
        
        if current_context == "":
            ints = predict_classes(msg) 
        else:
            ints = [] 
            
        res = get_response(ints, intents, msg) 
        
        ChatLog.insert(tk.END, "Bot: " + res + "\n\n") 
        ChatLog.config(state=tk.DISABLED) 
        ChatLog.yview(tk.END) 

root = tk.Tk() 
root.title("La Chatbot") 
root.geometry("400x500") 
root.resizable(width=tk.FALSE, height=tk.FALSE) 

ChatLog = tk.Text(root, bd=0, bg='white', height=8, width=50, font="Arial") 
ChatLog.config(state="disabled") 

scrollbar = tk.Scrollbar(root, command=ChatLog.yview, cursor='heart') 
ChatLog['yscrollcommand'] = scrollbar.set 

SendButton = tk.Button(root, font=("Verdana", 12, "bold"), text="Send", width="12", height=5, 
                       bd=0, bg='#f9a602', activebackground="#3c9d9b", fg="#000000", command=send) 

EntryBox = tk.Text(root, bd=0, bg="white", width=29, height=5, font="Arial") 

scrollbar.place(x=376, y=6, height=386) 
ChatLog.place(x=6, y=6, height=386, width=370) 
EntryBox.place(x=128, y=401, height=90, width=265) 
SendButton.place(x=6, y=401, height=90) 

root.bind('<Return>', lambda event: send())
root.mainloop()
