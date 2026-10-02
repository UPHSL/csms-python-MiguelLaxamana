from dataclasses import dataclass, field

from csms.models.resident import Resident


@dataclass
class ResidentUpdateResult:
    success: bool
    resident: Resident | None = None
    errors: list[str] = field(
        default_factory=list
    )
    not_found: bool = False

    @classmethod
    def successful(
        cls,
        resident: Resident,
    ) -> "ResidentUpdateResult":
        return cls(
            success=True,
            resident=resident,
            errors=[],
            not_found=False,
        )

    @classmethod
    def validation_failed(
        cls,
        errors: list[str],
    ) -> "ResidentUpdateResult":
        return cls(
            success=False,
            resident=None,
            errors=list(errors),
            not_found=False,
        )

    @classmethod
    def resident_not_found(
        cls,
    ) -> "ResidentUpdateResult":
        return cls(
            success=False,
            resident=None,
            errors=[],
            not_found=True,
        )