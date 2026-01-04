from django.shortcuts import redirect, render
from .models import *
from django.contrib import auth
import cv2
import os
import numpy as np
import pickle
import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(
    r"D:\Main Project\VotingProject\votingmachine-9b24b-firebase-adminsdk-fbsvc-d04160a907.json"
)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://votingmachine-9b24b-default-rtdb.firebaseio.com/"
    })

def get_db():
    return db.reference("/")
DATA_DIR = "faces"
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
# messages
from django.contrib import messages
# Create your views here.
def index(request):
    return render(request, 'Index.html')
def common(request):
    return render(request, 'Common.html')
def CandidateRegistration(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        party=request.POST.get('party')
        dob=request.POST.get('dob')
        address=request.POST.get('address')
        voterid=request.POST.get('voterid')
        proof=request.FILES.get('proof')
        photo=request.FILES.get('photo')
        symbol=request.FILES.get('symbol')
        password=request.POST.get('password')
        login=CustomUser.objects.create_user(username=name,password=password,usertype='candidate',viewpassword=password)
        Candidate.objects.create(loginid=login,name=name,party=party,dob=dob,address=address,voterid=voterid,proof=proof,photo=photo,symbol=symbol)
        # Handle form submission logic here
        messages.success(request, "Candidate registered successfully.")
        pass

    return render(request, 'CadidateRegistration.html')
def capture_face_images(label_name, num_images=None):

    # Create folder for saving faces
    save_dir = os.path.join("faces", label_name)
    os.makedirs(save_dir, exist_ok=True)

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    count = 0
    print(f"Capturing faces for '{label_name}'")
    print("Press 'c' to capture face, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error grabbing frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
        )

        # Draw rectangles (for preview only)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Face Capture (Press C to save face, Q to quit)", frame)
        key = cv2.waitKey(1) & 0xFF

        # Press "c" to capture face
        if key == ord('c'):
            if len(faces) == 0:
                print("No face detected.")
                continue

            # Only crop the first detected face
            x, y, w, h = faces[0]
            face_img = gray[y:y+h, x:x+w]  # crop only face (gray recommended)

            # Resize to fixed size for training
            face_img = cv2.resize(face_img, (200, 200))

            filename = f"{label_name}_{count:04d}.jpg"
            cv2.imwrite(os.path.join(save_dir, filename), face_img)
            print(f"Saved: {filename}")
            count += 1

            if num_images and count >= num_images:
                print("Reached target number of face images.")
                break

        # Press "q" to quit
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total saved face images: {count}")
def VoterRegistration(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        dob=request.POST.get('dob')
        address=request.POST.get('address')
        photo=request.FILES.get('photo')
        voterid=request.POST.get('voterid')
        email=request.POST.get('email')
        voteridproof=request.FILES.get('voteridproof')
        password=request.POST.get('password')
        try:
            login=CustomUser.objects.create_user(username=name,password=password,usertype='voter',viewpassword=password)
            Voter.objects.create(loginid=login,name=name,dob=dob,email=email,address=address,photo=photo,voterid=voterid,voteridproof=voteridproof)
            # Handle form submission logic here
            capture_face_images(name, num_images=10)
            messages.success(request, "Voter registered successfully.")
        except Exception as e:
            messages.error(request, f"Error during registration: {e}")
        pass    
    return render(request, 'VoterRegistration.html')
def login(request):
    if request.method == 'POST':
        # Handle login logic here
        username=request.POST.get('username')
        password=request.POST.get('password')
        login=auth.authenticate(username=username,password=password)  
        if login:
            auth.login(request,login)
            request.session['username']=username
            request.session['uid']=login.id
            if login.usertype=='Admin':
                return redirect('/adminhome/')
            elif login.usertype=='candidate':
                return render(request, 'candidatehome.html')
            elif login.usertype=='voter':
            
                return redirect('/vhome/') 
            else:
                messages.error(request, "Invalid credentials") 
    return render(request, 'login.html')
def load_images_and_labels(data_dir):
    images = []
    labels = []
    label_map = {}             # name -> id
    current_id = 0

    for root, dirs, files in os.walk(data_dir):
        for dirname in dirs:
            person_name = dirname
            person_dir = os.path.join(root, dirname)

            # assign numeric id for this person
            if person_name not in label_map:
                label_map[person_name] = current_id
                current_id += 1

            person_id = label_map[person_name]

            # loop through images
            for filename in os.listdir(person_dir):
                if not (filename.lower().endswith(".jpg") or filename.lower().endswith(".png")):
                    continue

                img_path = os.path.join(person_dir, filename)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print("Could not read", img_path)
                    continue

                # resize to fixed size (same as capture)
                img = cv2.resize(img, (200, 200))

                images.append(img)
                labels.append(person_id)

    return images, labels, label_map


def vhome(request):
    print("Loading images...")
    import random
    logid=request.session['uid']
    voter=Voter.objects.get(loginid=logid)
    emaill=voter.email
    otp = random.randint(1000, 9999)
    msgge = f"Your OTP for voting is: {otp}"
    request.session['otp']=str(otp)
    ##############################################################################
    import smtplib
    import ssl
    from email.message import EmailMessage

    # Configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587  # For TLS
    SENDER_EMAIL = "safecast.evm@gmail.com"
    # Use the 16-character App Password, not your account password
    SENDER_PASSWORD = "jquo hlqa zjgj rzxo" 

    # Create the email message
    msg = EmailMessage()
    msg.set_content(msgge)
    msg["Subject"] = "OTP for Voting"
    msg["From"] = SENDER_EMAIL
    msg["To"] = emaill

    # Send the email
    context = ssl.create_default_context()

    try:
        # Connect and upgrade to secure TLS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context) 
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")




    #########################################################



    print("Your OTP is:", otp)
    images, labels, label_map = load_images_and_labels(DATA_DIR)

    if len(images) == 0:
        print("No images found in 'faces' folder.")
        exit()

    print("Number of images:", len(images))
    print("Persons and IDs:", label_map)

    # Convert to numpy arrays
    images = np.array(images)
    labels = np.array(labels)

    # Create LBPH face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    print("Training model...")
    recognizer.train(images, labels)
    print("Training finished.")

    # Save model
    recognizer.save("face_model.yml")

    # Save label map (so we can convert id -> name later)
    with open("labels.pickle", "wb") as f:
        pickle.dump(label_map, f)

    print("Model saved as face_model.yml")
    print("Labels saved as labels.pickle")


    return render(request, 'vhome.html')
def live_face_recognition(vname):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("face_model.yml") 

    # Load label map (name <-> id)
    with open("labels.pickle", "rb") as f:
        label_map = pickle.load(f)

    # Reverse mapping: id -> name
    id_to_name = {v: k for k, v in label_map.items()}
    print("Loaded labels:", id_to_name)

    # Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # ----
    cap = cv2.VideoCapture(0)   # 0 = default camera

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Live face recognition started.")
    print("Press 'q' to quit.")
    flag=1
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Convert to grayscale (LBPH works with gray images)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            # Crop face
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))

            # Predict id and confidence
            label_id, confidence = recognizer.predict(face_roi)

            # LBPH: lower confidence = better match
            # Tune this threshold as needed (try 70–100 range)
            if confidence < 80:
                
                name = id_to_name.get(label_id, "Unknown")
                if name == vname:
                    print(f"Voter '{vname}' recognized with confidence {confidence}. You may proceed to vote.")
                    flag=0
                else:
                    print(f"Face recognized as '{name}', but does not match voter '{vname}'.")  
            else:
                name = "Unknown"

            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 2)
            text = f"{name} ({int(confidence)})"
            cv2.putText(
                frame,
                text,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # Show the frame
        cv2.imshow("Live Face Recognition - Press 'q' to exit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return flag

def otpvalidation(request):
    if request.method=='POST':
        entered_otp=request.POST.get('otp')
        saved_otp=request.session['otp']
        if entered_otp==saved_otp:
            messages.success(request, "OTP verified successfully. You may proceed to face recognition.")
            return redirect('/voting/')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
    return render(request, 'otpvalidation.html')
def voting(request):

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("face_model.yml")  # trained model file

    # Load label map (name <-> id)
    with open("labels.pickle", "rb") as f:
        label_map = pickle.load(f)

    # Reverse mapping: id -> name
    id_to_name = {v: k for k, v in label_map.items()}
    print("Loaded labels:", id_to_name)

    # Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # ---------- LIVE RECOGNITION FUNCTION ----------

    if request.method == 'POST':
        # Handle voting logic here
        id=request.session['uid']
        voter=Voter.objects.get(loginid=id)
        flag=live_face_recognition(voter.name)
        if flag==0:
            messages.success(request, "Face recognized successfully. You may proceed to vote.")
        else:
            messages.error(request, "Face not recognized or does not match. Voting denied.")
        
    return render(request, 'voting.html')
def adminhome(request):

    return render(request, 'adminhome.html')
def adminviewcandidates(request):
    candidates=Candidate.objects.all()
    return render(request, 'adminviewcandidates.html',{'candidates':candidates})
def adminviewvoters(request):
    voters=Voter.objects.all()
    return render(request, 'adminviewvoters.html',{'voters':voters})
def adminviewelections(request):
    elections=Election.objects.all()
    return render(request, 'adminviewelections.html',{'elections':elections})
def adminaddelection(request):
    if request.method=='POST':
        electionname=request.POST.get('election_name')
        dateofelection=request.POST.get('start_date')
        description=request.POST.get('dis')
        Election.objects.create(electionname=electionname,dateofelection=dateofelection,description=description)
        messages.success(request, "Election added successfully.")
    return render(request, 'adminaddelection.html')
def adminviewresults(request):
    ref = get_db()
    data = ref.get()

    candidate_keys = ["CA", "CB", "CC", "CN"]
    results = {}

    for c in candidate_keys:
        value = data.get(c)
        if value:
            results[c] = int(value.replace("a", ""))

    if results:
        max_votes = max(results.values())

        winners = [c for c, v in results.items() if v == max_votes]

        if len(winners) == 1:
            winner = winners[0]
            is_draw = False
        else:
            winner = winners      # list of tied candidates
            is_draw = True
    else:
        winner = None
        is_draw = False
        max_votes = 0


    context = {
    "results": results,
    "winner": winner,
    "is_draw": is_draw,
    "max_votes": max_votes
}

    return render(request, "election_result.html", context)
    # return render(request, 'adminviewresults.html')



def election_result(request):
    ref = get_db()
    data = ref.get()

    candidate_keys = ["CA", "CB", "CC", "CN"]
    results = {}

    for c in candidate_keys:
        value = data.get(c)
        if value:
            results[c] = int(value.replace("a", ""))

    winner = max(results, key=results.get) if results else None

    context = {
        "results": results,
        "winner": winner,
        "winner_votes": results.get(winner) if winner else 0
    }

    return render(request, "election_result.html", context)
