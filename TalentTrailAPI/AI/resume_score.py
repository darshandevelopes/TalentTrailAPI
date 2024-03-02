# Import of pdfminer
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io

#Import of NLTK & Presparser
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from pyresparser import ResumeParser
# nltk.download('punkt')
# nltk.download('stopwords')
from sklearn.feature_extraction.text import TfidfVectorizer
import os

AI_BASE_PATH = '/home/darshan/Desktop/talenttrail-backend/TalentTrailAPI/AI/' 

#INPUT FROM HR

def get_required_skill():
    requires_skill = []
    return requires_skill

def get_required_experience():
    min_experience=0
    max_experience =10

    return min_experience ,max_experience

def get_required_jobProfile():
    
    required_jobProfile =" "
    return required_jobProfile

#INPUT FROM CANDIDATE 

# DOCUMENT Candidate_Resume(in pdf,doc) 
def get_candidate_resume():
    uploaded_file = os.path.join(AI_BASE_PATH, 'aws-devops-elegant-resume-example.pdf') 
    #     save_image_path = './UploadedResume/' + uploaded_file.name
    #     with open(save_image_path, "wb") as f:
    #         f.write(uploaded_file.getbuffer())
        
    return uploaded_file 

#INTEGER Candidate_Experience 
def get_candidate_experience():
    # take input & return  experience
    return 0

# Extracting Features
def extract_resume_text():
    resume_file = get_candidate_resume()
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(resume_file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

# Cleaning the data
def clean_resume(resume_text):
    clean_text = re.sub('http\S+\s*', ' ', resume_text)
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\S+', '', clean_text)
    clean_text = re.sub('@\S+', '  ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)
    clean_text = re.sub('\s+', ' ', clean_text)
    return clean_text

def removeStopWords(txt):
    SetOfStopWords= set(stopwords.words('english')+['``',"''"])
    word_tokens = word_tokenize(txt)
    filtered_sentence = [w for w in word_tokens if not w.lower() in SetOfStopWords and w not in string.punctuation]
    filtered_sentence = []
    for w in word_tokens:
        if w not in SetOfStopWords:
            filtered_sentence.append(w)
    listToStr = ' '.join(map(str, filtered_sentence))
    return listToStr

# Extraction of Skill using pyresparser
def extract_resume_skill():
    resume_file = get_candidate_resume()
    resume_data = ResumeParser(resume_file).get_extracted_data()
    candidate_skill = resume_data['skills']
    return candidate_skill

# If skill set of pyresparser not Updates then use below function
# to increase accuracy
def extract_resumetext_skill():
    candidate_skill = extract_resume_skill()
    required_skill = get_required_skill()
    resume_text = extract_resume_text()
    resume_text = clean_resume(resume_text)
    resume_text = removeStopWords(resume_text)

    # Tokenization   
    tokens = word_tokenize(resume_text)
    #print(tokens)

    for required in required_skill:
        if required not in candidate_skill and required in tokens:
            candidate_skill.add(required_skill)

    return candidate_skill

# Experience Matched or Not
def experience_matcher(candidate_experience, required_experience_min, required_experience_max):
    if candidate_experience >= required_experience_min and candidate_experience <= required_experience_max:
        return True
    return False

# Predict Profile

def predict_profile(resume_text):
    # Load the trained classifier
    svcm = pickle.load(open(os.path.join(AI_BASE_PATH, 'upsvcm.pkl'), 'rb'))
    ftfidfd = pickle.load(open(os.path.join(AI_BASE_PATH, 'updatedfidf.pkl'),'rb'))

    cleaned_resume = clean_resume(resume_text)
    more_cleaned = removeStopWords(cleaned_resume)
    #Removing stopwords
    # Transform the cleaned resume using the trained TfidfVectorizer
    input_features = ftfidfd.transform([more_cleaned ])

    # Make the prediction using the loaded classifier
    prediction_id = svcm.predict(input_features)[0]

    # Map category ID to category name
    category_mapping = {
            15: "Java Developer",
            23: "Testing",
            8: "DevOps Engineer",
            20: "Python Developer",
            24: "Web Designing",
            12: "HR",
            13: "Hadoop",
            3: "Blockchain",
            10: "ETL Developer",
            18: "Operations Manager",
            6: "Data Science",
            22: "Sales",
            16: "Mechanical Engineer",
            1: "UI-UX Designer",
            7: "Database",
            11: "Electrical Engineering",
            14: "Health and fitness",
            19: "PMO",
            4: "Business Analyst",
            9: "DotNet Developer",
            2: "Automation Testing",
            17: "Network Security Engineer",
            21: "SAP Developer",
            5: "Civil Engineer",
            0: "Advocate",
        }

    category_name = category_mapping.get(prediction_id, "Unknown")
    return category_name

def profile_matcher():
    resume_text = extract_resume_text()
    candidate_profile = predict_profile(resume_text)
    required_profile = get_required_jobProfile()

    if(candidate_profile == required_profile):
        return True
    
    return False

def resume_score(required_skill):
    candidate_skill = extract_resumetext_skill()
    matched_skill_count = 0

    cv_lower = [x.lower() for x in candidate_skill]
    job_description_lower = [x.lower() for x in required_skill]

    for required_key in job_description_lower:
        if required_key in cv_lower:
            matched_skill_count += 1
    
    required_skill_count = len(required_skill)
    match_percentage = ((matched_skill_count)/required_skill_count)*100

    return match_percentage

# def resume_status():
#     isProfileMatch = profile_matcher()

#     isExperienceMatch = experience_matcher()
#     required_skill = get_required_skill()
#     match_percentage = resume_score(required_skill)

#     if isProfileMatch and isExperienceMatch:
#         print("Profile & Experience Matched & Resume Score is", match_percentage)
#     elif isProfileMatch:
#        print("Experience does Not Matched & Resume Score is", match_percentage)
#     else:
#        print("Profile & Experience does Not Matched & Resume Score is", match_percentage)

# Resume Score based on Resume template standard
def resume_keyword_score():
    resume_text = extract_resume_text()
    resume_score = 0

    if 'Objective' in resume_text:
                    resume_score = resume_score + 10
    
    if 'Declaration' in resume_text:
                    resume_score = resume_score + 10

    if 'Achievements' in resume_text:
                    resume_score = resume_score + 10   

    if 'Projects' in resume_text:
                    resume_score = resume_score + 15 

    if 'Hobbies' or 'Interests' in resume_text:
                    resume_score = resume_score + 10 

    if 'Education' in resume_text:
                    resume_score = resume_score + 10 

    if 'Skills' in resume_text:
                    resume_score = resume_score + 20 

    if 'Work Experience' or 'Internship':
                    resume_score = resume_score + 15 


    return resume_score    


if __name__ == "__main__":
       print(20*'*')
       print( predict_profile(extract_resume_text()) )
       print(20*'*')
       print( profile_matcher() )
       print(20*'*')
       print( resume_score(['Java', 'Springboot', 'Servlet', 'AWS']) )
       print(20*'*')
       











