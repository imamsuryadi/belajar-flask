
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

firebaseConfig = {
  "apiKey": "AIzaSyB4aTTl6l156EE7FN36ZOFIbWl0H10vIUg",
  "authDomain": "siakad-a425c.firebaseapp.com",
  "databaseURL": "https://siakad-a425c-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "siakad-a425c",
  "storageBucket": "siakad-a425c.appspot.com",
  "messagingSenderId": "1094095827221",
  "appId": "1:1094095827221:web:d678530cd7a760782af91c"
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

def get_all_collection(collection, orderBy=None, direction=None):
    if orderBy:
        collects_ref = db.collection(collection).order_by(
            orderBy, direction=direction)
    else:
        collects_ref = db.collection(collection)
    collects = collects_ref.stream()
    RETURN = []
    for collect in collects:
        ret = collect.to_dict()
        ret['id'] = collect.id
        RETURN.append(ret)
    return RETURN