from app.contrib.protocol.utils import get_property

data = [
    {
        "key": "1",
        "label": "Introduction",
        "children": [
            {
                "key": "1.1",
                "label": "Study Rationale",
                "children": []
            },
            {
                "key": "1.2",
                "label": "Drug Information and Indication",
                "children": [
                    {
                        "key": "1.2.1",
                        "label": "Indication of the drug",
                        "children": []
                    },
                    {
                        "key": "1.2.2",
                        "label": "Dosage Forms and Strengths",
                        "children": []
                    },
                    {
                        "key": "1.2.3",
                        "label": "Dosage of Drug in different disease",
                        "children": []
                    },
                    {
                        "key": "1.2.4",
                        "label": "Mechanism of Action",
                        "children": []
                    },
                    {
                        "key": "1.2.5",
                        "label": "Pharmacodynamics and Toxicology",
                        "children": [
                            {
                                "key": "1.2.5.1",
                                "label": "Pharmacodynamic properties",
                                "children": []
                            },
                            {
                                "key": "1.2.5.2",
                                "label": "Toxicology properties",
                                "children": []
                            }
                        ]
                    },
                    {
                        "key": "1.2.6",
                        "label": "Drug interaction",
                        "children": []
                    },
                    {
                        "key": "1.2.7",
                        "label": "Condition of Drug",
                        "children": []
                    },
                    {
                        "key": "1.2.8",
                        "label": "Precautions of Drug",
                        "children": []
                    },
                    {
                        "key": "1.2.9",
                        "label": "Adverse reactions of Drug",
                        "children": []
                    }
                ]
            },
            {
                "key": "1.3",
                "label": "Reference Drug",
                "children": []
            },
            {
                "key": "1.4",
                "label": "Proposed Strengths",
                "children": []
            },
            {
                "key": "1.5",
                "label": "Study Contents",
                "children": [
                    {
                        "key": "1.5.1",
                        "label": "Objective",
                        "children": []
                    },
                    {
                        "key": "1.5.2",
                        "label": "Design",
                        "children": []
                    },
                    {
                        "key": "1.5.3",
                        "label": "Randomize Method",
                        "children": []
                    },
                    {
                        "key": "1.5.4",
                        "label": "Subject Inclusion Criteria",
                        "children": []
                    },
                    {
                        "key": "1.5.5",
                        "label": "Screening Indicators",
                        "children": [
                            {
                                "key": "1.5.5.1",
                                "label": "General Conditions, Medical History, and Drug Allergy History",
                                "children": []
                            },
                            {
                                "key": "1.5.5.2",
                                "label": "Laboratory Test",
                                "children": []
                            }
                        ]
                    },
                    {
                        "key": "1.5.6",
                        "label": "Contents and Requirements of Pre.study Education for Subjects",
                        "children": []
                    },
                    {
                        "key": "1.5.7",
                        "label": "Study Procedures",
                        "children": []
                    },
                    {
                        "key": "1.5.8",
                        "label": "Washout Period",
                        "children": []
                    },
                    {
                        "key": "1.5.9",
                        "label": "Safety Evaluation Indicators",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "2",
        "label": "Rationale For Study Design",
        "children": [
            {
                "key": "2.1",
                "label": "Overall Design of the Study",
                "children": []
            },
            {
                "key": "2.2",
                "label": "Pharmacokinetics Properties",
                "children": [
                    {
                        "key": "2.2.1",
                        "label": "Different types of the Properties",
                        "children": [
                            {
                                "key": "2.2.1.1",
                                "label": "Absorption Properties",
                                "children": []
                            },
                            {
                                "key": "2.2.1.2",
                                "label": "Distribution Properties",
                                "children": []
                            },
                            {
                                "key": "2.2.1.3",
                                "label": "Elimination Properties",
                                "children": []
                            },
                            {
                                "key": "2.2.1.4",
                                "label": "Metabolism Properties",
                                "children": []
                            },
                            {
                                "key": "2.2.1.5",
                                "label": "Excretion Properties",
                                "children": []
                            }
                        ]
                    },
                    {
                        "key": "2.2.2",
                        "label": "Special Populations Pharmacokinetics",
                        "children": []
                    }
                ]
            },
            {
                "key": "2.3",
                "label": "Previous Studies",
                "children": []
            },
            {
                "key": "2.4",
                "label": "Detailed Protocol Design",
                "children": [
                    {
                        "key": "2.4.1",
                        "label": "Overall Design",
                        "children": []
                    },
                    {
                        "key": "2.4.2",
                        "label": "Rationale Design",
                        "children": []
                    },
                    {
                        "key": "2.4.3",
                        "label": "Study retrictions Design",
                        "children": []
                    },
                    {
                        "key": "2.4.4",
                        "label": "Method of Subject Randomization and Number",
                        "children": []
                    },
                    {
                        "key": "2.4.5",
                        "label": "Study Duration",
                        "children": []
                    },
                    {
                        "key": "2.4.6",
                        "label": "Hospitalization, Administration, Sample Collection and Observation",
                        "children": [
                            {
                                "key": "2.4.6.1",
                                "label": "Detail of Randomization, Administration, and Meals",
                                "children": []
                            },
                            {
                                "key": "2.4.6.2",
                                "label": "Detail of blood sample collection and test substances",
                                "children": []
                            },
                            {
                                "key": "2.4.6.3",
                                "label": "Detail of vital signs",
                                "children": []
                            },
                            {
                                "key": "2.4.6.4",
                                "label": "Detail of ECG",
                                "children": []
                            },
                            {
                                "key": "2.4.6.5",
                                "label": "Detail of health monitoring",
                                "children": []
                            },
                            {
                                "key": "2.4.6.6",
                                "label": "Detail of physical activity and restrictions",
                                "children": []
                            },
                            {
                                "key": "2.4.6.7",
                                "label": "Detail of adverse event assessment",
                                "children": []
                            },
                            {
                                "key": "2.4.6.8",
                                "label": "Detail of concomitant medications assessment",
                                "children": []
                            },
                            {
                                "key": "2.4.6.9",
                                "label": "Detail of priprity of study activities",
                                "children": []
                            }
                        ]
                    },
                    {
                        "key": "2.4.7",
                        "label": "Dose and Method of Administration",
                        "children": []
                    },
                    {
                        "key": "2.4.8",
                        "label": "Safety Monitoring",
                        "children": []
                    },
                    {
                        "key": "2.4.9",
                        "label": "follow-up plan",
                        "children": []
                    },
                    {
                        "key": "2.4.10",
                        "label": "Sample size",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "3",
        "label": "Subject Selection",
        "children": [
            {
                "key": "3.1",
                "label": "Inclusion Criteria",
                "children": []
            },
            {
                "key": "3.2",
                "label": "Exclusion Criteria",
                "children": []
            },
            {
                "key": "3.3",
                "label": "Withdrawal Criteria",
                "children": []
            },
            {
                "key": "3.4",
                "label": "Removal Criteria",
                "children": []
            },
            {
                "key": "3.5",
                "label": "Dropout Criteria",
                "children": []
            },
            {
                "key": "3.6",
                "label": "Termination Criteria",
                "children": []
            }
        ]
    },
    {
        "key": "4",
        "label": "Clinical Procedures",
        "children": [
            {
                "key": "4.1",
                "label": "Drug Information",
                "children": []
            },
            {
                "key": "4.2",
                "label": "Receipt, Dispensing and Storage of Study Drug",
                "children": [
                    {
                        "key": "4.2.1",
                        "label": "Receipt of Study Drug",
                        "children": []
                    },
                    {
                        "key": "4.2.2",
                        "label": "Drug Inventory",
                        "children": []
                    },
                    {
                        "key": "4.2.3",
                        "label": "Drawing of Study Drug",
                        "children": []
                    },
                    {
                        "key": "4.2.4",
                        "label": "Dispensing Method",
                        "children": []
                    },
                    {
                        "key": "4.2.5",
                        "label": "Labeling of Study Drug",
                        "children": []
                    }
                ]
            },
            {
                "key": "4.3",
                "label": "Dosage of the Drug",
                "children": []
            },
            {
                "key": "4.4",
                "label": "Drug Administration",
                "children": []
            },
            {
                "key": "4.5",
                "label": "Blinding method",
                "children": []
            },
            {
                "key": "4.6",
                "label": "Concomitant Medications",
                "children": []
            },
            {
                "key": "4.7",
                "label": "Medication Compliance",
                "children": []
            },
            {
                "key": "4.8",
                "label": "Retention Plan",
                "children": []
            },
            {
                "key": "4.9",
                "label": "Policy of drug Reconciliation and Return",
                "children": []
            }
        ]
    },
    {
        "key": "5",
        "label": "Sample Collection, Shipment and Storage",
        "children": [
            {
                "key": "5.1",
                "label": "Detail Description of Sample Processing",
                "children": []
            },
            {
                "key": "5.2",
                "label": "Policy Sample Number",
                "children": []
            },
            {
                "key": "5.3",
                "label": "Detail of Sample Shipment and Storage",
                "children": []
            }
        ]
    },
    {
        "key": "6",
        "label": "Overall of bioanalytical analysis",
        "children": [
            {
                "key": "6.1",
                "label": "Blood sample time point",
                "children": [
                    {
                        "key": "6.1.1",
                        "label": "Overall About",
                        "children": []
                    },
                    {
                        "key": "6.1.2",
                        "label": "Overall Information",
                        "children": []
                    }
                ]
            },
            {
                "key": "6.2",
                "label": "Detail of analysis method validation",
                "children": []
            },
            {
                "key": "6.3",
                "label": "Analytes to Measure",
                "children": []
            }
        ]
    },
    {
        "key": "7",
        "label": "Pharmacokinetics and Safety Evaluation Indicators",
        "children": [
            {
                "key": "7.1",
                "label": "Pharmacokinetics Analysis",
                "children": [
                    {
                        "key": "7.1.1",
                        "label": "Parameters for Evaluation",
                        "children": []
                    },
                    {
                        "key": "7.1.2",
                        "label": "Other Parameters",
                        "children": []
                    }
                ]
            },
            {
                "key": "7.2",
                "label": "Safet Evaluation Indicators",
                "children": [
                    {
                        "key": "7.2.1",
                        "label": "Laboratory Tests and Safe Varibles Analysis",
                        "children": []
                    },
                    {
                        "key": "7.2.2",
                        "label": "Detail of Vital Signs",
                        "children": []
                    },
                    {
                        "key": "7.2.3",
                        "label": "Detail of Physical Examinations",
                        "children": []
                    },
                    {
                        "key": "7.2.4",
                        "label": "Detail of ECG",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "8",
        "label": "Data management and Statistical Analysis",
        "children": [
            {
                "key": "8.1",
                "label": "Data management",
                "children": []
            },
            {
                "key": "8.2",
                "label": "Statistical Analysis",
                "children": [
                    {
                        "key": "8.2.1",
                        "label": "Analysis Sets",
                        "children": []
                    },
                    {
                        "key": "8.2.2",
                        "label": "Missing, Unused, Spurious Data",
                        "children": []
                    },
                    {
                        "key": "8.2.3",
                        "label": "Revison Procedures for Deviations",
                        "children": []
                    },
                    {
                        "key": "8.2.4",
                        "label": "Statistical Contents",
                        "children": [
                            {
                                "key": "8.2.4.1",
                                "label": "Detail for Pharmacokinetic Analysis",
                                "children": []
                            },
                            {
                                "key": "8.2.4.2",
                                "label": "Detail for Safety Analysis",
                                "children": []
                            }
                        ]
                    },
                    {
                        "key": "8.2.5",
                        "label": "Analysis Software & General Requirements",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "9",
        "label": "Quality Assurance",
        "children": [
            {
                "key": "9.1",
                "label": "Quality Control",
                "children": []
            },
            {
                "key": "9.2",
                "label": "Quality Assurance of Sample Test",
                "children": []
            },
            {
                "key": "9.3",
                "label": "Quality Assurance of the Data Transfer, Calculation, and Reporting Process",
                "children": []
            },
            {
                "key": "9.4",
                "label": "Monitoring, Audits, Inspection",
                "children": [
                    {
                        "key": "9.4.1",
                        "label": "Study Monitoring",
                        "children": []
                    },
                    {
                        "key": "9.4.2",
                        "label": "Audits and Inspection",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "10",
        "label": "Handling of Abnormalities During the Study",
        "children": [
            {
                "key": "10.1",
                "label": "Protocol Deviation",
                "children": []
            },
            {
                "key": "10.2",
                "label": "Adverse Events",
                "children": [
                    {
                        "key": "10.2.1",
                        "label": "Definition of Adverse Events",
                        "children": []
                    },
                    {
                        "key": "10.2.2",
                        "label": "Adverse Event Severity Grades",
                        "children": []
                    },
                    {
                        "key": "10.2.3",
                        "label": "Assessing Relationship to Study Drug",
                        "children": []
                    },
                    {
                        "key": "10.2.4",
                        "label": "Handling of Adverse Events",
                        "children": []
                    },
                    {
                        "key": "10.2.5",
                        "label": "Procedures for Collection Reporting and Recording Adverse Events",
                        "children": []
                    },
                    {
                        "key": "10.2.6",
                        "label": "Adverse Event Description",
                        "children": []
                    },
                    {
                        "key": "10.2.7",
                        "label": "Adverse Events follow-up",
                        "children": []
                    },
                    {
                        "key": "10.2.8",
                        "label": "Outcome of Adverse Event",
                        "children": []
                    }
                ]
            },
            {
                "key": "10.3",
                "label": "Serious Dverse Events",
                "children": [
                    {
                        "key": "10.3.1",
                        "label": "Definition of Seirous Adverse Event",
                        "children": []
                    },
                    {
                        "key": "10.3.2",
                        "label": "Serious Adverse Events Report",
                        "children": []
                    },
                    {
                        "key": "10.3.3",
                        "label": "Suspected Unexpected Serious Adverse Reaction Report",
                        "children": []
                    },
                    {
                        "key": "10.3.4",
                        "label": "Serious Adverse Events follow-up",
                        "children": []
                    },
                    {
                        "key": "10.3.5",
                        "label": "Pregnancy Events",
                        "children": []
                    }
                ]
            }
        ]
    },
    {
        "key": "11",
        "label": "Study Drug Table",
        "children": []
    },
    {
        "key": "12",
        "label": "Table of study procedures",
        "children": []
    },
    {
        "key": "13",
        "label": "Table of blood sampling and vital signs test",
        "children": []
    }
]


def add_source_key(value):
    new_data = []
    for item in value:
        p = get_property("some", item["key"])
        source = p.get("source") if p else None
        new_item = {"key": item["key"], "label": item["label"], "source": source}
        if "children" in item:
            new_item["children"] = add_source_key(item["children"])
        new_data.append(new_item)
    return new_data


if __name__ == "__main__":
    # Example usage
    j = add_source_key(data)
    import json
    with open("data.json", "w") as f:
        f.write(json.dumps(j))
    # from pprint import pprint
    # pprint(j)
