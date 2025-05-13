# The Task

I am a Frontend Developer building a dynamic user registration form. I want to enforce complex input rules on the client side, provide real-time feedback, and let designers tweak behavior with minimal code changes. This code repository underpins our form validation library with declarative schemas.

# The Requirements

* `EnumConstraints` : Ensure gender, plan_type, and newsletter_opt_in only take allowed selections.
* `ConditionalValidation` : Validate company_name only when user_type is “business.”
* `DefaultValues` : Set default country to “US” and default language to browser locale when fields are empty.
* `RangeChecks` : Enforce password length and age field between 13 and 120.
* `AsyncValidation` : Check username uniqueness via asynchronous API before enabling Submit.
* `SingleItemValidation` : Validate each form submission separately, returning granular field-level messages.
* `OptionalFields` : Allow profile_picture upload and bio as optional fields with custom tooltips.
* `StrictMode` : Switch between lenient (ignore unknown inputs) and strict (reject unknown keys) in QA vs. production.
* `PluginSystem` : Install third-party plugins for credit card validation, address autocomplete, and reCAPTCHA.
* `SchemaImportExport` : Export form schema to YAML for design review and import updates without code changes.
