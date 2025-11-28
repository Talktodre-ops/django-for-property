"""Forms for listings app."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from listings.models import (
    IDType,
    Listing,
    ListingDocument,
    ListingPhoto,
    OwnerProfile,
    PreferredContact,
)

User = get_user_model()


class SignupForm(UserCreationForm):
    """Extended signup form with email."""

    email = forms.EmailField(required=True)

    class Meta:
        """Meta options for SignupForm."""

        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        """Save user with email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class OwnerProfileForm(forms.ModelForm):
    """Form for owner profile updates."""

    class Meta:
        """Meta options for OwnerProfileForm."""

        model = OwnerProfile
        fields = [
            "phone_number",
            "whatsapp_number",
            "preferred_contact",
            "id_type",
            "id_number",
            "id_document",
            "id_expiry_date",
        ]
        widgets = {
            "preferred_contact": forms.RadioSelect(choices=PreferredContact.choices),
            "id_type": forms.Select(choices=[("", "---------")] + list(IDType.choices)),
            "id_expiry_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "placeholder": "YYYY-MM-DD"
                },
                format='%Y-%m-%d'
            ),
        }

    def clean(self):
        """Validate the entire form and check for ID document consistency."""
        cleaned_data = super().clean()
        id_type = cleaned_data.get("id_type")
        id_number = cleaned_data.get("id_number")
        id_document = cleaned_data.get("id_document")

        # If user has entered ID info but no document uploaded, add an error
        if (id_type or id_number) and not id_document and not self.instance.id_document:
            self.add_error(
                'id_document',
                'You must upload your ID document file. Click "Choose File" to select your ID (PDF, JPG, or PNG).'
            )

        return cleaned_data

    def clean_id_document(self):
        """Validate ID document file."""
        id_document = self.cleaned_data.get("id_document")

        # If no new file uploaded, keep existing file
        if not id_document:
            if self.instance and self.instance.id_document:
                return self.instance.id_document
            # No file and no existing file - validation will happen in clean()
            return None

        # Validate the new file
        if id_document:
            # Check file name exists
            if not id_document.name:
                raise forms.ValidationError("Please select a file to upload.")

            # Validate file size (max 5MB)
            if id_document.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    f"File size ({id_document.size / (1024*1024):.2f}MB) exceeds maximum of 5MB. Please compress or use a smaller file."
                )

            # Validate file type (case-insensitive)
            file_name_lower = id_document.name.lower()
            valid_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
            if not any(file_name_lower.endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    f"File format not supported. Accepted formats: JPG, PNG, PDF. Your file: {id_document.name}"
                )

        return id_document


class ListingForm(forms.ModelForm):
    """Form for creating/editing listings."""

    class Meta:
        """Meta options for ListingForm."""

        model = Listing
        fields = [
            "title",
            "description",
            "property_type",
            "listing_type",
            "address_line",
            "city",
            "state",
            "country",
            "postal_code",
            "latitude",
            "longitude",
            "bedrooms",
            "bathrooms",
            "parking_spaces",
            "land_size_sqm",
            "building_size_sqm",
            "price",
            "currency",
            "service_charge",
            "is_negotiable",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_price(self):
        """Validate price is positive."""
        price = self.cleaned_data.get("price")
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        return price


class ListingPhotoForm(forms.ModelForm):
    """Form for uploading listing photos."""

    class Meta:
        """Meta options for ListingPhotoForm."""

        model = ListingPhoto
        fields = ["image", "caption", "is_primary"]

    def clean_image(self):
        """Validate image file."""
        image = self.cleaned_data.get("image")
        if image:
            # Validate file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Image size must be less than 10MB")
            # Validate file type
            valid_extensions = [".jpg", ".jpeg", ".png"]
            if not any(image.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError("File must be an image (JPG, PNG)")
        return image


class ListingDocumentForm(forms.ModelForm):
    """Form for uploading listing documents."""

    class Meta:
        """Meta options for ListingDocumentForm."""

        model = ListingDocument
        fields = ["doc_type", "file"]

    def clean_file(self):
        """Validate document file."""
        file = self.cleaned_data.get("file")
        if file:
            # Validate file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB")
            # Validate file type
            valid_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    "File must be an image (JPG, PNG) or PDF"
                )
        return file

