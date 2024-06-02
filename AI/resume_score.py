# Import of pdfminer
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
import os

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
import os

AI_BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Load the trained classifier
svcm = pickle.load(open(os.path.join(AI_BASE_PATH, 'upsvcm.pkl'), 'rb'))
ftfidfd = pickle.load(open(os.path.join(AI_BASE_PATH, 'updatedfidf.pkl'),'rb'))

class ResumeAnalyzer:
    def __init__(self, resume_path, required_skills, required_jobProfile):
        self.resume_path = resume_path
        self.resume_text = self.extract_resume_text()
        self.required_skills = required_skills
        self.required_skills = required_skills
        self.min_experience = 0
        self.max_experience = 10
        self.required_jobProfile = required_jobProfile
        self.candidate_predicted_profile = self.predict_profile()

    # Extracting Features
    def extract_resume_text(self):
        resume_file = self.resume_path
        resume_file = '/home/ubuntu/talenttrailapi'+resume_file
        if os.path.exists(resume_file):
            pass
        else:
            resume_file = self.resume_path

        resource_manager = PDFResourceManager()
        with io.StringIO() as fake_file_handle:
            with TextConverter(resource_manager, fake_file_handle, laparams=LAParams()) as converter:
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                
            with open(resume_file, 'rb') as fh:
                for page in PDFPage.get_pages(fh,
                                            caching=True,
                                            check_extractable=True):
                    page_interpreter.process_page(page)
                    # print(page)

            text = fake_file_handle.getvalue()
            return text

    @staticmethod
    def clean_resume(resume_text):
        clean_text = re.sub('http\S+\s*', ' ', resume_text)
        clean_text = re.sub('RT|cc', ' ', clean_text)
        clean_text = re.sub('#\S+', '', clean_text)
        clean_text = re.sub('@\S+', '  ', clean_text)
        clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
        clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)
        clean_text = re.sub('\s+', ' ', clean_text)
        return clean_text
    
    @staticmethod
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
    def extract_resume_skill(self):
        resume_file = self.resume_path
        resume_file = '/home/ubuntu/talenttrailapi'+resume_file
        if os.path.exists(resume_file):
            pass
        else:
            resume_file = self.resume_path
        resume_data = ResumeParser(resume_file).get_extracted_data()
        candidate_skill = resume_data['skills']
        return candidate_skill

    # If skill set of pyresparser not Updates then use below function
    # to increase accuracy
    def extract_resumetext_skill(self):
        candidate_skill = self.extract_resume_skill()
        resume_text = self.resume_text
        resume_text = self.clean_resume(resume_text)
        resume_text = self.removeStopWords(resume_text)

        # Tokenization   
        tokens = word_tokenize(resume_text)
        #print(tokens)

        for rskill in self.required_skills:
            if rskill not in candidate_skill and rskill in tokens:
                candidate_skill.add(rskill)

        return candidate_skill

    @staticmethod
    def experience_matcher(candidate_experience, required_experience_min, required_experience_max):
        if candidate_experience >= required_experience_min and candidate_experience <= required_experience_max:
            return True
        return False

    @staticmethod
    def candidate_level(no_of_pages):
        cand_level = ''
        if no_of_pages == 1:
            cand_level = "Fresher"      
        elif no_of_pages == 2:
            cand_level = "Intermediate"       
        elif no_of_pages >= 3:
            cand_level = "Experienced"

        return cand_level

    @staticmethod
    def recommend_skills(predicted_profile):
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
        elif predicted_profile == 'Python Developer':
            recommended_skills = ['Pytorch', 'Tensorflow', 'Keras', 'Scikit-learn',]
        return recommended_skills

    def predict_profile(self):
        cleaned_resume = self.clean_resume(self.resume_text)
        more_cleaned = self.removeStopWords(cleaned_resume)
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

    def profile_matcher(self):
        # self.candidate_predicted_profile = self.predict_profile()
        required_profile = self.required_jobProfile

        if(self.candidate_predicted_profile  == required_profile):
            return True
        
        return False

    def resume_score(self):
        candidate_skill = self.extract_resumetext_skill()
        matched_skill_count = 0

        cv_lower = [x.lower() for x in candidate_skill]
        job_description_lower = [x.lower() for x in self.required_skills]
        print(f"cv lower {cv_lower}\njob {job_description_lower}")
        print(f"cv lower {cv_lower}\njob {job_description_lower}")
        for required_key in job_description_lower:
            if required_key in cv_lower:
                matched_skill_count += 1
        
        required_skills_count = len(self.required_skills)
        if required_skills_count > 0:
            match_percentage = ((matched_skill_count)/required_skills_count)*100
            return match_percentage
        else:
            return 0

    # Resume Score based on Resume template standard
    def resume_keyword_score(self):
        resume_score = 0

        if 'Objective' in self.resume_text:
            resume_score = resume_score + 10
        
        if 'Declaration' in self.resume_text:
            resume_score = resume_score + 10

        if 'Achievements' in self.resume_text:
            resume_score = resume_score + 10   

        if 'Projects' in self.resume_text:
            resume_score = resume_score + 15 

        if 'Hobbies' or 'Interests' in self.resume_text:
            resume_score = resume_score + 10 

        if 'Education' in self.resume_text:
            resume_score = resume_score + 10 

        if 'Skills' in self.resume_text:
            resume_score = resume_score + 20 

        if 'Work Experience' or 'Internship':
            resume_score = resume_score + 15 

        return resume_score    

    def analyze_resume_for_candidate(self):
        # Resume Parsing Using PyResParser
        resume_data = ResumeParser(self.resume_path).get_extracted_data()
        if resume_data:
            # Experienced Level
            no_of_pages = resume_data['no_of_pages']
            experienced_level = self.candidate_level(no_of_pages)

            # Resume Tips & Tricks
            resume_sections_present = {'objective': False, 'declaration': False, 'hobbies': False, 'achievements': False, 'projects': False}
            keywords = {'Objective': 'objective', 'Declaration': 'declaration', 'Hobbies': 'hobbies', 'Interests': 'hobbies', 'Achievements': 'achievements', 'Projects': 'projects'}

            for keyword, key in keywords.items():
                if keyword in self.resume_text:
                    resume_sections_present[key] = True
            
            # Recommended Skills
            candidate_skills = resume_data['skills']
            recommended_skills = self.recommend_skills(self.candidate_predicted_profile )
            return {'experienced_level': experienced_level, 'resume_sections_present': resume_sections_present, 
                    'candidate_skills': candidate_skills, 'recommended_skills': recommended_skills,
                    'candidate_predicted_profile': self.candidate_predicted_profile}

    def analyze_resume_for_hr(self):
        profile_matches = self.profile_matcher()
        score = self.resume_score()
        return {'predicted_profile':self.candidate_predicted_profile, 'does_profile_match': profile_matches, 'score': score}
    
if __name__ == "__main__":
    resume_path = os.path.join(AI_BASE_PATH, 'aws-devops-elegant-resume-example.pdf')
    analyzer = ResumeAnalyzer(resume_path, ['Java'])
    print(analyzer.analyze_resume_for_hr())
    print(analyzer.analyze_resume_for_candidate())
