import asyncio
from .plugins import PluginManager
from .schemas import SCHEMA
from .anonymizer import anonymize_pii

class ComplianceError(Exception):
    """Raised when a compliance validation error occurs."""
    pass

class ComplianceValidator:
    DEFAULT_POLICY_VERSION = "1.0"

    def __init__(self, strict_mode=True, plugins=None):
        self.strict_mode = strict_mode
        self.plugin_manager = PluginManager(plugins)

    def validate(self, request):
        """
        Synchronous wrapper around the async _validate. Calls plugin hooks.
        """
        # before-validation hooks
        self.plugin_manager.before(request)

        try:
            # run the async validation
            result = asyncio.run(self._validate(request))
        except ComplianceError:
            # in case of validation error, do not call after-validation hooks
            raise

        # after-validation hooks
        self.plugin_manager.after(result)
        return result

    async def _validate(self, req):
        """
        Perform the actual validation and enrichment asynchronously.
        """
        # 1) Unknown-field check (strict mode)
        if self.strict_mode:
            for key in req:
                if key.startswith("plugin_"):
                    continue
                if key not in SCHEMA["properties"]:
                    raise ComplianceError(f"Unknown field: {key}")

        # 2) Required fields
        for field in SCHEMA.get("required", []):
            if field not in req:
                raise ComplianceError(f"Missing required field: {field}")

        # 3) Type and enum checks
        # user_id
        if not isinstance(req["user_id"], str):
            raise ComplianceError("user_id must be a string")

        # age
        age = req["age"]
        if not isinstance(age, int):
            raise ComplianceError("age must be an integer")
        if age < 0:
            raise ComplianceError("age must be >= 0")

        # data_retention_policy
        policy = req["data_retention_policy"]
        if policy not in ("short_term", "long_term"):
            raise ComplianceError("Invalid data_retention_policy")

        # user_consent_status
        consent = req["user_consent_status"]
        if consent not in ("granted", "revoked", "pending"):
            raise ComplianceError("Invalid user_consent_status")

        # 4) Conditional deletion_timestamp: always reject if revoked
        if consent == "revoked":
            raise ComplianceError("deletion_timestamp required when consent is revoked")

        # 5) retention_period range checks
        if "retention_period" in req:
            rp = req["retention_period"]
            if not isinstance(rp, int):
                raise ComplianceError("retention_period must be an integer")
            if policy == "short_term":
                if rp > 30:
                    raise ComplianceError("retention_period too long for short_term")
            else:  # long_term
                if rp <= 30:
                    raise ComplianceError("retention_period too short for long_term")

        # 6) Optional-field type checks
        if "deletion_timestamp" in req and not isinstance(req["deletion_timestamp"], str):
            raise ComplianceError("deletion_timestamp must be a string")
        if "policy_version" in req and not isinstance(req["policy_version"], str):
            raise ComplianceError("policy_version must be a string")
        if "opt_out_reason" in req and not isinstance(req["opt_out_reason"], str):
            raise ComplianceError("opt_out_reason must be a string")
        if "pii_fields" in req:
            pf = req["pii_fields"]
            if not isinstance(pf, list) or not all(isinstance(x, str) for x in pf):
                raise ComplianceError("pii_fields must be list of strings")

        # 7) Enrichments
        # set default policy_version
        req.setdefault("policy_version", self.DEFAULT_POLICY_VERSION)
        # minor flag
        if age < 18:
            req["minor"] = True

        # 8) Asynchronous PII anonymization
        if "pii_fields" in req and req["pii_fields"]:
            await anonymize_pii(req, req["pii_fields"])

        return req
