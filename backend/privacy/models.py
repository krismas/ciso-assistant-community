from django.db import models
from iam.models import User, FolderMixin
from tprm.models import Entity
from core.models import AppliedControl
from core.models import FilteringLabelMixin, I18nObjectMixin, ReferentialObjectMixin
from core.base_models import NameDescriptionMixin, AbstractBaseModel
from core.constants import COUNTRY_CHOICES
from django.db.models import Count
from django.utils.translation import gettext_lazy as _


class NameDescriptionFolderMixin(NameDescriptionMixin, FolderMixin):
    class Meta:
        abstract = True


LEGAL_BASIS_CHOICES = (
    # Article 6(1) Legal Bases
    ("consent", _("Consent")),
    ("contract", _("Performance of a Contract")),
    ("legal_obligation", _("Compliance with a Legal Obligation")),
    ("vital_interests", _("Protection of Vital Interests")),
    ("public_interest", _("Performance of a Task in the Public Interest")),
    ("legitimate_interests", _("Legitimate Interests")),
    # Special Category Processing - Article 9(2)
    ("explicit_consent", _("Explicit Consent for Special Categories")),
    ("employment_social_security", _("Employment and Social Security Law")),
    (
        "vital_interests_incapacity",
        _("Vital Interests (Subject Physically/Legally Incapable)"),
    ),
    ("nonprofit_organization", _("Processing by Nonprofit Organization")),
    ("public_data", _("Data Manifestly Made Public by the Data Subject")),
    ("legal_claims", _("Establishment, Exercise or Defense of Legal Claims")),
    ("substantial_public_interest", _("Substantial Public Interest")),
    ("preventive_medicine", _("Preventive or Occupational Medicine")),
    ("public_health", _("Public Health")),
    ("archiving_research", _("Archiving, Research or Statistical Purposes")),
    # Additional GDPR Bases
    ("child_consent", _("Child's Consent with Parental Authorization")),
    ("data_transfer_adequacy", _("Transfer Based on Adequacy Decision")),
    ("data_transfer_safeguards", _("Transfer Subject to Appropriate Safeguards")),
    ("data_transfer_binding_rules", _("Transfer Subject to Binding Corporate Rules")),
    (
        "data_transfer_derogation",
        _("Transfer Based on Derogation for Specific Situations"),
    ),
    # Common Combined Bases
    ("consent_and_contract", _("Consent and Contract")),
    ("contract_and_legitimate_interests", _("Contract and Legitimate Interests")),
    # Other
    ("not_applicable", _("Not Applicable")),
    ("other", _("Other Legal Basis (Specify in Description)")),
)


class ProcessingNature(ReferentialObjectMixin, I18nObjectMixin):
    DEFAULT_PROCESSING_NATURE = [
        "collection",
        "recording",
        "organization",
        "structuring",
        "storage",
        "adaptationOrAlteration",
        "retrieval",
        "consultation",
        "use",
        "disclosureByTransmission",
        "disseminationOrOtherwiseMakingAvailable",
        "alignmentOrCombination",
        "restriction",
        "erasureOrDestruction",
    ]

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_default_values(cls):
        for value in cls.DEFAULT_PROCESSING_NATURE:
            ProcessingNature.objects.update_or_create(
                name=value,
            )

    class Meta:
        ordering = ["name"]
        verbose_name = "Processing Nature"
        verbose_name_plural = "Processing Natures"


class Processing(NameDescriptionFolderMixin, FilteringLabelMixin):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("in_review", "In Review"),
        ("approved", "Approved"),
        ("deprecated", "Deprecated"),
    )

    ref_id = models.CharField(max_length=100, blank=True)
    nature = models.ManyToManyField(ProcessingNature, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="authored_processings"
    )
    legal_basis = models.CharField(
        max_length=255, choices=LEGAL_BASIS_CHOICES, blank=True
    )
    information_channel = models.CharField(max_length=255, blank=True)
    usage_channel = models.CharField(max_length=255, blank=True)
    dpia_required = models.BooleanField(default=False, blank=True)
    dpia_reference = models.CharField(max_length=255, blank=True)
    has_sensitive_personal_data = models.BooleanField(default=False)
    owner = models.ForeignKey(
        Entity, on_delete=models.SET_NULL, null=True, related_name="owned_processings"
    )
    associated_controls = models.ManyToManyField(
        AppliedControl, blank=True, related_name="processings"
    )

    def update_sensitive_data_flag(self):
        """Update the has_sensitive_personal_data flag based on associated personal data"""
        has_sensitive = self.personal_data.filter(is_sensitive=True).exists()

        if has_sensitive != self.has_sensitive_personal_data:
            self.has_sensitive_personal_data = has_sensitive
            self.save(update_fields=["has_sensitive_personal_data"])

    def metrics(self):
        return {}


class Purpose(NameDescriptionFolderMixin):
    processing = models.ForeignKey(
        Processing, on_delete=models.CASCADE, related_name="purposes"
    )

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)


class PersonalData(NameDescriptionFolderMixin):
    DELETION_POLICY_CHOICES = (
        ("automatic_deletion", _("Automatic Deletion")),
        ("anonymization", _("Anonymization")),
        ("manual_review_deletion", _("Manual Review Deletion")),
        ("user_requested_deletion", _("User Requested Deletion")),
        ("legal_regulatory_hold", _("Legal/Regulatory Hold")),
        ("partial_deletion", _("Partial Deletion")),
    )
    PERSONAL_DATA_CHOICES = (
        # Basic Identity Information
        ("basic_identity", _("Basic Identity Information")),
        ("name", _("Name")),
        ("identification_numbers", _("Identification Numbers")),
        ("online_identifiers", _("Online Identifiers")),
        ("location_data", _("Location Data")),
        # Contact Information
        ("contact_details", _("Contact Details")),
        ("address", _("Address")),
        ("email", _("Email Address")),
        ("phone_number", _("Phone Number")),
        # Financial Information
        ("financial_data", _("Financial Data")),
        ("bank_account", _("Bank Account Information")),
        ("payment_card", _("Payment Card Information")),
        ("transaction_history", _("Transaction History")),
        ("salary_information", _("Salary Information")),
        # Special Categories of Personal Data (Sensitive)
        ("health_data", _("Health Data")),
        ("genetic_data", _("Genetic Data")),
        ("biometric_data", _("Biometric Data")),
        ("racial_ethnic_origin", _("Racial or Ethnic Origin")),
        ("political_opinions", _("Political Opinions")),
        ("religious_beliefs", _("Religious or Philosophical Beliefs")),
        ("trade_union_membership", _("Trade Union Membership")),
        ("sexual_orientation", _("Sexual Orientation")),
        ("sex_life_data", _("Sex Life Data")),
        # Digital Behavior and Activities
        ("browsing_history", _("Browsing History")),
        ("search_history", _("Search History")),
        ("cookies", _("Cookies Data")),
        ("device_information", _("Device Information")),
        ("ip_address", _("IP Address")),
        ("user_behavior", _("User Behavior")),
        # Professional Data
        ("employment_details", _("Employment Details")),
        ("education_history", _("Education History")),
        ("professional_qualifications", _("Professional Qualifications")),
        ("work_performance", _("Work Performance Data")),
        # Social Relationships
        ("family_details", _("Family Details")),
        ("social_network", _("Social Network")),
        ("lifestyle_information", _("Lifestyle Information")),
        # Communication Data
        ("correspondence", _("Correspondence Content")),
        ("messaging_content", _("Messaging Content")),
        ("communication_metadata", _("Communication Metadata")),
        # Government/Official Data
        ("government_identifiers", _("Government Identifiers")),
        ("tax_information", _("Tax Information")),
        ("social_security", _("Social Security Information")),
        ("drivers_license", _("Driver's License Information")),
        ("passport_information", _("Passport Information")),
        # Legal Data
        ("legal_records", _("Legal Records")),
        ("criminal_records", _("Criminal Records")),
        ("judicial_data", _("Judicial Data")),
        # Preferences and Opinions
        ("preferences", _("Preferences")),
        ("opinions", _("Opinions")),
        ("feedback", _("Feedback")),
        # Other Types
        ("images_photos", _("Images and Photos")),
        ("voice_recordings", _("Voice Recordings")),
        ("video_recordings", _("Video Recordings")),
        ("other", _("Other Personal Data")),
    )

    processing = models.ForeignKey(
        Processing, on_delete=models.CASCADE, related_name="personal_data"
    )
    category = models.CharField(max_length=255, choices=PERSONAL_DATA_CHOICES)
    retention = models.CharField(max_length=255, blank=True)
    deletion_policy = models.CharField(
        max_length=50, choices=DELETION_POLICY_CHOICES, blank=True
    )
    is_sensitive = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)

        # Update the processing's sensitive data flag if needed
        if self.is_sensitive and not self.processing.has_sensitive_personal_data:
            self.processing.has_sensitive_personal_data = True
            self.processing.save(update_fields=["has_sensitive_personal_data"])

    @classmethod
    def get_categories_count(cls):
        categories = (
            cls.objects.values("category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Convert to list of dictionaries with readable category names
        result = []
        for item in categories:
            category_code = item["category"]
            category_name = dict(cls.PERSONAL_DATA_CHOICES).get(
                category_code, category_code
            )
            result.append(
                {"id": category_code, "name": category_name, "value": item["count"]}
            )

        return result


class DataSubject(NameDescriptionFolderMixin):
    CATEGORY_CHOICES = (
        # Core Categories
        ("customer", _("Customer/Client")),
        ("prospect", _("Prospective Customer/Client")),
        ("employee", _("Employee")),
        ("job_applicant", _("Job Applicant")),
        ("contractor", _("Contractor/Vendor")),
        ("business_partner", _("Business Partner")),
        # Website/Service Users
        ("user", _("Website/App User")),
        ("visitor", _("Visitor")),
        # Special Categories
        ("minor", _("Child/Minor")),
        ("vulnerable", _("Vulnerable Person")),
        # Others
        ("public", _("General Public")),
        ("other", _("Other Data Subject Category")),
    )

    processing = models.ForeignKey(
        "Processing", on_delete=models.CASCADE, related_name="data_subjects"
    )
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)


class DataRecipient(NameDescriptionFolderMixin):
    CATEGORY_CHOICES = (
        # Internal Recipients
        ("internal_team", _("Internal Team/Department")),
        ("employee", _("Employee")),
        ("subsidiary", _("Subsidiary Company")),
        ("parent_company", _("Parent Company")),
        ("affiliated_entity", _("Affiliated Entity")),
        # External Service Providers
        ("service_provider", _("Service Provider")),
        ("data_processor", _("Data Processor")),
        ("cloud_provider", _("Cloud Service Provider")),
        ("it_provider", _("IT Service Provider")),
        ("marketing_agency", _("Marketing Agency")),
        ("payment_processor", _("Payment Processor")),
        ("analytics_provider", _("Analytics Provider")),
        # Business Partners
        ("business_partner", _("Business Partner")),
        ("distributor", _("Distributor")),
        ("reseller", _("Reseller")),
        ("supplier", _("Supplier")),
        ("contractor", _("Contractor")),
        # Professional Services
        ("legal_advisor", _("Legal Advisor")),
        ("accountant", _("Accountant")),
        ("consultant", _("Consultant")),
        ("auditor", _("Auditor")),
        # Authorities
        ("regulatory_authority", _("Regulatory Authority")),
        ("tax_authority", _("Tax Authority")),
        ("law_enforcement", _("Law Enforcement")),
        ("government_entity", _("Government Entity")),
        ("court", _("Court")),
        # Others
        ("joint_controller", _("Joint Controller")),
        ("individual_recipient", _("Individual Recipient")),
        ("public", _("Public Disclosure")),
        ("other", _("Other Recipient Category")),
    )

    processing = models.ForeignKey(
        Processing, on_delete=models.CASCADE, related_name="data_recipients"
    )
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)


class DataContractor(NameDescriptionFolderMixin):
    RELATIONSHIP_TYPE_CHOICES = (
        ("data_processor", _("Data Processor")),
        ("sub_processor", _("Sub-processor")),
        ("joint_controller", _("Joint Controller")),
        ("independent_controller", _("Independent Controller")),
        ("other", _("Other Relationship Type")),
    )
    processing = models.ForeignKey(
        Processing, on_delete=models.CASCADE, related_name="contractors_involved"
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    relationship_type = models.CharField(
        max_length=255, choices=RELATIONSHIP_TYPE_CHOICES
    )
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)
    documentation_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)


class DataTransfer(NameDescriptionFolderMixin):
    processing = models.ForeignKey(
        Processing, on_delete=models.CASCADE, related_name="data_transfers"
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    country = models.CharField(max_length=3, choices=COUNTRY_CHOICES)
    legal_basis = models.CharField(
        max_length=255, choices=LEGAL_BASIS_CHOICES, blank=True
    )
    guarantees = models.TextField(blank=True)
    documentation_link = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        self.folder = self.processing.folder
        super().save(*args, **kwargs)
