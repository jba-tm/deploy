from app.core.enums import TextChoices


class DatasetChoices(TextChoices):
    DRUG = "drug"
    CLINICAL_TRIALS = "clinical_trial"


class DrugFilterChoices(TextChoices):
    SYNONYMS = "has_synonym", "has synonym"
    USAGES = "used_for", "used for"
    SIDE_EFFECTS = "has_side_effect", "has side effect"
    KINGDOM = "kingdom", "Kingdom"
    SUB_CLASS = "subclass", "Subclass"
    SUPER_CLASS = "superclass", "Superclass"
    MARKETED_NAME = "marketed_name", "marketed name"
    MANUFACTURER = "manufacturer", "manufacturer"
    COUNTRY = "country", "country"
    TARGET_GENES = "targets_gene", "Targets gene"
    SPECIES = "effective_in_species", "Effective in species"


class ClinicTrialFilterChoices(TextChoices):
    ALLOCATION = "allocation", "allocation"
    FUNDED_BY = "funded_by", "funded by"
    INTERVENTION_MODEL = "intervention_model", "intervention model"
    NUMBER_OF_VOLUNTEERS = "number_of_volunteers", "number of volunteers"
    PRIMARY_PURPOSE = "primary_purpose", "primary purpose"
    AGES_OF_VOLUNTEERS = "ages_of_volunteers", "ages of volunteers"
    GENDER_OF_VOLUNTEERS = "gender_of_volunteers", "gender of volunteers"
    TRIAL_COMPLETION_DATE = "trial_completion_date", "trial completion date"
    TRIAL_START_DATE = "trial_start_date", "trial start date"
    TRIAL_STATUS = "trial_status", "trial status"
    MASKING = "masking", "masking"
    COLLABORATES = "collaborates_with", "collaborates with"
    CONDITIONS = "tested_condition", "tested condition"
