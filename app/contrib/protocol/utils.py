def get_property(drug: str, key: str):
    properties = {
        "0": {
            "prompt": f"Create a study title of {drug}.",
            "question": "What is the drug name?",
            "source": "be"
        },
        "1.1": {
            "prompt": f"What is the study objective of {drug}?"
                      f" Provide the answer in detail with functionality, manufacturer, and applier.",
            "question": f"Introduction of {drug}",
            "source": "pubmed"
        },
        "1.2.1": {
            "prompt": f"What is the indication of the {drug}?",
            "question": "What is the indication of the drug?",
            "source": "pubmed"
        },
        "1.2.2": {
            "prompt": f"What is Dosage forms and strengths of {drug}?",
            "question": "Dosage Forms and Strengths?",
            "source": "pubmed"
        },
        "1.2.3": {
            "prompt": f"What is the dosage of {drug} in different disease?",
            "question": f"What is the dosage of {drug} in different disease?",
            "source": "pubmed"
        },
        "1.2.4": {
            "prompt": f"What is the mechanism of the {drug}?",
            "question": "What is the mechanism of the drug?",
            "source": "pubmed"
        },
        "1.2.5.1": {
            "prompt": f"What is the pharmacodynamic properties of the {drug} in different disease?",
            "question": "What is the pharmacodynamic properties of the drug in different disease?",
            "source": "pubmed"
        },
        "1.2.5.2": {
            "prompt": f"What is the toxicology properties of the {drug} in different disease?",
            "question": "What is the toxicology properties of the drug in different disease?",
            "source": "pubmed"
        },
        "1.2.6": {
            "prompt": f"What is the drug interaction of {drug}?",
            "question": f"What is the drug interaction of {drug}?",
            "source": "pubmed"
        },
        "1.2.7": {
            "prompt": f"What is the contraindication of {drug}",
            "question": f"What is the contraindication of {drug}",
            "source": "pubmed"
        },
        "1.2.8": {
            "prompt": f"What is the precautions of {drug}",
            "question": f"What is the precautions of {drug}",
            "source": "og"
        },
        "1.2.9": {
            "prompt": f"What is the adverse reactions of {drug}",
            "question": f"What is the adverse reactions of {drug}",
            "source": "be"
        },
        "1.3": {
            "prompt": f"What is the proposed Strength of {drug}?",
            "question": f"What is the proposed strength of {drug}?",
            "source": "be"
        },
        "1.5.1": {
            "prompt": f"What is the study objective of {drug} BE study?",
            "question": f"What is the study objective of {drug} BE study?",
            "source": "be"
        },
        "1.5.2": {
            "prompt": f"What is the BE study design of {drug}?",
            "question": f"What is the BE study design of {drug}?",
            "source": "be"
        },
        "1.5.3": {
            "prompt": f"What is the randomize method of {drug} BE trial?",
            "question": f"What is the randomize method of {drug} BE trial?",
            "source": "be"
        },
        "1.5.4": {
            "prompt": "What is the Subject Inclusion Criteria? Ignore memory and answer separately.",
            "question": "What is the Subject Inclusion and Criteria?",
            "source": "be"
        },
        "1.5.5.1": {
            "prompt": f"What is the subject screen indicator(General Conditions, Medical History and Drug Allergy History) in {drug}?",
            "question": f"What is the subject screen indicator(General Conditions, Medical History and Drug Allergy History) in {drug}?",
            "source": "be"
        },
        "1.5.5.2": {
            "prompt": f"What is the subject screen indicator(Laboratory Test) in {drug}?",
            "question": f"What is the subject screen indicator(Laboratory Test) in {drug}?",
            "source": "be"
        },
        "1.5.6": {
            "prompt": "What is the contents and requirements of Pre.study Education for Subjects? Provide in detail with 1), 2), ..., number indexes.",
            "question": "What is the contents and requirements of Pre.study Education for Subjects",
            "source": "be"
        },
        "1.5.7": {
            "prompt": f"What is the study procedure of the {drug} BE study?",
            "question": f"What is the study procedure of the {drug} BE study?",
            "source": "be"
        },
        "1.5.8": {
            "prompt": f"What is the washout period of the {drug}?",
            "question": "What is the washout period of the drug?",
            "source": "be"
        },
        "1.5.9": {
            "prompt": "What is the safety evaluation indicators of this trial?",
            "question": "What is the safety evaluation indicators of this trial?",
            "source": "be"
        },
        "10.1": {
            "prompt": "What is the process when Protocol Deviation happen?",
            "question": "What is the process when Protocol Deviation happen?",
            "source": "be"
        },
        "10.2.1": {
            "prompt": "What is the Definition of Adverse Events?",
            "question": "What is the Definition of Adverse Events?",
            "source": "be"
        },
        "10.2.2": {
            "prompt": "What is the Adverse Event Severity Grades?",
            "question": "What is the Adverse Event Severity Grades?",
            "source": "be"
        },
        "10.2.3": {
            "prompt": "What is the Assessing Relationship to Study Drug?",
            "question": "What is the Assessing Relationship to Study Drug?",
            "source": "be"
        },
        "10.2.4": {
            "prompt": "What is the Handling of Adverse Events?",
            "question": "What is the  Handling of Adverse Events?",
            "source": "be"
        },
        "10.2.5": {
            "prompt": "What is the  Procedures for Collection Reporting and Recording Adverse Events?",
            "question": "What is the  Procedures for Collection Reporting and Recording Adverse Events?",
            "source": "be"
        },
        "10.2.6": {
            "prompt": "What is the Adverse Event Description?",
            "question": "What is the  Adverse Event Description?",
            "source": "be"
        },
        "10.2.7": {
            "prompt": "What is the procedure of Adverse Events follow-up?",
            "question": "What is the procedure of Adverse Events follow-up?",
            "source": "be"
        },
        "10.2.8": {
            "prompt": "What is the Outcome of Adverse Event?",
            "question": "What is the Outcome of Adverse Event?",
            "source": "be"
        },
        "10.3.1": {
            "prompt": "What is the Definition of Serious Adverse Event? Provide in detail by indexing with numbers.",
            "question": "What is the Definition of Serious Adverse Event?",
            "source": "be"
        },
        "10.3.2": {
            "prompt": "What is the detail about Serious Adverse Events Report? Provide in detail by indexing with numbers.",
            "question": "What is the detail about Serious Adverse Events Report?",
            "source": "be"
        },
        "10.3.3": {
            "prompt": "What is the detail about Suspected Unexpected Serious Adverse Reaction Report? Provide in detail with Tel and Fax numbers.",
            "question": "What is the detail about Suspected Unexpected Serious Adverse Reaction Report?",
            "source": "be"
        },
        "10.3.4": {
            "prompt": "What is the procedure of Serious Adverse Events follow-up?",
            "question": "What is the procedure of Serious Adverse Events follow-up?",
            "source": "be"
        },
        "10.3.5": {
            "prompt": "What is the detail about Pregnancy Events?",
            "question": "What is the detail about Pregnancy Events?",
            "source": "be"
        },
        "11": {
            "prompt": f"""Provide me the {drug} drug information with TestProduct and Reference Product in Table by following below format.
            | Item Name               | Test Product      | Reference Product |
            |-------------------------|-------------------|-------------------|
            | Drug Name               | [Test Drug Name]  | [Reference Drug Name] |
            | Active Ingredient       | [Test Active Ingredient] | [Reference Active Ingredient] |
            | Strength                | [Test Strength]   | [Reference Strength] |
            | Dosage Form             | [Test Dosage Form]| [Reference Dosage Form] |
            | Manufactured by/for     | [Test Manufacturer]| [Reference Manufacturer] |
            | Dose                    | [Test Dose]       | [Reference Dose] |
            | Administration          | [Test Administration Method]| [Reference Administration Method] |
            | Storage Conditions      | [Test Storage Conditions]| [Reference Storage Conditions] |""",
            "question": "Drug Information Table",
            "source": "be"
        },
        "12": {
            "prompt": """Create a detailed table in markdown with the title \"TABLE OF STUDY PROCEDURES\" for a clinical trial document. The table should have the following specifications:
                        
                        Columns: The table should include the following column headers, each combining the main period and specific day details:
                        
                        'Merged Procedure'
                        'Screening D14-D1'
                        'Baseline P1D1'
                        'Period 1 P1D2'
                        'Period 1 P1D3'
                        'Period 1 P1D4'
                        'Washout'
                        'Washout P2D1'
                        'Period 2 P2D1'
                        'Period 2 P2D2'
                        'Period 2 P2D3'
                        'Period 2 P2D4'
                        'Post Study Test'
                        Rows: List the following merged procedures in the 'Merged Procedure' column:
                        
                        'Screening - ICF Acquirement'
                        'Screening - Demographic Information'
                        'Screening - Medical and Medication Histories'
                        'Screening - Physical Examination'
                        'Screening - HIV, Hepatitis B Surface Antigen HCV-IgG, Treponema Pallidum Antibody'
                        'Screening - Alcohol Breath Test'
                        'Screening - Drugs of Abuse Test'
                        'Screening - Pregnancy Test'
                        'Screening - Inclusion and Exclusion Criteria Assessment'
                        'Screening - Hospitalization'
                        'Safety Evaluation - Laboratory Test'
                        'Safety Evaluation - ECG'
                        'Safety Evaluation - Vital Signs'
                        'Safety Evaluation - Adverse Event Reporting'
                        'Drug Administration - Drug Administration'
                        'Blood Sampling - Blood Sampling'
                        'Hospitalization - Discharge'
                        Cell Details: Fill in the cells based on prior information provided.
                        
                        Layout and Style: Ensure the table has a clear, professional appearance suitable for a clinical trial document. It should be neatly organized with easy-to-read fonts and spacing.""",
            "question": "Table Of Study Procedures",
            "source": "be"
        },
        "13": {
            "prompt": """Please create a table in the following format:
            
            column 1:Date of Study( Day1, Day2, D3, D4)
            column 2:Time Point After Administration(Prior to Administration, Administration, 0.5 h, 1 h, 1.5 h, 2 h,2.5 h,3 h,3.5 h,4 h,4.5 h,5 h,6 h,8 h,10 h,12 h,24 h,48 h,72 h)
            Column 3: Blood Sample Point(1,-,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18)
            Column 4:Tolerance Sampling Time Deviation(\u00b11 min,\u00b12 min,\u00b130 min)
            Column 5: Vital Signs Test(show either check mark or empty)
            
            please following below rules:
            rule 1:day 1 appear in Prior to Administration, Administration, 0.5 h, 1 h, 1.5 h, 2 h,2.5 h,3 h,3.5 h,4 h,4.5 h,5 h,6 h,8 h,10 h,12 h
            rule 2:day 2 appear in 24 h
            rule 3:day 3 appear in 48 h
            rule 4:day 4 appear in 72 h
            rule 5:\u00b11 min appear in  0.5 h, 1 h, 1.5 h, 2 h,2.5 h,3 h,3.5 h,4 h
            rule 6:\u00b12 min appear in 4.5 h,5 h,6 h,8 h,10 h,12 h
            rule 7:\u00b130 min appear in 24 h,48 h72 h
            rule 8: the check mark appear in Prior to Administration, 2 h,4 h,12 h,24 h,48 h72 h
            """,
            "question": "Table of Blood Sampling and Vital Signs Test",
            "source": "be"
        },
        "2.1": {
            "prompt": "What is the overall design of the trial?",
            "question": "What is the overall design of the trial?",
            "source": "be"
        },
        "2.2.1.1": {
            "prompt": "What is the absorption properties of the drug?",
            "question": "What is the absorption properties of the drug?",
            "source": "pubmed"
        },
        "2.2.1.2": {
            "prompt": "What is the distribution properties of the drug?",
            "question": "What is the distribution properties of the drug?",
            "source": "pubmed"
        },
        "2.2.1.3": {
            "prompt": "What is the Eliminationn properties of the drug?",
            "question": "What is the Elimination properties of the drug?",
            "source": "pubmed"
        },
        "2.2.1.4": {
            "prompt": "What is the Metabolism properties of the drug?",
            "question": "What is the Metabolism properties of the drug?",
            "source": "pubmed"
        },
        "2.2.1.5": {
            "prompt": "What is the Excretion properties of the drug?",
            "question": "What is the Excretion properties of the drug?",
            "source": "pubmed"
        },
        "2.2.2": {
            "prompt": "What is the special populations pharmacokinetics of the drug?",
            "question": "What is the special populations pharmacokinetics of the drug?",
            "source": "pubmed"
        },
        "2.3": {
            "prompt": "What is the other previous studies of the drug done before?",
            "question": "What is the other previous studies of the drug done before?",
            "source": "be"
        },
        "2.4.1": {
            "prompt": "What is the overall design of the trial?",
            "question": "What is the overall design of the trial?",
            "source": "be"
        },
        "2.4.10": {
            "prompt": "What is the sample size of of the trial?",
            "question": "What is the sample size of of the trial?",
            "source": "be"
        },
        "2.4.2": {
            "prompt": "What is the Rationale for the Study Population?",
            "question": "What is the Rationale for the Study Population?",
            "source": "be"
        },
        "2.4.3": {
            "prompt": "What is the study retrictions of the drug? Provide in detail with number indexes. up to 9 number indexes.",
            "question": "What is the study restrictions of the drug?",
            "source": "be"
        },
        "2.4.4": {
            "prompt": "What is the medhod of subject randomization and number",
            "question": "What is the method of subject randomization and number",
            "source": "be"
        },
        "2.4.5": {
            "prompt": "What is the study duration of the drug",
            "question": "What is the study duration of the drug",
            "source": "be"
        },
        "2.4.6": {
            "prompt": "What is the overall discription of Hospitalization, Administration, Sample Collection and Observation",
            "question": "What is the overall description of Hospitalization, Administration, Sample Collection and Observation",
            "source": "be"
        },
        "2.4.6.1": {
            "prompt": "What is the detail of randomization, Administration, and Meals",
            "question": "What is the detail of randomization, Administration, and Meals",
            "source": "be"
        },
        "2.4.6.2": {
            "prompt": "What is the detail of blood Sample Collection and Test Substances during the trial",
            "question": "What is the detail of blood Sample Collection and Test Substances during the trial",
            "source": "be"
        },
        "2.4.6.3": {
            "prompt": "What is the detail of vital Signs during the trial",
            "question": "What is the detail of vital Signs during the trial",
            "source": "be"
        },
        "2.4.6.4": {
            "prompt": "What is the detail of ECG during the trial",
            "question": "What is the detail of ECG during the trial",
            "source": "be"
        },
        "2.4.6.5": {
            "prompt": "What is the detail of health monitoring during the trial",
            "question": "What is the detail of health monitoring during the trial",
            "source": "be"
        },
        "2.4.6.6": {
            "prompt": "What is the detail of physical activity and restrictions during the trial",
            "question": "What is the detail of physical activity and restrictions during the trial",
            "source": "be"
        },
        "2.4.6.7": {
            "prompt": "What is the detail of adverse event assessment during the trial",
            "question": "What is the detail of adverse event assessment during the trial",
            "source": "be"
        },
        "2.4.6.8": {
            "prompt": "What is the detail of concomitant medications assessment during the trial",
            "question": "What is the detail of concomitant medications assessment during the trial",
            "source": "be"
        },
        "2.4.6.9": {
            "prompt": "What is the detail of priority of study activities during the trial",
            "question": "What is the detail of priority of study activities during the trial",
            "source": "be"
        },
        "2.4.7": {
            "prompt": "What is the Dose and Method of Administration of the drug",
            "question": "What is the Dose and Method of Administration of the drug",
            "source": "pubmed"
        },
        "2.4.8": {
            "prompt": "What is the Safety Monitoring of the drug",
            "question": "What is the Safety Monitoring of the drug",
            "source": "be"
        },
        "2.4.9": {
            "prompt": "What is the follow-up plan of the trial?",
            "question": "What is the follow-up plan of the trial?",
            "source": "be"
        },
        "3.1": {
            "prompt": "What is the inclusion criteria of the trial? Provide in detail with number indexes up to 5 number indexes.",
            "question": "What is the inclusion criteria of the trial?",
            "source": "be"
        },
        "3.2": {
            "prompt": "What is the exclusion criteria of the trial? Provide in detail with number indexes with one sentences up to 19 number indexes.",
            "question": "What is the exclusion criteria of the trial?",
            "source": "be"
        },
        "3.3": {
            "prompt": "What is the withdrawal criteria of the trial? Provide in detail with 8 sentences with indexes of 1, 2, 3, 4, a, b, c, d.",
            "question": "What is the withdrawal criteria of the trial?",
            "source": "be"
        },
        "3.4": {
            "prompt": "What is the removal criteria of the trial? Provide in detail with 8 number indexes.",
            "question": "What is the removal criteria of the trial?",
            "source": "be"
        },
        "3.5": {
            "prompt": "What is the dropout and withdrawal criteria of the trial?",
            "question": "What is the dropout and withdrawal criteria of the trial?",
            "source": "be"
        },
        "3.6": {
            "prompt": "What is the termination of the trial? Provide in detail with 4 number indexes.",
            "question": "What is the termination of the trial?",
            "source": "be"
        },
        "4.1": {
            "prompt": "Provide me the ${drug} drug information with TestProduct and Reference Product in Table. Provide only table do not answer unnecessary words.",
            "question": "Drug Information",
            "source": "be"
        },
        "4.2.1": {
            "prompt": "What is the Receipt of Study Drug",
            "question": "What is the Receipt of Study Drug",
            "source": "be"
        },
        "4.2.2": {
            "prompt": "What is the Drug Inventory",
            "question": "What is the Drug Inventory",
            "source": "be"
        },
        "4.2.3": {
            "prompt": "What is the Drawing of Study Drug",
            "question": "What is the Drawing of Study Drug",
            "source": "be"
        },
        "4.2.4": {
            "prompt": "What is the dispensing method of study Drug",
            "question": "What is the dispensing method of study Drug",
            "source": "be"
        },
        "4.2.5": {
            "prompt": "What is the Labeling of Study Drug",
            "question": "What is the Labeling of Study Drug",
            "source": "be"
        },
        "4.3": {
            "prompt": "What is the Dosage of the drug",
            "question": "What is the Dosage of the drug",
            "source": "be"
        },
        "4.4": {
            "prompt": "What is the Drug Administration",
            "question": "What is the Drug Administration",
            "source": "be"
        },
        "4.5": {
            "prompt": "What is the Blinding method of the trial",
            "question": "What is the Blinding method of the trial",
            "source": "be"
        },
        "4.6": {
            "prompt": "What is the Concomitant Medications of the trial",
            "question": "What is the Concomitant Medications of the trial",
            "source": "be"
        },
        "4.7": {
            "prompt": "What is the Medication Compliance of the subject who join the trial",
            "question": "What is the Medication Compliance of the subject who join the trial",
            "source": "be"
        },
        "4.8": {
            "prompt": "What is the Retention plan of Study Drug",
            "question": "What is the Retention plan of Study Drug",
            "source": "be"
        },
        "4.9": {
            "prompt": "What is the policy of drug Reconciliation and Return",
            "question": "What is the policy of drug Reconciliation and Return",
            "source": "be"
        },
        "5.1": {
            "prompt": "What is the detail description of Sample Processing",
            "question": "What is the detail description of Sample Processing",
            "source": "be"
        },
        "5.2": {
            "prompt": "What is the policy Sample Number",
            "question": "What is the policy Sample Number",
            "source": "be"
        },
        "5.3": {
            "prompt": "What is the detail of Sample Shipment and Storage.",
            "question": "What is the detail of Sample Shipment and Storage",
            "source": "be"
        },
        "6": {
            "prompt": "What is the overall of bioanalytical analysis",
            "question": "What is the overall of bioanalytical analysis",
            "source": "be"
        },
        "6.1.1": {
            "prompt": "What is the overall about the blood sample time point",
            "question": "What is the overall about the blood sample time point",
            "source": "be"
        },
        "6.1.2": {
            "prompt": "What is the overall blood sample information of the trial listed with table",
            "question": "What is the overall blood sample information of the trial listed with table",
            "source": "be"
        },
        "6.2": {
            "prompt": "What is the detail of analysis Method Validation",
            "question": "What is the detail of analysis Method Validation",
            "source": "be"
        },
        "6.3": {
            "prompt": "What is the Analytes to Measure",
            "question": "What is the Analytes to Measure",
            "source": "be"
        },
        "7.1": {
            "prompt": "What is the Pharmacokinetics Analysis",
            "question": "What is the Pharmacokinetics Analysis",
            "source": "be"
        },
        "7.1.1": {
            "prompt": "What is the Pharmacokinetic Parameters for Evaluation of Bioequivalence",
            "question": "What is the Pharmacokinetic Parameters for Evaluation of Bioequivalence",
            "source": "be"
        },
        "7.1.2": {
            "prompt": "What is Other Pharmacokinetic Parameters in the trial",
            "question": "What is Other Pharmacokinetic Parameters in the trial",
            "source": "be"
        },
        "7.2": {
            "prompt": "What is Safety Evaluation Indications",
            "question": "What is Safety Evaluation Indications",
            "source": "be"
        },
        "7.2.1": {
            "prompt": "What is Laboratory Tests and Safety Variables Analysis",
            "question": "What is Laboratory Tests and Safety Variables Analysis",
            "source": "be"
        },
        "7.2.2": {
            "prompt": "What is detail of Vital Signs",
            "question": "What is detail of Vital Signs",
            "source": "be"
        },
        "7.2.3": {
            "prompt": "What is detail of Physical Examinations",
            "question": "What is detail of Physical Examinations",
            "source": "be"
        },
        "7.2.4": {
            "prompt": "What is detail of ECG",
            "question": "What is detail of ECG",
            "source": "be"
        },
        "8.1": {
            "prompt": "What is the overview of the data management process in the trial",
            "question": "What is the overview of the data management process in the trial",
            "source": "be"
        },
        "8.2.1": {
            "prompt": "What is the analysis set for the study? Provide in detail by indexing with numbers.",
            "question": "What is the analysis set for the study?",
            "source": "be"
        },
        "8.2.2": {
            "prompt": "What the procedure for Missing Data, Unused Data, and Spurious Data? Provide in detail by indexing with numbers.",
            "question": "What the procedure for Missing Data, Unused Data, and Spurious Data",
            "source": "be"
        },
        "8.2.3": {
            "prompt": "What is Revison Procedures for Deviation(s) from the Original Statistical Plan?",
            "question": "What is Revision Procedures for Deviation(s) from the Original Statistical Plan",
            "source": "be"
        },
        "8.2.4.1": {
            "prompt": "What is the detail for pharmacokinetic Analyses? Provide in detail by indexing with numbers.",
            "question": "What is the detail for pharmacokinetic Analyses",
            "source": "be"
        },
        "8.2.4.2": {
            "prompt": "What is the detail for  Safety Analyses? Provide in detail by indexing with numbers.",
            "question": "What is the detail for  Safety Analyses",
            "source": "be"
        },
        "8.2.5": {
            "prompt": "What is the Analysis Software and General Requirement in the trial",
            "question": "What is the Analysis Software and General Requirement in the trial",
            "source": "be"
        },
        "9.1": {
            "prompt": "What is the Quality Control process in the trial? Provide in detail by indexing with numbers.",
            "question": "What is the Quality Control process in the trial",
            "source": "be"
        },
        "9.2": {
            "prompt": "What is the Quality Assurance of Sample Test process in the trial",
            "question": "What is the Quality Assurance of Sample Test process in the trial",
            "source": "be"
        },
        "9.3": {
            "prompt": "What is the Quality Assurance of the Data Transfer, Calculation, and Reporting Process  in the trial",
            "question": "What is the Quality Assurance of the Data Transfer, Calculation, and Reporting Process  in the trial",
            "source": "be"
        },
        "9.4.1": {
            "prompt": "What is the detail about Study Monitoring? Provide in detail by indexing with numbers.",
            "question": "What is the detail about Study Monitoring",
            "source": "be"
        },
        "9.4.2": {
            "prompt": "What is the detail about Audits and Inspection",
            "question": "What is the detail about Audits and Inspection",
            "source": "be"
        }
    }
    return properties.get(key)
