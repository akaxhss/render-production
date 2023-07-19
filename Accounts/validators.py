from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

yes_or_no_regex = RegexValidator(regex="^(?i:yes|yess|yyess|no|noo|nnoo)$", message="Enter either yes/no")
phone_regex = RegexValidator(regex="(0|91)?[7-9][0-9]{9}", message="Phone number must be entered in the format: '+999999999'.")


def yes_or_no_Validation(value):
    valid = False
    # if value.lower() not in ['yes'] and value.lower() not in ['no']:
    valid_inputs = ['yes', 'yess', 'no', 'noo']
    # if value.lower() != 'yes' and value.lower() != 'no':
    for valid_input in valid_inputs:
        if value.lower() == valid_input:
            valid = True;p
            break;
    if not valid:
        raise ValidationError("Enter either a yes or no")


def CheckIfAlpha(value):
    if value.replace(" ", "").isalpha() != True:
        raise ValidationError("Entered value should be Alphabets and not any other characters")



def CheckNull(value):
    if value == '':
        raise ValidationError("Field is required")
        
