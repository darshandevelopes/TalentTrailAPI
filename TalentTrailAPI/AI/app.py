# Import Statements

import streamlit as st
from streamlit_tags import st_tags
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io, random
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
# nltk.download('punkt')
# nltk.download('stopwords')
from sklearn.feature_extraction.text import TfidfVectorizer
 

# Load the trained classifier
svcm = pickle.load(open('upsvcm.pkl', 'rb'))
ftfidfd = pickle.load(open('updatedfidf.pkl','rb'))



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

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
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


# Predict Profile
def predict_profile(resume_text):
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

def experienced(no_of_pages):
    cand_level = ''
    if no_of_pages == 1:
        cand_level = "Fresher"      
    elif no_of_pages == 2:
        cand_level = "Intermediate"       
    elif no_of_pages >= 3:
        cand_level = "Experienced"

    return cand_level

def recommended_skill(predicted_profile):
    recommended_skills=[]
    if predicted_profile == "Data Science": 
        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                              'Data Mining', 'Clustering & Classification', 'Data Analytics',
                              'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                              'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                              'Streamlit']
    elif predicted_profile == "Web Designing":
        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                              'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
    elif predicted_profile == "UI-UX Designer":
        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                              'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing',
                                              'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe',
                                              'Solid', 'Grasp', 'User Research']
    return recommended_skills

# web app
def main():
    st.title("Resume Prediction ")
    uploaded_file = st.file_uploader('Upload Resume', type=['pdf'])


    if uploaded_file  is not None:
        save_image_path = './UploadedResume/' + uploaded_file.name
        with open(save_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        resume_text = pdf_reader(save_image_path)

        # print(resume_text)
   
        #Profile_Prediction 
        predicted_profile = predict_profile(resume_text)
        st.write("Your Resume analysis says you are ", predicted_profile)

        # print("Predicted Category:", category_name)
        # print(prediction_id)

        # Resume Parsing Using PyResParser
        resume_data = ResumeParser(save_image_path).get_extracted_data()
        if resume_data:
            st.header("**Resume Analysis Using pyresparser**")
            # Experienced Level
            page = resume_data['no_of_pages']
            experienced_level =experienced(page)

            if experienced_level=="Fresher":
                st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are looking Fresher.</h4>''',
                                unsafe_allow_html=True)
            elif experienced_level == "Intermediate":
                st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',
                                unsafe_allow_html=True)
            elif experienced_level == "Experienced":
                st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',
                                unsafe_allow_html=True)

            
            # Resume Tips & Tricks
            st.subheader("**Resume Tips & Ideas**")
            if 'Objective' in resume_text:
                st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Great You have added Objective</h4>''',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Please add your career objective.</h4>''',
                        unsafe_allow_html=True)

            if 'Declaration' in resume_text:
                st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Great You have added Delcaration/h4>''',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Please add Declaration.</h4>''',
                        unsafe_allow_html=True)

            if 'Hobbies' or 'Interests' in resume_text:
                st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Please add Hobbies.</h4>''',
                        unsafe_allow_html=True)

            if 'Achievements' in resume_text:
                st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Great You have added your Achievements </h4>''',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Please add Achievements.</h4>''',
                        unsafe_allow_html=True)

            if 'Projects' in resume_text:
                st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects </h4>''',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                        '''<h4 style='text-align: left; color: #fabc10;'>[-] Please add Projects.</h4>''',
                        unsafe_allow_html=True)


            # Recommended Skills
            st.subheader("**Skills Recommendation**")
            ## Skill shows
            keywords = st_tags(label='### Skills that you have',value=resume_data['skills'], key='1')
            recommended_skills = recommended_skill(predicted_profile)          
            recommended_keywords = st_tags(label='### Recommended skills for you.', value=recommended_skills, key='2')
            st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will increase the chances of getting a Job</h4>''',
                            unsafe_allow_html=True)
    
        else:
            st.error('Something went wrong')

# python main
if __name__ == "__main__":
    main()